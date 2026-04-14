from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, Service as ServiceSchema
from app.services.connection_manager import ConnectionManager
from app.services.observability_scanner import ObservabilityScanner
from app import models

router = APIRouter()

@router.post("/{service_id}/scan")
def scan_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return ObservabilityScanner.scan_service(db, service_id)

@router.post("/test")
def test_connection(
    service: ServiceCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    res = ConnectionManager.test_connection(service)
    if res["status"] == "success":
        res["schemas"] = ConnectionManager.get_schemas(service.service_type, service.connection_url)
    return res

@router.get("/raw/tables")
def get_raw_tables(
    service_type: str, 
    url: str, 
    schema: str = None,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    return ConnectionManager.get_tables(service_type, url, schema)

@router.post("/", response_model=ServiceSchema)
def create_service(
    service: ServiceCreate, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # Auto-test
    test_res = ConnectionManager.test_connection(service)
    status = "healthy" if test_res["status"] == "success" else "unhealthy"
    
    db_service = Service(
        name=service.name,
        service_type=service.service_type,
        connection_url=service.connection_url,
        integrated_tables=service.integrated_tables,
        status=status,
        owner_id=current_user.id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/", response_model=list[ServiceSchema])
def get_services(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # Only return services owned by the user, or all for superuser
    if current_user.is_superuser:
        return db.query(Service).all()
    return db.query(Service).filter(Service.owner_id == current_user.id).all()

@router.get("/{service_id}/schemas")
def get_service_schemas(
    service_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return ConnectionManager.get_schemas(service.service_type, service.connection_url)

@router.get("/{service_id}/tables")
def get_service_tables(
    service_id: int, 
    schema: str = None, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return ConnectionManager.get_tables(service.service_type, service.connection_url, schema)

@router.put("/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and db_service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = service_in.model_dump(exclude_unset=True)
    
    # If connection URL is updated, re-test it
    if "connection_url" in update_data:
        # Create a temp object for testing
        test_obj = ServiceCreate(
            name=update_data.get("name", db_service.name),
            service_type=db_service.service_type,
            connection_url=update_data["connection_url"]
        )
        test_res = ConnectionManager.test_connection(test_obj)
        db_service.status = "healthy" if test_res["status"] == "success" else "unhealthy"

    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/{service_id}")
def delete_service(
    service_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(service)
    db.commit()
    return {"status": "success", "message": "Service deleted"}

@router.post("/{service_id}/refresh-tables")
def refresh_service_tables(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check ownership
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get current tables from source
    try:
        # We assume the schema is part of the integrated tables list or we use the first one found
        # In a real app, service would have a 'default_schema' field.
        # For now, let's just get tables from the connection URL's schema if specified or use a param
        # We'll use get_tables which we already have logic for
        current_tables = ConnectionManager.get_tables(service.service_type, service.connection_url)
        
        # Intersect integrated_tables with current_tables to remove orphans
        if service.integrated_tables:
            valid_tables = [t for t in service.integrated_tables if t in current_tables]
            service.integrated_tables = valid_tables
            db.add(service)
            db.commit()
            db.refresh(service)
            return {"status": "success", "updated_tables": valid_tables}
        
        return {"status": "success", "message": "No tables integrated yet"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh tables: {str(e)}")
