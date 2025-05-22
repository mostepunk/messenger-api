from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.uuid_generate_v4(),
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    def update_relation(self, relation: str, data: dict):
        for key, value in data.items():
            if key == "id":
                continue
            setattr(getattr(self, relation), key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__}.ID:{self.id}>"
