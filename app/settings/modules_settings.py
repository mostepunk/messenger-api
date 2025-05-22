from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


class ModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="modules_section_")

    # Папка должна заканчиваться на точку
    modules_dir: str = "app.modules."
    enabled_modules: str = "BASE"
    base_modules: list[str] = [
        "healthcheck_module",
        "auth_module",
        "base_module",
        # "catalogues_module",
    ]

    @property
    def modules(self) -> list[str]:
        """Получить список активированных модулей.

        Returns:
            list[str]:
        """
        return self.enabled_modules.split(",")

    @property
    def root_base_dir(self) -> str:
        """Преобразовывает переменную MODULES_SECTION_MODULES_DIR.

        `app.modules.` -> `app/modules`
        Путь не должен оканчиваться на слэш.
        Используется в скрипте для создания новых модулей.

        Returns:
            str:
        """
        return self.modules_dir.replace(".", "/").rstrip("/")
