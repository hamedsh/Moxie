from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.rule import execute_raw_query
from api.deps import get_db
from core.config import settings

api_healthcheck = APIRouter()


@api_healthcheck.get("")
async def healthcheck(
        db_session: AsyncSession = Depends(get_db),
):
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
        'date': datetime.utcnow().isoformat(),
        'release': settings.RELEASE,
        'environment': settings.ENV,
        'database': db_status,
    }

    return JSONResponse(content=data)
