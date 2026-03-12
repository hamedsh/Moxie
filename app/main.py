import random
import string
import time

import sentry_sdk
from fastapi import FastAPI
from starlette.requests import Request

from api.api_v1.api_managment import api_management
from api.api_v1.healthcheck import api_healthcheck
from api.api_v1.api_gateway import api_gateway
from api.deps import logger
from core.config import settings
from core.session import async_session
from core.context import set_db_session, clear_db_session


async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    logger.debug(f"rdi={idem} headers: %s", str(request.headers))
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

    return response


async def db_session_middleware(request: Request, call_next):
    """Middleware to manage database session in context variables."""
    async with async_session() as session:
        set_db_session(session)
        try:
            response = await call_next(request)
        finally:
            clear_db_session()
    return response


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        release=settings.RELEASE,
        environment=settings.ENV,
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/",
)
app.middleware('http')(db_session_middleware)
app.middleware('http')(log_requests)

app.include_router(api_gateway, prefix=f"{settings.API_V1_STR}/api_gateway")
app.include_router(api_management, prefix=f"{settings.API_V1_STR}/api_management")
app.include_router(api_healthcheck, prefix="/api/v1/healthcheck")
