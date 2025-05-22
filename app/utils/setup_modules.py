import importlib
import logging

from fastapi import FastAPI

from app.modules.base_module.db.models.base import Base
from app.settings import config

LOG_PREFIX = "[MODULES]:"


class SetupModules:
    """Настройка модулей из переменных окружения:

    - Извлечь из переменной окружения названия всех модулей.
    - Импортировать модуль из папки.
    - Добавить в фастапи роут каждого модуля.
    - Функционал по импорту SQLAlchemy моделей из каждого модуля.
    """

    def __init__(
        self,
        modules: list[str] = config.modules.modules,
        modules_dir: str = config.modules.modules_dir,
    ) -> None:
        self.raw_modules = modules
        self.modules_dir = modules_dir
        self.imported_modules = []

        self.parse_modules()
        self.import_modules()

    def parse_modules(self) -> None:
        """Распарсить входящие модули.

        Извлечь базовые модули, если переменная BASE была указана.
        """
        if "BASE" in self.raw_modules:
            del self.raw_modules[self.raw_modules.index("BASE")]
            self.raw_modules.extend(config.modules.base_modules)
        self.delete_duplicated_module_names()

    def delete_duplicated_module_names(self) -> None:
        """Удалить дубли, модулей из списка.

        Самый простой вариант это:
        self.raw_modules = set(self.raw_modules)
        Но если сделать множество, то порядок модулей будет постоянно меняться,
        И в свагере будет меняться местами группы тегов.
        """
        not_duplicated = []
        for module in self.raw_modules:
            if module not in not_duplicated:
                not_duplicated.append(module)
        self.raw_modules = not_duplicated

    def import_modules(self) -> None:
        """Преобразовать список строк в модули.

        В случае ошибки игнорировать этот модуль и сообщить об этом в логе.
        """
        for module in self.raw_modules:
            try:
                imported_module = self.load_module(self.modules_dir, module)
            except ModuleNotFoundError:
                logging.exception(f"{LOG_PREFIX} Module <{module}> Not Exist")
            else:
                self.imported_modules.append(imported_module)

    def attach_module_to_app(self, app: FastAPI) -> None:
        """Прикрепить роуты импортированных модулей к приложению fastapi.

        В случае ошибки игнорируется модуль, и сообщается об этом в лог.

        Args:
            app (FastAPI): приложение fastapi
        """
        if not self.imported_modules:
            logging.warning(f"{LOG_PREFIX} No module was imported")
            return

        for module in self.imported_modules:
            try:
                module_router = module.api.router
            except AttributeError:
                logging.exception(
                    f"{LOG_PREFIX} Module {module.__name__} Has no router"
                )
            else:
                logging.info(f"{LOG_PREFIX} Module {module.__name__} enabled")
                app.include_router(module_router, prefix=config.app.prefix)

    @staticmethod
    def load_module(modules_dir: str, module: str):
        """Преобразование текста в модуль.

        хз как обозначить type hint для модуля
        Все что я нашел это <class 'module'>
        """
        return importlib.import_module(modules_dir + module)

    def import_db_models(self) -> list[Base]:
        """Импортировать из установленных модулей модели базы данных."""
        self._extract_module("db.models")

    def _extract_module(self, module_name: str):
        """Извлечь необходимый модуль."""
        if not self.imported_modules:
            logging.warning(f"{LOG_PREFIX} No module was imported")
            return

        for module in self.imported_modules:
            try:
                self._recursive_import(module, module_name)
            except AttributeError:
                logging.warning(
                    f"{LOG_PREFIX} Module {module.__name__} Has no {module_name}"
                )

    @staticmethod
    def _recursive_import(module_obj, module_name: str) -> None:
        """Рекурсивный импорт из модулей.

        На данный момент модули устроены так:
        module_name:
          - __init__.py
            from . import api, db, dispatch, schemas, services
          - db/__init__.py
            from . import cruds, models
          - db/models/__init__.py
            from .tables import TableModel
        Поэтому невозможен простой импорт
        module.db.models
        надо пройти внутрь каждого модуля, и импортировать их отдельно
        ---

        Args:
            module_obj : класс модуль
            module_name(str): имя импортируемого модуля (e.g. db.models.tables)
        """
        modules = module_name.split(".")
        modules_lst = [module_obj]
        for m in modules:
            new = getattr(modules_lst[-1], m)
            modules_lst.append(new)


def attach_modules_to_app(app: FastAPI) -> None:
    """Прикрепить роуты импортированных модулей к приложению fastapi.
    ---
    Usage:
    ```python
    from app.application import get_fastapi_app
    from app.utils.setup_modules import attach_modules_to_app

    fastapi_app = get_fastapi_app()
    attach_modules_to_app(fastapi_app)
    ```
    Args:
        app (FastAPI): app
    """
    s = SetupModules()
    s.attach_module_to_app(app)


def import_database_models():
    """Импортировать из установленных модулей модели базы данных.

    ---

    ```python
    from app.utils.setup_modules import import_database_models

    import_database_models()
    ```
    """
    s = SetupModules()
    models = s.import_db_models()
