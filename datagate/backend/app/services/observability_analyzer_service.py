from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.observability_model import (
    DGObservabilitySnapshot, DGObservabilityVolumeTS, DGObservabilitySchema, 
    DGObservabilityIncident, DGObservabilityMetric, DGObservabilityMetricThreshold
)
from datetime import datetime, timedelta
import logging
import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)

def run_metric_prediction(db: Session, table_name: str, column_name: str, metric_name: str):
    """
    Sử dụng Prophet để phân tích lịch sử của một metric và dự báo dải kỳ vọng.
    """
    history = db.query(DGObservabilityMetric).filter(
        DGObservabilityMetric.table_name == table_name,
        DGObservabilityMetric.column_name == column_name,
        DGObservabilityMetric.metric_name == metric_name
    ).order_by(DGObservabilityMetric.snapshot_time.asc()).all()

    if len(history) < 5:
        return {"status": "insufficient_data"}

    df = pd.DataFrame([{"ds": h.snapshot_time, "y": h.metric_value} for h in history])
    
    model = Prophet(interval_width=0.95, yearly_seasonality=False)
    model.fit(df)
    
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    
    last_forecast = forecast.iloc[-1]
    
    return {
        "status": "success",
        "current_value": history[-1].metric_value,
        "expected_range": [last_forecast['yhat_lower'], last_forecast['yhat_upper']],
        "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(48).to_dict('records')
    }


