from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import async_session


# Dependency to get the database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
