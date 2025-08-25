from fastapi import APIRouter, BackgroundTasks, Depends, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.dependencies.token import get_current_user_token
from app.database.repositories.audit import AuditRepository
from app.database.repositories.clients import ClientRepository
from app.database.repositories.tariffs import TariffsRepository
from app.database.repositories.tokens import TokensRepository
from app.database.repositories.users import UsersRepository
from app.exceptions import (
    AuthFailedException,
    NotFoundException,
    NoDefaultTariffException,
    InvalidOrExpiredConfirmationTokenException,
    InvalidTokenException,
    AuthEmailNotFoundException
)
from app.models.audit import LogEntry
from app.models.clients import Client
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.client import ClientCreateSchema
from app.schemas.token import TokenVerifySchema
from app.schemas.user import UserPublicSchema, UserCreateSchema, UserUpdateSchema
from app.services import jwt_service
from app.tasks import task_notify_on_email_confirm

router = APIRouter()


@router.post(
    path="/register",
    response_model=UserPublicSchema,
    name="auth:register",
    status_code=status.HTTP_201_CREATED
)
async def register(
        new_user: UserCreateSchema,
        bg_tasks: BackgroundTasks,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_rep: AuditRepository = Depends(get_repository(AuditRepository)),
        clients_repo: ClientRepository = Depends(get_repository(ClientRepository)),
        tariffs_repo: TariffsRepository = Depends(get_repository(TariffsRepository)),
):
    # Register creates individual clients
    default_tariff = await tariffs_repo.get_default()

    if not default_tariff:
        raise NoDefaultTariffException()

    new_client = ClientCreateSchema(
        tariff_id=default_tariff.id,
        name=f"{new_user.first_name} {new_user.last_name}",
        type=Client.TYPE_INDIVIDUAL  # type: ignore[arg-type]
    )
    new_client = await clients_repo.create(new_client=new_client)
    new_user = new_user.model_copy(update={"individual_client_id": new_client.id})
    created_user = await users_repo.create(new_user=new_user)

    await audit_rep.create(
        new_entry=LogEntryCreateSchema(
            user_id=created_user.id,
            action=LogEntry.ACTION_REGISTER
        )
    )
    bg_tasks.add_task(task_notify_on_email_confirm, created_user)
    return created_user


@router.get(
    path="/confirm-email",
    name="auth:confirm-email",
)
async def confirm_email(
        token: str,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_rep: AuditRepository = Depends(get_repository(AuditRepository))
) -> JSONResponse:
    payload = jwt_service.verify_email_confirmation_token(token=token)

    if not payload:
        raise InvalidOrExpiredConfirmationTokenException()

    user_id = payload.sub

    if not user_id:
        raise InvalidTokenException()

    await users_repo.verify_email(user_id=int(user_id))
    await audit_rep.create(
        new_entry=LogEntryCreateSchema(
            user_id=int(user_id),
            action=LogEntry.ACTION_VERIFY
        )
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email successfully confirmed"}
    )


@router.post(
    path="/confirm-email-resend",
    name="auth:confirm-email-resend",
)
async def confirm_email_resend(
        bg_tasks: BackgroundTasks,
        email: EmailStr = Body(..., embed=True),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> JSONResponse:
    user = await users_repo.get_by_email(email=email)

    if not user:
        raise AuthEmailNotFoundException()

    bg_tasks.add_task(task_notify_on_email_confirm, user)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Confirmation email sent"}
    )


@router.post("/login", name="auth:login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    user = await users_repo.authenticate(email=form_data.username, password=form_data.password)

    if not user:
        raise AuthFailedException()

    entry_log: LogEntryCreateSchema = LogEntryCreateSchema(
        user_id=user.id,
        action=LogEntry.ACTION_LOGIN
    )
    await audit_repo.create(new_entry=entry_log)

    token_pair = jwt_service.create_token_pair(user=user)
    # Todo: Check if needs else
    if token_pair:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"token": token_pair.access}
        )


@router.get("/logout", name="auth:logout")
async def logout(
        current_user: User = Depends(get_current_active_user),
        token: str = Depends(get_current_user_token),
        tokens_repo: TokensRepository = Depends(get_repository(TokensRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
) -> JSONResponse:
    await tokens_repo.blacklist_token(token=token)
    entry_log: LogEntryCreateSchema = LogEntryCreateSchema(
        user_id=current_user.id,
        action=LogEntry.ACTION_LOGOUT
    )
    await audit_repo.create(new_entry=entry_log)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successfully logged out"}
    )


@router.get("/profile", response_model=UserPublicSchema, name="auth:profile-detail")
async def profile_detail(
        current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.put("/profile", response_model=UserPublicSchema, name="auth:profile-update")
async def profile_update(
        user_data: UserUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    updated_user = await users_repo.update(user=current_user, data=user_data)
    entry_log: LogEntryCreateSchema = LogEntryCreateSchema(
        user_id=updated_user.id,
        action=LogEntry.ACTION_UPDATE,
        model_type=User.get_model_type(),
        target_id=updated_user.id
    )
    await audit_repo.create(new_entry=entry_log)
    return updated_user


@router.post("/verify_token", name="auth:token-verify")
async def token_verify(
        token_data: TokenVerifySchema,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> JSONResponse:
    payload = jwt_service.decode_token(token=token_data.token)
    user = await users_repo.get_by_id(user_id=int(payload.sub))

    if not user:
        raise NotFoundException(detail="User not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Success"}
    )
