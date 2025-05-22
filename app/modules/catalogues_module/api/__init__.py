from fastapi import APIRouter

from .routes import catalogue_router

router = APIRouter(
    tags=["Справочники"],
    prefix="/catalogues",
)

router.include_router(catalogue_router.router)
