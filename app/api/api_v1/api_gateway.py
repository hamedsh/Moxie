from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from api.api_v1.utils import _capture_route_logic
from api.deps import get_db
from api.schemas.rule import JsonModel

api_gateway = APIRouter()


@api_gateway.get("/{url_path:path}", include_in_schema=False)
async def capture_routes_get(
    request: Request,
    url_path: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await _capture_route_logic(db_session, url_path, request)


@api_gateway.post("/{url_path:path}", include_in_schema=False)
async def capture_routes_post(
    request: Request,
    url_path: str,
    request_body: Optional[JsonModel] = None,
    db_session: AsyncSession = Depends(get_db),
):
    return await _capture_route_logic(
        db_session, url_path, request, request_body,
    )


@api_gateway.patch("/{url_path:path}", include_in_schema=False)
async def capture_routes_patch(
    request: Request,
    url_path: str,
    request_body: Optional[JsonModel] = None,
    db_session: AsyncSession = Depends(get_db),
):
    return await _capture_route_logic(db_session, url_path, request, request_body)


@api_gateway.delete("/{url_path:path}", include_in_schema=False)
async def capture_routes_delete(
    request: Request,
    url_path: str,
    request_body: Optional[JsonModel] = None,
    db_session: AsyncSession = Depends(get_db),
):
    return await _capture_route_logic(db_session, url_path, request, request_body)


@api_gateway.put("/{url_path:path}", include_in_schema=False)
async def capture_routes_put(
    request: Request,
    url_path: str,
    request_body: Optional[JsonModel] = None,
    db_session: AsyncSession = Depends(get_db),
):
    return await _capture_route_logic(db_session, url_path, request, request_body)
