from typing import Any

from fastapi import status


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        super().__init__(message)


class BadRequestError(AppError):
    def __init__(
        self,
        message: str = "Bad request",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Unauthorized",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Forbidden",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictError(AppError):
    def __init__(
        self,
        message: str = "Conflict",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationError(AppError):
    def __init__(
        self,
        message: str = "Validation error",
        detail: Any | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
