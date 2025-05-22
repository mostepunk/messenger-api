from fastapi import APIRouter

from .routes import healthcheck

router = APIRouter(
    tags=["healthcheck"],
    prefix="/healthcheck",
)

router.include_router(healthcheck.router)
