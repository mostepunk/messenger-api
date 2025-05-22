# from .routes import router as routers
from fastapi import APIRouter

# add tags
# router = APIRouter(
#    tags=["chat_module"],
#    prefix="/chat_module",
# )

router = APIRouter()

# example including routers from api/routes
# router.include_router(routers.router)