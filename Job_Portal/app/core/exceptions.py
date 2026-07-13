from __future__ import annotations

from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: dict[str, str] | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(AppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(AppException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class RateLimitError(AppException):
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ConflictError(AppException):
    def __init__(self, detail: str = "Conflict error"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
