from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from core.config import settings
from api.deps import logger


def _get_pool_config() -> dict:
    """Get connection pool configuration based on database type and env vars.
    
    Returns:
        dict: Pool configuration options
    """
    db_type = settings.DB_TYPE.lower()
    
    # Default pool size and overflow
    pool_size = int(settings.DB_POOL_SIZE or 20)
    max_overflow = int(settings.DB_POOL_MAX_OVERFLOW or 10)
    pool_recycle = int(settings.DB_POOL_RECYCLE or 3600)  # 1 hour
    pool_pre_ping = settings.DB_POOL_PRE_PING or True
    
    logger.info(
        f"Database connection pool config: pool_size={pool_size}, "
        f"max_overflow={max_overflow}, recycle={pool_recycle}s, pre_ping={pool_pre_ping}"
    )
    
    if db_type == "sqlite":
        # SQLite uses NullPool (no connection pooling)
        return {"poolclass": NullPool}
    else:
        # MySQL and PostgreSQL use QueuePool
        return {
            "poolclass": QueuePool,
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": pool_pre_ping,
        }


# Create async engine with appropriate pool configuration
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO,
    **_get_pool_config(),
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
