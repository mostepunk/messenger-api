import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependencies.dependency_db import get_session
from app.modules.healthcheck_module.services.health_service import HealthService
from app.settings.db_settings import DBSettings


def incorrect_connect():
    test_db_settings = DBSettings()
    test_db_settings.db = "database_not_exist"

    async_engine = create_async_engine(
        test_db_settings.async_db_uri,
        pool_pre_ping=True,
        poolclass=NullPool,
        echo=False,
        future=True,
        connect_args={"prepare_threshold": 0, "application_name": "api_v2_async"},
    )
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return async_session


@pytest.fixture(scope="session")
def health_service(session):
    return HealthService(session)


@pytest.fixture(scope="function")
async def session_not_exists():
    incorrect_session = incorrect_connect()
    async with incorrect_session() as session:
        yield session


@pytest.fixture(scope="function")
async def incorrect_health_service(session_not_exists):
    return HealthService(
        session_not_exists,
    )


async def override_get_session():
    incorrect_session = incorrect_connect()
    async with incorrect_session() as session:
        yield session


@pytest.fixture(scope="function")
async def incorrect_app(app):
    app.dependency_overrides[get_session] = override_get_session
    yield app
