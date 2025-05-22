from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.base_module.db.models.base import Base


class BaseCatalogueModel(Base):
    __abstract__ = True

    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(String(100), unique=True)
