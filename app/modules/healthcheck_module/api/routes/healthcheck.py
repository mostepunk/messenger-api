import logging

from fastapi import APIRouter, Depends

from app.dependencies.services_dependency import get_service
from app.modules.healthcheck_module.services.health_service import HealthService
from app.utils.err_message import err_msg

router = APIRouter()


@router.get("/", name="healthcheck:get")
async def check_health(
    service: HealthService = Depends(get_service(HealthService)),
):
    try:
        return await service.check_health()
    except Exception as err:
        logging.exception(f"ERROR: {err}")
        return err_msg(
            status_code=500,
            error_body={"status": "error", "error": f"{err}"},
        )
