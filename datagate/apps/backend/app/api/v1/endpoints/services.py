from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, Service as ServiceSchema
from app.services.connection_manager import ConnectionManager

router = APIRouter()

@router.post("/test")
def test_connection(service: ServiceCreate):
    res = ConnectionManager.test_connection(service)
    if res["status"] == "success":
        res["schemas"] = ConnectionManager.get_schemas(service.service_type, service.connection_url)
    return res

@router.get("/raw/tables")
def get_raw_tables(service_type: str, url: str, schema: str = None):
    return ConnectionManager.get_tables(service_type, url, schema)

@router.post("/", response_model=ServiceSchema)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    # Auto-test
    test_res = ConnectionManager.test_connection(service)
    status = "healthy" if test_res["status"] == "success" else "unhealthy"
    
    db_service = Service(
        name=service.name,
        service_type=service.service_type,
        connection_url=service.connection_url,
        integrated_tables=service.integrated_tables,
        status=status
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/", response_model=list[ServiceSchema])
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()

@router.get("/{service_id}/schemas")
def get_service_schemas(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return ConnectionManager.get_schemas(service.service_type, service.connection_url)

@router.get("/{service_id}/tables")
def get_service_tables(service_id: int, schema: str = None, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return ConnectionManager.get_tables(service.service_type, service.connection_url, schema)

@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(service)
    db.commit()
    return {"status": "success", "message": "Service deleted"}
