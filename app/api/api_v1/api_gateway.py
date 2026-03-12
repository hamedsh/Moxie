from typing import Optional

from fastapi import APIRouter
from starlette.requests import Request

from api.api_v1.utils import _capture_route_logic
from core.context import get_db_session

api_gateway = APIRouter()


@api_gateway.get("/{url_path:path}", include_in_schema=False)
async def capture_routes_get(
    request: Request,
    url_path: str,
):
    return await _capture_route_logic(url_path, request)


@api_gateway.post("/{url_path:path}", include_in_schema=False)
async def capture_routes_post(
    request: Request,
    url_path: str,
    request_body: Optional[object] = None,
):
    db_session = get_db_session()
    return await _capture_route_logic(
        db_session, url_path, request, request_body,
    )


@api_gateway.patch("/{url_path:path}", include_in_schema=False)
async def capture_routes_patch(
    request: Request,
    url_path: str,
    request_body: Optional[object] = None,
):
    db_session = get_db_session()
    return await _capture_route_logic(db_session, url_path, request, request_body)


@api_gateway.delete("/{url_path:path}", include_in_schema=False)
async def capture_routes_delete(
    request: Request,
    url_path: str,
    request_body: Optional[object] = None,
):
    db_session = get_db_session()
    return await _capture_route_logic(db_session, url_path, request, request_body)


@api_gateway.put("/{url_path:path}", include_in_schema=False)
async def capture_routes_put(
    request: Request,
    url_path: str,
    request_body: Optional[object] = None,
):
    db_session = get_db_session()
    return await _capture_route_logic(db_session, url_path, request, request_body)
