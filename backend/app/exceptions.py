from fastapi import HTTPException, status


class NoDefaultTariffException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No default tariff is found"
        )


class AuthEmailAlreadyRegisteredException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is already registered",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailAlreadyVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already confirmed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthEmailNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthFailedException(HTTPException):
    def __int__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthTokenExpiredException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenBlacklistedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Blacklisted token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail if detail else "Forbidden",
        )


class NotFoundException(HTTPException):
    def __init__(self, detail: str = '') -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Not found"
        )


class InvalidOrExpiredConfirmationTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
