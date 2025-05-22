from typing import Callable

from fastapi import BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.dependency_db import get_session
from app.modules.base_module.services.base_service import BaseService


def get_service(
    repo_type: type[BaseService],
) -> Callable[[BackgroundTasks, AsyncSession], BaseService]:
    def _get_service(
        session: AsyncSession = Depends(get_session),
    ) -> BaseService:
        return repo_type(session)

    return _get_service
