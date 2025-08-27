from fastapi import Depends

from app.api.dependencies.db import get_repository
from app.database.repositories.urgencies import UrgenciesRepository


async def urgency_list(
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository))
):
    results = await urgencies_repo.get_list()
    return results
