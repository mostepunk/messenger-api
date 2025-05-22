import logging

from app.modules.base_module.services.base_service import BaseService
from app.modules.healthcheck_module.db.cruds.health_crud import HealthCRUD


class HealthService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self.crud = HealthCRUD(self.session)

    async def check_health(self):
        answer = await self.crud.check_connect()
        logging.debug("DB ok")
        return {"health": "ok"}
