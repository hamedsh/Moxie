import json
from http import HTTPStatus
from typing import Optional

import httpx
import pytest
from httpx import AsyncClient, Headers
# from httpx._models import Headers
from pytest_mock import MockerFixture
from requests import Response
from respx import MockRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from api.api_v1.utils import _generate_headers
from api.db_models.models import RuleModel

XML_RESPONSE = "<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>body</body></note>"

URL_PREFIX = "/api/api_v1/api_gateway"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method, body',
    (
        ('GET', None),
        ('POST', {'key_1': 'value_1', 'key_2': 'value_2'}),
        ('POST', {}),
        ('POST', None),
        ('PATCH', {'key1': ['val1', 'val2']}),
        ('DELETE', {'key1': {'key_1_1': 'val1', 'key_1_2': 'val2'}}),
        ('PUT', {}),
    ),
)
async def test_if_there_is_no_rule_then_it_return_final_response(
    test_client: AsyncClient,
    respx_mock: MockRouter,
    method: str,
    body: Optional[dict],
) -> None:
    test_response = '{"response": "test response"}'
    test_path = 'some_domain/some_url/some_sub_url'
    test_query = 'a=10'

    def httpx_response_mock(request: Request):
        assert f'https://{test_path}' == str(request.url).split('?', maxsplit=1)[0]
        if body:
            assert body == json.loads(request.content.decode())
        return httpx.Response(
            HTTPStatus.CREATED,
            content=test_response,
        )
    respx_mock.route(
        method=method, host='some_domain', path='/some_url/some_sub_url', params={'a': '10'},
    ).mock(side_effect=httpx_response_mock)
    url = f'/api/api_v1/api_gateway/{test_path}?{test_query}'

    response: Response = await test_client.request(
        method=method, url=url, json=body, headers={'X-ZOHO-Include-Formatted': 'value_1'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json.loads(test_response)


# pylint: disable=too-many-arguments,too-many-positional-arguments
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method, response_body, request_body, status_code',
    (
        ('GET', {"key": "value"}, None, HTTPStatus.OK),
        ('POST', {"key": "value"}, {"req_key": "req_value"}, HTTPStatus.CREATED),
        ('PATCH', {"key": "value"}, {"req_key": "req_value"}, HTTPStatus.ACCEPTED),
        ('DELETE', {"key": "value"}, None, HTTPStatus.NO_CONTENT),
        ('PUT', {"key": "value"}, {"req_key": "req_value"}, HTTPStatus.ACCEPTED),
    ),
)
async def test_it_there_is_a_rule_for_get_it_will_return_custom_response(
    test_client: AsyncClient,
    db_session: AsyncSession,
    method,
    response_body,
    request_body,
    status_code,
) -> None:
    test_url = 'some_domain/some_url/'
    test_params = 'some_sub_url=10'
    test_url_rule = r'some_domain/some_url/\?some_sub_url=.*'
    test_rule = RuleModel(
        method=method,
        url=test_url_rule,
        call_backend=False,
        status_code=status_code,
        response=json.dumps(response_body),
        custom_headers={'header_1': 'value_1'},
        response_media_type='application/json',
    )
    db_session.add(test_rule)
    await db_session.commit()

    response: Response = await test_client.request(
        method=method, url=f'{URL_PREFIX}/{test_url}', params=test_params, json=request_body,
    )

    assert response.status_code == status_code
    assert response.headers['Content-Type'] == 'application/json'
    if status_code != HTTPStatus.NO_CONTENT:
        assert response.json() == response_body


@pytest.mark.asyncio
async def test_get_response_when_delay_provided(
    test_client: AsyncClient,
    db_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    test_url = 'some_domain/some_url/some_sub_url'
    test_response_delay = 10
    test_rule = RuleModel(
        method='GET',
        url=test_url,
        call_backend=False,
        status_code=HTTPStatus.CREATED,
        response=json.dumps({'status': 'ok'}),
        response_delay=test_response_delay,
    )
    db_session.add(test_rule)
    await db_session.commit()
    sleep_mock = mocker.patch("api.api_v1.utils.asyncio.sleep")

    response: Response = await test_client.request(
        method='GET', url=f'{URL_PREFIX}/{test_url}', json={},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert sleep_mock.await_args_list[0].args[0] == test_response_delay


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method, response_body, request_body, status_code',
    (
        ('GET', XML_RESPONSE, None, HTTPStatus.OK),
        ('POST', XML_RESPONSE, {"req_key": "req_value"}, HTTPStatus.CREATED),
        ('PATCH', XML_RESPONSE, {"req_key": "req_value"}, HTTPStatus.ACCEPTED),
        ('DELETE', XML_RESPONSE, None, HTTPStatus.NO_CONTENT),
        ('PUT', XML_RESPONSE, {"req_key": "req_value"}, HTTPStatus.ACCEPTED),
    ),
)
async def test_it_there_is_a_rule_for_get_it_will_return_custom_xml_response(  # pylint: disable=too-many-arguments
    test_client: AsyncClient,
    db_session: AsyncSession,
    method,
    response_body,
    request_body,
    status_code,
) -> None:
    test_url = 'some_domain/some_url/'
    test_params = 'some_sub_url=10'
    test_url_rule = r'some_domain/some_url/\?some_sub_url=.*'
    test_rule = RuleModel(
        method=method,
        url=test_url_rule,
        call_backend=False,
        status_code=status_code,
        response=response_body,
        custom_headers={'header_1': 'value_1'},
        response_media_type='application/xml',
    )
    db_session.add(test_rule)
    await db_session.commit()

    response: Response = await test_client.request(
        method=method, url=f'{URL_PREFIX}/{test_url}', params=test_params, json=request_body,
    )

    assert response.status_code == status_code
    assert response.headers['Content-Type'] == 'application/xml'
    if status_code != HTTPStatus.NO_CONTENT:
        assert response.text == response_body


class MockRequest:
    def __init__(self, headers):
        self.headers = Headers(headers)


@pytest.mark.asyncio
async def test_generate_headers_with_matching_included_headers():
    request = MockRequest({'Content-Type': 'application/json', 'Accept': 'application/json'})
    custom_headers = {'X-Custom-Header': 'value'}
    expected_headers = {'content-type': 'application/json', 'accept': 'application/json', 'X-Custom-Header': 'value'}

    assert _generate_headers(request, custom_headers) == expected_headers


@pytest.mark.asyncio
async def test_generate_headers_with_no_matching_included_headers():
    request = MockRequest({'X-Random-Header': 'random'})
    custom_headers = {'X-Custom-Header': 'value'}
    expected_headers = {'X-Custom-Header': 'value', 'x-random-header': 'random'}
    assert _generate_headers(request, custom_headers) == expected_headers


@pytest.mark.asyncio
async def test_generate_headers_with_case_insensitive_matching():
    request = MockRequest({'content-type': 'application/json', 'accept': 'application/json'})
    custom_headers = {'X-Custom-Header': 'value'}
    expected_headers = {'content-type': 'application/json', 'accept': 'application/json', 'X-Custom-Header': 'value'}
    assert _generate_headers(request, custom_headers) == expected_headers


@pytest.mark.asyncio
async def test_generate_headers_with_empty_original_and_custom_headers():
    request = MockRequest({})
    custom_headers = {}
    expected_headers = {}
    assert _generate_headers(request, custom_headers) == expected_headers
