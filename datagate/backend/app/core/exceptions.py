from typing import Any, Dict, Optional


class AppError(Exception):
    """Base error class for the application."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", detail: Any = None):
        super().__init__(message, status_code=404, detail=detail)


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", detail: Any = None):
        super().__init__(message, status_code=400, detail=detail)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", detail: Any = None):
        super().__init__(
            message,
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", detail: Any = None):
        super().__init__(message, status_code=403, detail=detail)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", detail: Any = None):
        super().__init__(message, status_code=409, detail=detail)
