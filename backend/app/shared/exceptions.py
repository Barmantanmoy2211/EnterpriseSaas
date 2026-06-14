from typing import Any


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__("NOT_FOUND", message, 404, details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: Any = None):
        super().__init__("CONFLICT", message, 409, details)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden", details: Any = None):
        super().__init__("FORBIDDEN", message, 403, details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Any = None):
        super().__init__("VALIDATION_ERROR", message, 422, details)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized", details: Any = None):
        super().__init__("UNAUTHORIZED", message, 401, details)
