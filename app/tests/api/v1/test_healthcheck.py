from http import HTTPStatus
from unittest.mock import ANY

import pytest
from httpx import AsyncClient
from requests import Response
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_response_when_delay_provided(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    response: Response = await test_client.request(
        method='GET', url='/api/v1/healthcheck',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'database': 'ok', 'date': ANY, 'environment': 'TEST', 'release': None,
    }
