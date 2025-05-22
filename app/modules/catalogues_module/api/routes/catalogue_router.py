from typing import Annotated, Callable

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.services_dependency import get_service
from app.modules.auth_module.dependencies.jwt_decode import get_user_from_token
from app.modules.catalogues_module.db.catalogue_registry import catalogue_registry
from app.modules.catalogues_module.schemas.catalogues import CatalogueSchema
from app.modules.catalogues_module.services import CatalogueService

router = APIRouter()


def generate_catalogue_endpoint(name: str) -> Callable:
    async def endpoint(
        account: Annotated[get_user_from_token, Depends()],
        service: CatalogueService = Depends(get_service(CatalogueService)),
    ):
        try:
            return await service.get_catalogue_by_name(name)
        except ValueError:
            raise HTTPException(status_code=404, detail="Catalogue not found")

    return endpoint


for path_name in catalogue_registry.keys():
    router.add_api_route(
        f"/{path_name}/",
        generate_catalogue_endpoint(path_name),
        response_model=list[CatalogueSchema],
        methods=["GET"],
        name=f"Get catalogue: {path_name}",
    )
