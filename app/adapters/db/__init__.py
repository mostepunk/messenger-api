from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import config

ASYNC_ENGINE = create_async_engine(
    config.db.async_db_uri,
    pool_pre_ping=True,
    poolclass=NullPool,
    echo=config.db.echo,
    future=True,
    connect_args={"prepare_threshold": 0},
)
ASYNC_SESSION = async_sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SYNC_ENGINE = create_engine(
    config.db.sync_db_uri,
    echo=config.db.echo,
    pool_pre_ping=True,
    poolclass=NullPool,
    # connect_args={"application_name": "api_v2_sync"},
)
SYNC_SESSION = sessionmaker(
    bind=SYNC_ENGINE,
    autocommit=False,
    autoflush=False,
)
