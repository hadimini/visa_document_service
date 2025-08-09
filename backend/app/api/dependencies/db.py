from typing import Type, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import async_session
from app.database.repositories.base import BaseRepository


# Dependency to get the database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: AsyncSession = Depends(get_db)) -> Type[BaseRepository]:
        return Repo_type(db)
    return get_repo
