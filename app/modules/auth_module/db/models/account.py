from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base

if TYPE_CHECKING:
    from app.modules.chat_module.db.models.profile import ProfileModel


class AccountModel(Base):
    __tablename__ = "account"

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    description: Mapped[str | None]
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    confirmation_token: Mapped[str | None] = mapped_column(String(300))
    profile_id: Mapped[UUID] = mapped_column(FK("profile.id", ondelete="CASCADE"))

    sessions: Mapped[list["AccountSessionModel"] | None] = relationship(
        lazy="joined", cascade="all, delete-orphan"
    )
    # TODO: Выяснить, является ли это проблемой.
    # sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[AccountModel(account)],
    # expression 'ProfileModel' failed to locate a name ('ProfileModel').
    # If this is a class name, consider adding this relationship() to the
    # <class 'app.modules.auth_module.db.models.account.AccountModel'>
    # class after both dependent classes have been defined.
    profile: Mapped["ProfileModel"] = relationship(
        lazy="joined",  # cascade="all, delete-orphan"
    )


class AccountSessionModel(Base):
    __tablename__ = "account_session"

    refresh_token: Mapped[str] = mapped_column(String(300), unique=True)
    access_token: Mapped[str] = mapped_column(String(300), unique=True)
    fingerprint: Mapped[str | None] = mapped_column(String(40))
    account_id: Mapped[UUID] = mapped_column(FK("account.id", ondelete="CASCADE"))
