from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception class"""
    pass


class NoDefaultTariffException(BaseAppException):
    """
    Exception raised when no default tariff is found in the DB
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No default tariff is found"
        )


class AuthEmailAlreadyRegisteredException(BaseAppException):
    """
    Exception raised when a user tries to register with an email that's already in use.
    """
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is already registered",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailAlreadyVerifiedException(BaseAppException):
    """
    Exception raised when a user tries to verify an email that's already verified.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already confirmed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailNotFoundException(BaseAppException):
    """
    Exception raised when a user tries to verify an email that's not found.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthFailedException(BaseAppException):
    """
    Exception raised when user authentication goes wrong .
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthTokenExpiredException(BaseAppException):
    """
    Exception raised when user's access token has expired.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenBlacklistedException(BaseAppException):
    """
    Exception raised when user's access token is blacklisted.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Blacklisted token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(BaseAppException):
    """
    Exception raised when a user has no permission to perform this action.
    """
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail if detail else "Forbidden",
        )


class NotFoundException(BaseAppException):
    """
    Exception raised when a user tries to access a resource that's not found.
    """
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Not found"
        )


class InvalidOrExpiredConfirmationTokenException(BaseAppException):
    """
    Exception raised when a user's access token has expired.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenException(BaseAppException):
    """
    Exception raised when a user's access token is invalid.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )


class NameExistsException(BaseAppException):
    """
    Exception raised when a user tries to create / update an object with a name already exists.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already exists",
        )


class ObjectExistsException(BaseAppException):
    """
    Exception raised when a user tries to create / update an object with the same params.
    """
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object already exists"
        )
