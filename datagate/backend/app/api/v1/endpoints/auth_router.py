from fastapi import APIRouter
from app.schemas import LoginRequest, TokenResponse, UserMeOut
from app.services import AuthService
from app.db.session import get_db
from app.api.deps import get_current_user
from sqlalchemy.orm import Session
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@auth_router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    return service.login(data)

@auth_router.get("/me", response_model=UserMeOut)
def get_me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    return service.get_me(current_user)
    
@auth_router.post("/logout")
def logout():
    return None