from datetime import datetime

from mypyc.ir.ops import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.tokens import BlackListToken
from app.schemas.token import JWTPayloadSchema
from app.services.jwt import JWTService


class TokensRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.jwt_service = JWTService()

    async def get_all_blacklisted(self) -> Sequence[BlackListToken]:
        statement = select(BlackListToken)
        results = await self.db.execute(statement)
        return results.scalars().all()

    async def get_by_id(self, *, token_id: str) -> BlackListToken | None:
        statement = select(BlackListToken).where(BlackListToken.id == token_id)
        result = await self.db.execute(statement)
        token = result.one_or_none()
        return token[0] if token else None

    async def blacklist_token(self, *, token: str) -> BlackListToken:
        payload: JWTPayloadSchema = self.jwt_service.decode_token(token=token)
        black_list_token = BlackListToken(
            id=payload.jti,
            expire=datetime.fromtimestamp(payload.exp),
        )
        self.db.add(black_list_token)
        await self.db.commit()
        return black_list_token
