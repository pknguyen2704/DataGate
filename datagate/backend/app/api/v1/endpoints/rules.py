from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.api import deps
from app.models.rule import ActiveRule
from app.schemas.rule import (
    ActiveRuleCreate,
    ActiveRuleUpdate,
    ActiveRule as ActiveRuleSchema,
    RuleSuggestionBatch,
)
from typing import List
from app import models
from app.api.v1.endpoints.services import get_accessible_asset_service_or_403
from app.services.observability_scheduler import trigger_airflow_dag

router = APIRouter()

@router.get("/", response_model=List[ActiveRuleSchema])
def get_rules(
    table: str = None, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(ActiveRule)
    if table:
        get_accessible_asset_service_or_403(db, current_user, table)
        query = query.filter(ActiveRule.table_name == table)
    return query.order_by(ActiveRule.is_applied.desc(), ActiveRule.priority.asc(), ActiveRule.frequency.desc()).all()

@router.post("/", response_model=ActiveRuleSchema)
def create_rule(
    rule: ActiveRuleCreate, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    get_accessible_asset_service_or_403(db, current_user, rule.table_name)
    db_rule = ActiveRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.patch("/{rule_id}", response_model=ActiveRuleSchema)
def update_rule(
    rule_id: int, 
    rule_update: ActiveRuleUpdate, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_rule = db.query(ActiveRule).filter(ActiveRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    get_accessible_asset_service_or_403(db, current_user, db_rule.table_name)
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/{rule_id}")
def delete_rule(
    rule_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_rule = db.query(ActiveRule).filter(ActiveRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    get_accessible_asset_service_or_403(db, current_user, db_rule.table_name)
    
    db.delete(db_rule)
    db.commit()
    return {"status": "success"}


@router.post("/suggestions/internal", response_model=List[ActiveRuleSchema])
def upsert_rule_suggestions_internal(
    payload: RuleSuggestionBatch,
    db: Session = Depends(deps.get_db),
):
    created_or_updated = []
    for suggestion in payload.suggestions:
        db_rule = (
            db.query(ActiveRule)
            .filter(
                ActiveRule.table_name == suggestion.table_name,
                ActiveRule.column_name == suggestion.column_name,
                ActiveRule.rule_type == suggestion.rule_type,
                ActiveRule.rule_expression == suggestion.rule_expression,
            )
            .first()
        )

        if db_rule:
            db_rule.frequency = (db_rule.frequency or 0) + 1
            db_rule.last_seen = datetime.utcnow()
            db_rule.category = suggestion.category
            db_rule.priority = suggestion.priority
            db_rule.source = suggestion.source
            db_rule.description = suggestion.description
            db_rule.confidence_score = suggestion.confidence_score
        else:
            db_rule = ActiveRule(
                table_name=suggestion.table_name,
                column_name=suggestion.column_name,
                rule_type=suggestion.rule_type,
                rule_expression=suggestion.rule_expression,
                category=suggestion.category,
                priority=suggestion.priority,
                source=suggestion.source,
                description=suggestion.description,
                confidence_score=suggestion.confidence_score,
                frequency=1,
                last_seen=datetime.utcnow(),
                is_active=True,
                is_applied=False,
            )
            db.add(db_rule)
        created_or_updated.append(db_rule)

    db.commit()
    for rule in created_or_updated:
        db.refresh(rule)
    return created_or_updated


@router.post("/suggestions/trigger")
def trigger_rule_suggestions(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    table_name = payload.get("table_name")
    if not table_name:
        raise HTTPException(status_code=400, detail="table_name is required")
    get_accessible_asset_service_or_403(db, current_user, table_name)
    schema_name, asset_name = table_name.split(".", 1) if "." in table_name else ("public", table_name)
    return trigger_airflow_dag(
        "rule_suggestion_agent",
        {
            "catalog": payload.get("catalog", "iceberg"),
            "schema": schema_name,
            "table": asset_name,
            "sample_size": payload.get("sample_size", 10000),
        },
    )


@router.post("/validate/trigger")
def trigger_rule_validation(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    table_name = payload.get("table_name")
    if not table_name:
        raise HTTPException(status_code=400, detail="table_name is required")
    get_accessible_asset_service_or_403(db, current_user, table_name)
    return trigger_airflow_dag(
        "rule_validation_agent",
        {
            "table": table_name,
            "model": payload.get("model", f"silver_{table_name.split('.')[-1]}"),
        },
    )
