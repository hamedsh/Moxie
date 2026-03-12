# pylint: disable=no-member
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from asyncpg import InvalidCatalogNameError
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import concurrency
from sqlalchemy_utils import database_exists, create_database

from core.base_class import Base
from core.config import settings
from core.context import set_db_session, clear_db_session
from core.session import async_engine, async_session
from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db_setup_sessionmaker():
    assert settings.ENV == "TEST"
    await concurrency.greenlet_spawn(create_db)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def create_db():
    try:
        database_exists(async_engine.engine.url)
    except InvalidCatalogNameError:
        create_database(async_engine.engine.url)


@pytest_asyncio.fixture(autouse=True)
async def db_session(test_db_setup_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        set_db_session(session)
        try:
            yield session
        finally:
            for _, table in Base.metadata.tables.items():
                await session.execute(delete(table))
            await session.commit()
            await session.close()
            clear_db_session()


@pytest_asyncio.fixture(scope="session")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers.update({"Host": "localhost"})
        yield client
