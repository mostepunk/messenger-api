"""Инициализация нового модуля.

- new_module/
├── api/
│   ├──  __init__.py
│   └── routes/
│     ├── __init__.py
│     └── rotuer.py
├── db/
│    ├── __init__.py
│    ├──  cruds/
│    │ └── __init__.py
│    └──  models/
│      └── __init__.py
├── dependencies/
│     └── __init__.py
├── schemas/
│    └──  __init__.py
├── services/
│    └──  __init__.py
├── tests/
│    └──  __init__.py
├── utils/
│    └──  __init__.py
└── __init__.py
"""

import logging

from .base_creator import BaseModuleCreator


class ModuleCreator(BaseModuleCreator):
    def create_modules(self) -> None:
        logging.debug(f"Start creating {self.module_path}")
        self.create_module(self.module_path)
        self.write_file(
            f"{self.module_path}/__init__.py",
            "from . import api, db, schemas, services",
        )
        self.create_file(f"{self.module_path}/readme.md")
        self.write_file(
            f"{self.module_path}/readme.md",
            f"# {self.name}\n\nОписание модуля {self.name}\n",
        )
        self.create_api_module()
        self.create_database_module()
        self.create_module(f"{self.module_path}/dependencies")
        self.create_module(f"{self.module_path}/schemas")
        self.create_module(f"{self.module_path}/services")
        self.create_module(f"{self.module_path}/tests")
        logging.info(f"Module {self.module_path} created successfully")

    def create_api_module(self) -> None:
        """Создание модуля API.

        Структура модуля:
        ```
        api/
         ├──  __init__.py
         └── routes/
           ├── __init__.py
           └── rotuer.py
        ```
        """
        api_module = f"{self.module_path}/api"
        self.create_module(api_module)
        self.create_module(f"{self.module_path}/api/routes")
        self.create_file(f"{self.module_path}/api/routes/router.py")

        api_init_file = (
            "# from .routes import router as routers\n"
            "from fastapi import APIRouter\n\n"
            "# add tags\n"
            "# router = APIRouter(\n"
            f'#    tags=["{self.name}"],\n'
            f'#    prefix="/{self.name}",\n'
            "# )\n\n"
            "router = APIRouter()\n\n"
            "# example including routers from api/routes\n"
            "# router.include_router(routers.router)"
        )
        self.write_file(f"{self.module_path}/api/__init__.py", api_init_file)

        router_file = "from fastapi import APIRouter\n\nrouter = APIRouter()"
        self.write_file(f"{self.module_path}/api/routes/router.py", router_file)

        routes_init_text = "from . import router"
        self.write_file(f"{self.module_path}/api/routes/__init__.py", routes_init_text)

    def create_database_module(self) -> None:
        """Создание модуля для БД.

        Структура модуля:
        ```
        db/
         ├── __init__.py
         ├── cruds/
         │ └── __init__.py
         └── models/
           └── __init__.py
        ```
        """
        main_module = f"{self.module_path}/db"
        self.create_module(main_module)
        self.create_module(f"{main_module}/cruds")
        self.create_module(f"{main_module}/models")

        db_init_file = "from . import cruds, models"
        self.write_file(f"{self.module_path}/db/__init__.py", db_init_file)

        db_models_init_file = "# from .model import NewModelCRUD"
        self.write_file(
            f"{self.module_path}/db/models/__init__.py", db_models_init_file
        )

        self.create_file(f"{main_module}/models/model.py")
        db_crud_file = (
            "# from app.modules.base_module.db.cruds.base_crud import BaseCRUD\n"
            "\n"
            "\n"
            "# class NewModelCRUD(BaseCRUD[UserBaseSchema, DatabaseUserSchema, UserModel]):\n"
            "#     _in_schema = UserBaseSchema\n"
            "#     _out_schema = DatabaseUserSchema\n"
            "#     _table = UserModel\n\n"
            "#     def __init__(self, session: AsyncSession):\n"
            "#         self.session = session\n\n"
        )
        self.write_file(f"{main_module}/cruds/model_crud.py", db_crud_file)
        db_cruds_model_file = (
            "# from sqlalchemy.orm import Mapped, mapped_column\n"
            "\n"
            "# from app.modules.base_module.db.models.base import Base\n"
            "\n"
            "\n"
            "# class UserModel(Base):\n"
            '#     __tablename__ = "auth_users"\n'
            "#     name: Mapped[str]\n"
            "#     email: Mapped[str] = mapped_column(unique=True)\n"
            "#     password: Mapped[str]\n"
            "#     description: Mapped[str | None]\n"
        )
        self.write_file(f"{main_module}/models/model.py", db_cruds_model_file)
