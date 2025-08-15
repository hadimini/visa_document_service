from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.tokens import BlackListToken
from app.schemas.token import JWTPayload
from app.services.jwt import JWTService


class TokensRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.jwt_service = JWTService()

    async def blacklist_token(self, *, token: str) -> BlackListToken:
        payload: JWTPayload = self.jwt_service.decode_token(token=token)
        black_list_token = BlackListToken(
            id=payload.jti,
            expire=datetime.fromtimestamp(payload.exp),
        )
        self.db.add(black_list_token)
        await self.db.commit()
        return black_list_token
