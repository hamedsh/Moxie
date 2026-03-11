from typing import TYPE_CHECKING
import re

from sqlalchemy import pool, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings


if settings.ENV == "TEST":
    sqlalchemy_database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
    db_type = settings.TEST_DB_TYPE
else:
    sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI
    db_type = settings.DB_TYPE


def regexp_match(pattern: str, text: str) -> bool:
    """
    Cross-database regex match function.
    Works with SQLite, MySQL, and PostgreSQL.
    """
    try:
        return bool(re.match(pattern, text))
    except (TypeError, re.error):
        return False


# For SQLite, use StaticPool; for others use NullPool
if db_type.lower() == "sqlite":
    engine_kwargs = {
        "poolclass": pool.StaticPool,
        "connect_args": {"check_same_thread": False},
        "echo": True,
    }
else:
    engine_kwargs = {
        "pool_pre_ping": True,
        "poolclass": pool.NullPool,
        "echo": True,
    }

async_engine = create_async_engine(
    sqlalchemy_database_uri,
    **engine_kwargs,
)

# Register custom regexp_match function for SQLite
if db_type.lower() == "sqlite":
    @event.listens_for(async_engine.sync_engine, "connect")
    def create_regexp_function(dbapi_conn, connection_record):
        """Register the regexp_match function with SQLite."""
        dbapi_conn.create_function("regexp_match", 2, regexp_match)

async_session = async_sessionmaker(
    bind=async_engine, autocommit=False, autoflush=False, class_=AsyncSession,
)

if TYPE_CHECKING:
    async_session: async_sessionmaker[AsyncSession]  # type: ignore
