"""Context variables for managing database sessions across requests."""

from contextvars import ContextVar
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

# Context variable to store the database session
_db_session_context: ContextVar[Optional[AsyncSession]] = ContextVar(
    "db_session", default=None
)


def set_db_session(session: AsyncSession) -> None:
    """Set the database session in the context."""
    _db_session_context.set(session)


def get_db_session() -> Optional[AsyncSession]:
    """Get the database session from the context."""
    return _db_session_context.get()


def clear_db_session() -> None:
    """Clear the database session from the context."""
    _db_session_context.set(None)
