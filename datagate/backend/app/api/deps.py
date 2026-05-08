from app.core.config import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models import User
from app.services import AuthService
from sqlalchemy.orm import Session
from collections.abc import Callable

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{config.api_v1_str}/auth/login",
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token payload"
        )
    
    service = AuthService(db)
    user = service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Inactive user"
        )
    
    return user

def require_permission(permission_code: str) -> Callable:
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        service = AuthService(db)
        if not service.has_permission(current_user, permission_code):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = f"Missing permission: {permission_code}"
            )
        return current_user
    return checker
