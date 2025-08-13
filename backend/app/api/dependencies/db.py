from typing import Type, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.repositories.base import BaseRepository


def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: AsyncSession = Depends(get_session)) -> Type[BaseRepository]:
        return Repo_type(db)
    return get_repo
