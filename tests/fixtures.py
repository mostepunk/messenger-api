import asyncio
import os
import sys

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy_utils import create_database, drop_database

from app.adapters.db import ASYNC_SESSION
from app.fastapi_engine.app import fastapi_app
from app.settings import config

os.environ["TESTING"] = "True"


@pytest.fixture(scope="session", autouse=True)
def temp_db() -> str:
    """Созидание тестовой БД."""
    try:
        print(config.db.dsn_no_driver)
        create_database(config.db.dsn_no_driver)  # Создаем БД
        alembic_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
        )
        print(alembic_path)
        alembic_cfg = Config(alembic_path)
        command.upgrade(alembic_cfg, "head")  # выполняем миграции
        yield

    finally:
        drop_database(config.db.dsn_no_driver)  # удаляем БД
        os.environ["TESTING"] = "False"


@pytest.fixture(scope="session")
async def session():
    async with ASYNC_SESSION() as session:
        print(f"Generated {session=}", file=sys.stdout)
        try:
            print(f"Yields {session=}", file=sys.stdout)
            yield session
        except Exception as err:
            print(f"Exception: {err}", file=sys.stderr)
            print(f"Rollback {session=}", file=sys.stderr)
            await session.rollback()
        finally:
            print(f"Close {session=}", file=sys.stdout)
            await session.close()


@pytest.fixture(scope="session")
def event_loop():
    """Make the loop session scope to use session async fixtures.

    https://github.com/pytest-dev/pytest-asyncio/issues/658#issuecomment-1787665571
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    test_app = fastapi_app
    return test_app


@pytest.fixture
async def client(app) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client
