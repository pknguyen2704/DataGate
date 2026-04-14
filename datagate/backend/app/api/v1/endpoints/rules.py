from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.rule import ActiveRule
from app.schemas.rule import ActiveRuleCreate, ActiveRuleUpdate, ActiveRule as ActiveRuleSchema
from typing import List
from app import models

router = APIRouter()

@router.get("/", response_model=List[ActiveRuleSchema])
def get_rules(
    table: str = None, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(ActiveRule)
    if table:
        query = query.filter(ActiveRule.table_name == table)
    return query.order_by(ActiveRule.frequency.desc()).all()

@router.post("/", response_model=ActiveRuleSchema)
def create_rule(
    rule: ActiveRuleCreate, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
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
    
    db.delete(db_rule)
    db.commit()
    return {"status": "success"}