class ObservabilityAnalyzer:
    """
    Bộ phân tích dữ liệu giám sát (Analyzer).
    Nhiệm vụ: So sánh dữ liệu cũ và mới để phát hiện bất thường.
    Sử dụng Prophet cho cả Freshness và Volume anomaly detection.
    """

    @staticmethod
    def analyze_table(db: Session, table_name: str):
        """Hàm chính để bắt đầu phân tích một bảng"""
        logger.info(f"🧐 Đang phân tích dữ liệu cho bảng: {table_name}")

        # 1. Kiểm tra thay đổi cấu trúc (Schema Drift)
        ObservabilityAnalyzer._check_schema_drift(db, table_name)

        # 2. Kiểm tra bất thường về khối lượng (Volume Anomaly) dùng Prophet
        ObservabilityAnalyzer._check_volume_with_prophet(db, table_name)

        # 3. Kiểm tra bất thường về độ trễ (Freshness Anomaly) dùng Prophet
        ObservabilityAnalyzer._check_freshness_with_prophet(db, table_name)

    # ===================================================================
    # SCHEMA DRIFT DETECTION
    # ===================================================================

    @staticmethod
    def _check_schema_drift(db: Session, table_name: str):
        """So sánh Schema hiện tại với lần quét trước đó"""
        # Lấy 2 mốc thời gian quét gần nhất
        times = db.query(DGObservabilitySchema.snapshot_time)\
            .filter(DGObservabilitySchema.table_name == table_name)\
            .distinct().order_by(desc(DGObservabilitySchema.snapshot_time)).limit(2).all()

        if len(times) < 2:
            return  # Chưa có đủ lịch sử để so sánh

        latest_schema = db.query(DGObservabilitySchema).filter(
            DGObservabilitySchema.table_name == table_name,
            DGObservabilitySchema.snapshot_time == times[0][0]
        ).all()
        prev_schema = db.query(DGObservabilitySchema).filter(
            DGObservabilitySchema.table_name == table_name,
            DGObservabilitySchema.snapshot_time == times[1][0]
        ).all()

        latest_cols = {c.column_name: c.data_type for c in latest_schema}
        prev_cols = {c.column_name: c.data_type for c in prev_schema}

        # Phát hiện cột bị xóa hoặc đổi kiểu dữ liệu
        for col_name, col_type in prev_cols.items():
            if col_name not in latest_cols:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "drift", "high",
                    f"Cột '{col_name}' đã bị xóa khỏi bảng."
                )
            elif col_type != latest_cols[col_name]:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "drift", "medium",
                    f"Cột '{col_name}' bị đổi kiểu: {col_type} -> {latest_cols[col_name]}"
                )

        # Phát hiện cột mới thêm vào
        for col_name in latest_cols:
            if col_name not in prev_cols:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "drift", "low",
                    f"Phát hiện cột mới: '{col_name}'"
                )

    # ===================================================================
    # VOLUME ANOMALY DETECTION (Prophet)
    # ===================================================================

    @staticmethod
    def _check_volume_with_prophet(db: Session, table_name: str):
        """Sử dụng thư viện Prophet để dự báo và phát hiện số lượng bản ghi bất thường"""
        try:
            history = db.query(DGObservabilityVolumeTS).filter(
                DGObservabilityVolumeTS.table_name == table_name
            ).order_by(DGObservabilityVolumeTS.dt.asc()).all()

            if len(history) < 7:
                return  # Cần tối thiểu 7 ngày dữ liệu

            df = pd.DataFrame([{"ds": h.dt, "y": h.records_added or 0} for h in history])

            model = Prophet(interval_width=0.95, daily_seasonality=False)
            model.fit(df)

            forecast = model.predict(model.make_future_dataframe(periods=0))

            actual = df.iloc[-1]['y']
            predict = forecast.iloc[-1]

            if actual < predict['yhat_lower']:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "volume", "high",
                    f"Dữ liệu nạp bị sụt giảm bất thường: {actual} records "
                    f"(Kỳ vọng tối thiểu {predict['yhat_lower']:.0f})"
                )
            elif actual > predict['yhat_upper']:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "volume", "medium",
                    f"Dữ liệu nạp tăng đột biến: {actual} records "
                    f"(Kỳ vọng tối đa {predict['yhat_upper']:.0f})"
                )

        except Exception as e:
            logger.error(f"Lỗi khi chạy Prophet Volume: {e}")

    # ===================================================================
    # FRESHNESS ANOMALY DETECTION (Prophet)
    # ===================================================================

    @staticmethod
    def _check_freshness_with_prophet(db: Session, table_name: str):
        """
        Sử dụng Prophet để phân tích lịch sử cập nhật và phát hiện bất thường.
        Phân tích inter-arrival time (khoảng cách giữa các lần cập nhật).
        Nếu thời gian chờ hiện tại vượt quá dải dự báo → tạo incident.
        """
        try:
            snapshots = db.query(DGObservabilitySnapshot).filter(
                DGObservabilitySnapshot.table_name == table_name,
                DGObservabilitySnapshot.last_updated_time.isnot(None)
            ).order_by(DGObservabilitySnapshot.last_updated_time.asc()).all()

            if len(snapshots) < 7:
                return  # Cần tối thiểu 7 data points

            # Tính inter-arrival time (khoảng cách giờ giữa các lần cập nhật)
            update_times = [s.last_updated_time for s in snapshots if s.last_updated_time]
            if len(update_times) < 7:
                return

            intervals = []
            for i in range(1, len(update_times)):
                delta = (update_times[i] - update_times[i - 1]).total_seconds() / 3600  # hours
                intervals.append({
                    "ds": update_times[i],
                    "y": max(delta, 0),  # đảm bảo không âm
                })

            if len(intervals) < 5:
                return

            df = pd.DataFrame(intervals)

            model = Prophet(
                interval_width=0.95,
                daily_seasonality=False,
                weekly_seasonality=True,
            )
            model.fit(df)

            # Dự đoán giới hạn tối đa cho khoảng chờ tiếp theo
            future = model.make_future_dataframe(periods=1, freq='h')
            forecast = model.predict(future)
            predicted_upper = forecast.iloc[-1]['yhat_upper']

            # Kiểm tra thời gian chờ hiện tại
            last_update = update_times[-1]
            hours_since = (datetime.now() - last_update).total_seconds() / 3600

            if hours_since > predicted_upper and predicted_upper > 0:
                ObservabilityAnalyzer._create_incident(
                    db, table_name, "freshness", "high",
                    f"Dữ liệu đến trễ: {hours_since:.1f} giờ kể từ lần cập nhật cuối "
                    f"(Giới hạn dự báo: {predicted_upper:.1f} giờ)"
                )

        except Exception as e:
            logger.error(f"Lỗi khi chạy Prophet Freshness: {e}")

    # ===================================================================
    # PREDICTION DATA (cho Frontend charts)
    # ===================================================================

    @staticmethod
    def get_volume_prediction(db: Session, table_name: str) -> dict:
        """Trả về dữ liệu lịch sử + dải dự báo volume cho frontend chart"""
        try:
            history = db.query(DGObservabilityVolumeTS).filter(
                DGObservabilityVolumeTS.table_name == table_name
            ).order_by(DGObservabilityVolumeTS.dt.asc()).all()

            history_data = [{"date": str(h.dt), "actual": h.records_added or 0} for h in history]

            if len(history) < 5:
                return {"history": history_data, "forecast": []}

            df = pd.DataFrame([{"ds": h.dt, "y": h.records_added or 0} for h in history])
            model = Prophet(interval_width=0.95, daily_seasonality=False)
            model.fit(df)

            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future)

            forecast_data = [
                {
                    "date": str(row['ds'].date()),
                    "predicted": round(row['yhat'], 0),
                    "lower": round(row['yhat_lower'], 0),
                    "upper": round(row['yhat_upper'], 0),
                }
                for _, row in forecast.iterrows()
            ]

            return {"history": history_data, "forecast": forecast_data}

        except Exception as e:
            logger.error(f"Volume prediction error: {e}")
            return {"history": [], "forecast": [], "error": str(e)}

    @staticmethod
    def get_freshness_prediction(db: Session, table_name: str) -> dict:
        """Trả về dữ liệu lịch sử freshness + dải dự báo cho frontend chart"""
        try:
            snapshots = db.query(DGObservabilitySnapshot).filter(
                DGObservabilitySnapshot.table_name == table_name,
                DGObservabilitySnapshot.last_updated_time.isnot(None)
            ).order_by(DGObservabilitySnapshot.snapshot_time.asc()).all()

            history_data = [
                {
                    "date": str(s.snapshot_time),
                    "last_updated": str(s.last_updated_time) if s.last_updated_time else None,
                    "total_records": s.total_records,
                    "total_size": s.total_size,
                }
                for s in snapshots
            ]

            # Tính inter-arrival times
            update_times = [s.last_updated_time for s in snapshots if s.last_updated_time]
            if len(update_times) < 5:
                return {"history": history_data, "forecast": [], "current_delay_hours": None}

            intervals = []
            for i in range(1, len(update_times)):
                delta = (update_times[i] - update_times[i - 1]).total_seconds() / 3600
                intervals.append({"ds": update_times[i], "y": max(delta, 0)})

            df = pd.DataFrame(intervals)
            model = Prophet(interval_width=0.95, daily_seasonality=False, weekly_seasonality=True)
            model.fit(df)

            future = model.make_future_dataframe(periods=3, freq='h')
            forecast = model.predict(future)

            forecast_data = [
                {
                    "date": str(row['ds']),
                    "predicted_interval": round(row['yhat'], 2),
                    "lower": round(row['yhat_lower'], 2),
                    "upper": round(row['yhat_upper'], 2),
                }
                for _, row in forecast.iterrows()
            ]

            hours_since = (datetime.now() - update_times[-1]).total_seconds() / 3600

            return {
                "history": history_data,
                "forecast": forecast_data,
                "current_delay_hours": round(hours_since, 2),
                "predicted_max_delay": round(forecast.iloc[-1]['yhat_upper'], 2),
                "status": "late" if hours_since > forecast.iloc[-1]['yhat_upper'] else "on_time",
            }

        except Exception as e:
            logger.error(f"Freshness prediction error: {e}")
            return {"history": history_data if 'history_data' in dir() else [], "forecast": [], "error": str(e)}

    # ===================================================================
    # INCIDENT MANAGEMENT
    # ===================================================================

    @staticmethod
    def _create_incident(db: Session, table_name: str, inc_type: str, severity: str, message: str):
        """Tạo một cảnh báo mới vào database, tránh trùng lặp"""
        exists = db.query(DGObservabilityIncident).filter(
            DGObservabilityIncident.table_name == table_name,
            DGObservabilityIncident.message == message,
            DGObservabilityIncident.status == "open"
        ).first()

        if not exists:
            incident = DGObservabilityIncident(
                table_name=table_name,
                incident_type=inc_type,
                severity=severity,
                message=message,
                detected_at=datetime.now()
            )
            db.add(incident)
            db.commit()
