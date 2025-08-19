from fastapi import APIRouter, BackgroundTasks, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.dependencies.token import get_current_user_token
from app.database.repositories.audit import AuditRepository
from app.database.repositories.tokens import TokensRepository
from app.database.repositories.users import UsersRepository
from app.exceptions import AuthFailedException, NotFoundException
from app.models.audit import LogEntry
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.core import SuccessResponseScheme
from app.schemas.token import TokenPairSchema, TokenVerifySchema
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
        user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_rep: AuditRepository = Depends(get_repository(AuditRepository)),
):
    created_user = await user_repo.create(new_user=new_user)
    await audit_rep.create(
        new_entry=LogEntryCreateSchema(user_id=created_user.id, action=LogEntry.ACTION_REGISTER)
    )
    bg_tasks.add_task(task_notify_on_email_confirm, created_user.id, user_repo)
    return created_user


@router.post("/login", name="auth:login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    user: User = await user_repo.authenticate(email=form_data.username, password=form_data.password)

    if not user:
        raise AuthFailedException()

    entry_log: LogEntryCreateSchema = LogEntryCreateSchema(
        user_id=user.id,
        action=LogEntry.ACTION_LOGIN
    )
    await audit_repo.create(new_entry=entry_log)

    token_pair: TokenPairSchema = jwt_service.create_token_pair(user=user)
    return {
        "token": token_pair.access.token
    }


@router.get("/logout", response_model=SuccessResponseScheme, name="auth:logout")
async def logout(
        current_user: User = Depends(get_current_active_user),
        token: str = Depends(get_current_user_token),
        tokens_repo: TokensRepository = Depends(get_repository(TokensRepository))
):
    await tokens_repo.blacklist_token(token=token)
    return {
        "message": "Successfully logged out"
    }


@router.get("/profile", response_model=UserPublicSchema, name="auth:profile-detail")
async def profile_detail(
        current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.put("/profile", response_model=UserPublicSchema, name="auth:profile-update")
async def profile_update(
        user_data: UserUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    updated_user = await user_repo.update(user=current_user, data=user_data)
    return updated_user


@router.post("/verify_token", name="auth:token-verify")
async def token_verify(
        token_data: TokenVerifySchema,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    payload = jwt_service.decode_token(token=token_data.token)
    user = await user_repo.get_by_id(user_id=int(payload.sub))

    if not user:
        raise NotFoundException(detail="User not found")

    return {
        "msg": "success"
    }
