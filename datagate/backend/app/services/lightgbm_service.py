from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LightGBMAUC, LightGBMParameter, SHAPResult


class LightGBMService:
    def __init__(self, db: Session):
        self.db = db

    def list_parameters(self, table_id: str | None = None) -> list[LightGBMParameter]:
        query = self.db.query(LightGBMParameter)
        if table_id:
            query = query.filter(LightGBMParameter.table_id == table_id)
        return query.order_by(LightGBMParameter.updated_at.desc()).all()

    def get_parameter_or_404(self, parameter_id: str) -> LightGBMParameter:
        row = self.db.query(LightGBMParameter).filter(LightGBMParameter.id == parameter_id).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LightGBM parameter not found")
        return row

    def create_parameter(self, data, user_id: str) -> LightGBMParameter:
        row = LightGBMParameter(**data.model_dump(), created_by=user_id, last_modified_by=user_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update_parameter(self, parameter_id: str, data, user_id: str) -> LightGBMParameter:
        row = self.get_parameter_or_404(parameter_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        row.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_parameter(self, parameter_id: str) -> None:
        row = self.get_parameter_or_404(parameter_id)
        self.db.delete(row)
        self.db.commit()

    def validate_json(self, data: dict) -> dict:
        return {"valid": bool(data), "message": "JSON payload is valid" if data else "JSON payload is empty"}

    def import_json(self, data: dict, user_id: str) -> LightGBMParameter:
        return self.create_parameter(data, user_id)

    def list_auc_results(self, table_id: str | None = None) -> list[LightGBMAUC]:
        query = self.db.query(LightGBMAUC)
        if table_id:
            query = query.filter(LightGBMAUC.table_id == table_id)
        return query.order_by(LightGBMAUC.processing_date_hour.desc()).all()

    def get_auc_result_or_404(self, auc_result_id: str) -> LightGBMAUC:
        row = self.db.query(LightGBMAUC).filter(LightGBMAUC.id == auc_result_id).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AUC result not found")
        return row

    def list_shap_results(self, auc_result_id: str) -> list[SHAPResult]:
        self.get_auc_result_or_404(auc_result_id)
        return self.db.query(SHAPResult).filter(SHAPResult.lightgbm_result_id == auc_result_id).order_by(SHAPResult.shap_rank.asc()).all()
