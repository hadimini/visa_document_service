from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception class"""
    pass


class NoDefaultTariffException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No default tariff is found"
        )


class AuthEmailAlreadyRegisteredException(BaseAppException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is already registered",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailAlreadyVerifiedException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already confirmed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailNotFoundException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthFailedException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthTokenExpiredException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenBlacklistedException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Blacklisted token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(BaseAppException):
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail if detail else "Forbidden",
        )


class NotFoundException(BaseAppException):
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Not found"
        )


class InvalidOrExpiredConfirmationTokenException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )


class NameExistsException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already exists",
        )


class ObjectExistsException(BaseAppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object already exists"
        )
