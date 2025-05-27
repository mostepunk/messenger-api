import multiprocessing
from typing import Literal, Union

from pydantic_settings import SettingsConfigDict

from app.settings.base import ApiMode, BaseSettings


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="api_")

    host: str = "0.0.0.0"
    service_port: int = 8788
    reload: bool = False
    # mode: ApiMode
    workers: int = 1
    prefix: str = ""

    title: str = "Messenger REST-API engine"
    description: str = ""
    version: str = "1.0.0"

    contact_name: str = "Mostepan Vladimir"
    contact_email: str = "user@example.com"

    redoc_path: Union[str, None] = None
    doc_path: str = "/docs"
    no_log_endpoints: str = "docs,openapi.json"

    http: Literal["http", "https"] = "https"
    route_confirm_password: str = "/setup-new-password"
    route_setup_new_password: str = "/confirm-email"

    cors_allowed_hosts: str = "http://localhost:5173,"

    @property
    def allowed_hosts(self):
        return self.cors_allowed_hosts.split(",")

    @property
    def domain(self):
        return f"http://{self.host}:{self.service_port}"

    @property
    def api_settings(self):
        return {
            "title": self.title,
            "description": self.description,
            "version": self.version,
            "contact": {
                "name": self.contact_name,
                "email": self.contact_email,
            },
            "redoc_url": self.prefix + self.redoc_path if self.redoc_path else None,
            "docs_url": self.prefix + self.doc_path if self.doc_path else None,
        }

    @property
    def num_workers(self):
        if self.environment == ApiMode.prod:
            return int(multiprocessing.cpu_count()) + 1
        return self.workers

    @property
    def server_settings(self):
        return {
            "host": self.host,
            "port": self.service_port,
            "workers": self.num_workers,
            "reload": self.reload,
            "loop": "asyncio",
        }

    @property
    def no_log(self):
        """Ендпоинты, которые не надо логировать в log_middleware.py"""
        l = [f"{self.prefix}/{route}" for route in self.no_log_endpoints.split(",")]
        l.append("/openapi.json")
        return l
