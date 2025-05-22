import inspect

from app.modules.catalogues_module.db import models
from app.modules.catalogues_module.db.models.base_catalogue import BaseCatalogueModel

CATALOGUE_PREFIX = "catalogue_"


def generate_catalogue_registry():
    registry = {}

    for name, obj in inspect.getmembers(models):
        if (
            inspect.isclass(obj)
            and issubclass(obj, BaseCatalogueModel)
            and obj is not BaseCatalogueModel
        ):
            tablename = getattr(obj, "__tablename__", "")
            if tablename.startswith(CATALOGUE_PREFIX):
                key = tablename[len(CATALOGUE_PREFIX) :].replace("_", "-")
                registry[key] = obj

    return registry


catalogue_registry = generate_catalogue_registry()
