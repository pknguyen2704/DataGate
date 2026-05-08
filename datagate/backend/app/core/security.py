from datetime import datetime, timedelta
from typing import Any
from passlib.context import CryptContext
from app.core.config import config
from jose import jwt, JWTError

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

def create_access_token(
    subject: str | Any
) -> str:
    expires_delta = timedelta(minutes=config.access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(subject),
        "exp": expire
    }

    return jwt.encode(
        payload, 
        config.secret_key,
        algorithm=config.algorithm
    )

def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        result = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        return result
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)