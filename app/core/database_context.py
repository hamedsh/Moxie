from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# This variable is unique to each "greenlet" or async task
_session_ctx: ContextVar[Optional[AsyncSession]] = ContextVar("db_session", default=None)

def get_db_session() -> AsyncSession:
    session = _session_ctx.get()
    if session is None:
        raise RuntimeError("Session not initialized in this context")
    return session

def set_db_session(session: AsyncSession):
    return _session_ctx.set(session)