import os

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import DATABASE_URL


DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else DATABASE_URL

engine = AsyncEngine(
    create_engine(DB_URL, echo=False, future=True)
)


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
