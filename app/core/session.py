from typing import TYPE_CHECKING

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings


if settings.ENV == "TEST":
    sqlalchemy_database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
else:
    sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(
    sqlalchemy_database_uri, pool_pre_ping=True, poolclass=pool.NullPool, echo=True,
)

async_session = async_sessionmaker(
    bind=async_engine, autocommit=False, autoflush=False, class_=AsyncSession,
)

if TYPE_CHECKING:
    async_session: async_sessionmaker[AsyncSession]  # type: ignore
