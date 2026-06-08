from fastapi import HTTPException, status


class BaseException(HTTPException):
    """Base exception for the application."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=message)


class DuplicateResourceException(BaseException):
    """Exception raised when a duplicate resource is found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class ValidationException(BaseException):
    """Exception raised for validation errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResourceNotFoundException(BaseException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
