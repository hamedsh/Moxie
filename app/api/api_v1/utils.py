import asyncio
import re
from typing import Optional

from httpx import Response as HttpxResponse, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from api.consts import INCLUDED_HEADERS, DEVELOPMENT_CLUSTER_NAME, DEFAULT_TIMEOUT
from api.crud.rule import search_rule, reduce_use_count
from api.deps import logger
from api.schemas.rule import JsonModel, Rule


def _get_full_path(request, url_path):
    if request.url.query:
        full_path = url_path + "?" + request.url.query
    else:
        full_path = url_path
    return full_path


async def _capture_route_logic(
        db_session: AsyncSession,
        full_path: str,
        request: Request,
        request_body: Optional[JsonModel] = None,
):
    logger.info('request: %s, %s, %s', request.method, full_path, request_body)
    full_path = _get_full_path(request, full_path)
    if request_body:
        request_body = request_body.dict()['__root__']
    endpoint_response: HttpxResponse = await _check_request(
        db_session, request, full_path, request_body,
    )
    return Response(
        content=endpoint_response.content if isinstance(endpoint_response, HttpxResponse) else endpoint_response.body,
        status_code=endpoint_response.status_code,
        media_type=endpoint_response.headers.get('content-type'),
    )


async def find_rule_with_decreased_use_count(session: AsyncSession, method: str, path: str) -> Optional[Rule]:
    rule = await search_rule(session, method, path)
    logger.debug('rule: %s', str(rule))

    if rule:
        await reduce_use_count(session, rule)

    return rule


async def apply_delay_if_needed(rule: Rule):
    if rule and rule.response_delay > 0:
        await asyncio.sleep(rule.response_delay)


def log_request_details(request: Request, path: str):
    logger.info(
        'request details: headers: %s, params: %s, url: %s', request.headers.items(), request.query_params, path,
    )


async def _check_request(
        session: AsyncSession, request: Request, path: str, request_body: Optional[dict] = None,
) -> Response:
    rule = await find_rule_with_decreased_use_count(session, request.method, path)

    await apply_delay_if_needed(rule)

    if rule:
        if rule.call_backend:
            return await _call_request(request, path, request_body, rule.custom_headers)

        log_request_details(request, path)
        media_type = rule.response_media_type or 'application/json'

        return Response(status_code=rule.status_code, content=rule.response, media_type=media_type)

    return await _call_request(request, path, request_body)


async def _call_request(
        request: Request, path: str, request_body: Optional[dict] = None, custom_header: dict = None,
) -> Response:
    request_headers = _generate_headers(request, custom_header or {})
    protocol = 'http' if DEVELOPMENT_CLUSTER_NAME in path.split('/')[0] else 'https'
    url = f'{protocol}://{path}'
    request_detail = {
        'method': request.method,
        'params': request.query_params,
        'url': url,
        'headers': request_headers,
        'json': request_body,
    }
    logger.info('request details: %s', request_detail)
    async with AsyncClient() as client:
        response = await client.request(**request_detail, timeout=DEFAULT_TIMEOUT)
        logger.info('response: %s', response)
        redirect_count = 0
        while response.status_code in {301, 302} and redirect_count < 5:
            new_url = response.headers.get("Location")
            logger.info('redirecting (%s) to: %s', redirect_count, new_url)
            if not new_url:
                break
            request_detail["url"] = new_url
            response = await client.request(**request_detail, timeout=DEFAULT_TIMEOUT)
            logger.info('redirect %s response: %s', redirect_count, response)
            redirect_count += 1
    return response


def _generate_headers(request: Request, custom_headers: dict) -> dict:
    original_headers = dict(request.headers.items())
    logger.debug('original header: %s', original_headers)

    request_headers = {
        **{
            header: value for header, value in original_headers.items()
            if any(re.match(pattern, header, re.IGNORECASE) for pattern in INCLUDED_HEADERS)
        },
        **custom_headers
    }

    return request_headers
