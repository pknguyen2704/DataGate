from datetime import datetime, timedelta
from typing import Any, Union

# Thư viện dùng để encode/decode JWT token
from jose import jwt

# Thư viện hash password (bcrypt)
from passlib.context import CryptContext

# Import config từ file config
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)


# =============================
# Password hashing config
# =============================

# Khởi tạo context để hash password bằng bcrypt
# bcrypt là thuật toán hash an toàn (không thể decode lại)
pwd_context = CryptContext(
    schemes=["bcrypt"],   # dùng bcrypt
    deprecated="auto"     # auto handle version cũ
)


# =============================
# Tạo JWT token
# =============================

def create_access_token(
    subject: Union[str, Any],   # user_id hoặc email
    expires_delta: timedelta = None
) -> str:
    """
    Tạo access token (JWT)

    subject: thông tin user (thường là user_id)
    expires_delta: thời gian hết hạn (optional)
    """

    # Nếu có truyền thời gian hết hạn custom
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Nếu không → dùng default từ config
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Payload của token
    to_encode = {
        "exp": expire,          # thời gian hết hạn
        "sub": str(subject)     # subject (user_id)
    }

    # Encode thành JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# =============================
# Verify password
# =============================

def verify_password(
    plain_password: str,   # password user nhập
    hashed_password: str   # password đã hash trong DB
) -> bool:
    """
    So sánh password user nhập với password trong DB
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================
# Hash password
# =============================

def get_password_hash(password: str) -> str:
    """
    Hash password trước khi lưu vào DB
    """
    return pwd_context.hash(password)