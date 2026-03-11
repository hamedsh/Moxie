from fastapi import Request

from app.core.database_context import _session_ctx
from core.session import async_session
from main import app


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 1. Create a new session for this specific request
    async with async_session() as session:
        # 2. Set the context variable
        token = _session_ctx.set(session)
        try:
            response = await call_next(request)
            return response
        finally:
            # 3. Clean up the context variable after the response is sent
            _session_ctx.reset(token)