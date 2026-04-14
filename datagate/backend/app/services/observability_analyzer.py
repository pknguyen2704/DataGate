from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.observability import DQTableSnapshot, DQTableVolumeTS, DQTableSchema, DQIncident
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ObservabilityAnalyzer:
    @staticmethod
    def analyze_table(db: Session, table_name: str):
        """Perform standard observability analysis on a table"""
        logger.info(f"🧐 Running observability analysis for {table_name}")
        
        # 1. Schema Drift
        ObservabilityAnalyzer._check_schema_drift(db, table_name)
        
        # 2. Freshness & Volume (Standard Metrics)
        ObservabilityAnalyzer._check_metrics_anomaly(db, table_name)

    @staticmethod
    def _check_schema_drift(db: Session, table_name: str):
        # Get latest two distinct snapshot times
        snapshot_times = db.query(DQTableSchema.snapshot_time)\
            .filter(DQTableSchema.table_name == table_name)\
            .distinct()\
            .order_by(desc(DQTableSchema.snapshot_time))\
            .limit(2)\
            .all()
        
        if len(snapshot_times) < 2:
            return # Not enough history

        latest_time = snapshot_times[0][0]
        previous_time = snapshot_times[1][0]

        latest_schema = db.query(DQTableSchema)\
            .filter(DQTableSchema.table_name == table_name, DQTableSchema.snapshot_time == latest_time).all()
        prev_schema = db.query(DQTableSchema)\
            .filter(DQTableSchema.table_name == table_name, DQTableSchema.snapshot_time == previous_time).all()

        latest_map = {c.column_name: c.data_type for c in latest_schema}
        prev_map = {c.column_name: c.data_type for c in prev_schema}

        # Check for missing columns
        for col in prev_map:
            if col not in latest_map:
                ObservabilityAnalyzer._create_incident(db, table_name, "drift", "high", f"Column '{col}' was removed from the schema.")
            elif prev_map[col] != latest_map[col]:
                ObservabilityAnalyzer._create_incident(db, table_name, "drift", "medium", f"Column '{col}' type changed from {prev_map[col]} to {latest_map[col]}.")

        # Check for new columns
        for col in latest_map:
            if col not in prev_map:
                ObservabilityAnalyzer._create_incident(db, table_name, "drift", "low", f"New column '{col}' ({latest_map[col]}) added.")

    @staticmethod
    def _check_metrics_anomaly(db: Session, table_name: str):
        # Freshness Check
        snapshots = db.query(DQTableSnapshot)\
            .filter(DQTableSnapshot.table_name == table_name)\
            .order_by(desc(DQTableSnapshot.snapshot_time))\
            .limit(10)\
            .all()
        
        if len(snapshots) >= 3:
            latest = snapshots[0]
            # Calculate time diff between updates in hours
            diffs = []
            for i in range(len(snapshots)-1):
                if snapshots[i].last_updated_time and snapshots[i+1].last_updated_time:
                    delta = (snapshots[i].last_updated_time - snapshots[i+1].last_updated_time).total_seconds() / 3600
                    if delta > 0: diffs.append(delta)
            
            if diffs:
                avg_diff = np.mean(diffs)
                std_diff = np.std(diffs)
                current_lag = (datetime.now() - latest.last_updated_time).total_seconds() / 3600 if latest.last_updated_time else 0
                
                # If current lag > Mean + 3*Std
                if current_lag > (avg_diff + 3 * std_diff) and current_lag > 24: # Avoid noise for ultra-fresh tables
                     ObservabilityAnalyzer._create_incident(db, table_name, "freshness", "medium", 
                        f"Data delay detected. Current lag {current_lag:.1f}h exceeds expected {avg_diff:.1f}h limit.")

        # Volume Check
        history = db.query(DQTableVolumeTS)\
            .filter(DQTableVolumeTS.table_name == table_name)\
            .order_by(DQTableVolumeTS.dt.desc())\
            .limit(20)\
            .all()
        
        if len(history) >= 7:
            counts = [h.records_added for h in history if h.records_added > 0]
            if len(counts) > 3:
                latest_count = counts[0]
                hist_counts = counts[1:]
                avg_count = np.mean(hist_counts)
                std_count = np.std(hist_counts)
                
                # Simple Z-score anomaly detection
                if std_count > 0:
                    z_score = (latest_count - avg_count) / std_count
                    if abs(z_score) > 3:
                        severity = "high" if z_score < -3 else "medium" # Dropping data is worse
                        msg = f"Volume anomaly: {latest_count} records added (Expected ~{avg_count:.0f}). Z-Score: {z_score:.2f}"
                        ObservabilityAnalyzer._create_incident(db, table_name, "volume", severity, msg)

    @staticmethod
    def _create_incident(db: Session, table_name: str, inc_type: str, severity: str, message: str):
        # Check if similar active incident exists in last 24h
        exists = db.query(DQIncident).filter(
            DQIncident.table_name == table_name,
            DQIncident.incident_type == inc_type,
            DQIncident.status == "open",
            DQIncident.message == message
        ).first()

        if not exists:
            logger.warning(f"🚨 ALERT [{inc_type.upper()}]: {message} on {table_name}")
            incident = DQIncident(
                table_name=table_name,
                incident_type=inc_type,
                severity=severity,
                message=message,
                detected_at=datetime.now()
            )
            db.add(incident)
            db.commit()
