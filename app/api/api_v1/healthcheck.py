from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.crud.rule import execute_raw_query
from core.config import settings
from core.context import get_db_session

api_healthcheck = APIRouter()


@api_healthcheck.get("")
async def healthcheck():
    db_session = get_db_session()
    try:
        db_res = await execute_raw_query(db_session, "select 1")
    except Exception as ex:  # pylint: disable=broad-except
        db_status = f'error: {ex}'
    else:
        if db_res == 1:
            db_status = 'ok'
        else:
            db_status = 'error'
    data = {
        'date': datetime.now(timezone.utc).isoformat(),
        'release': settings.RELEASE,
        'environment': settings.ENV,
        'database': db_status,
    }

    return JSONResponse(content=data)
