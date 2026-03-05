from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from api.db_models.models import RuleModel
from api.schemas.rule import Rule, Methods
from tests.data_test import RULE_DATA

URL_PREFIX = "/api/api_v1/api_management"


@pytest.mark.asyncio
async def test_add_rule(db_session: AsyncSession, test_client: AsyncClient) -> None:
    test_rule = Rule(
        method=Methods.GET,
        url='test_url/api/api_v1/id',
        call_backend=False,
        status_code=HTTPStatus.OK,
        response="""{'message': 'Validation Failed'}""",
        response_delay=10,
        custom_headers={"header_1": "value_1"},
        response_media_type="application/json",
    )

    response: Response = await test_client.post(f'{URL_PREFIX}/rule', json=test_rule.model_dump())

    assert response.status_code == HTTPStatus.CREATED
    response_json = response.json()
    rule_query = await db_session.execute(select(RuleModel).where(RuleModel.id == response.json()['id']))
    rule = rule_query.scalars().first()
    for key, value in test_rule.dict().items():
        assert getattr(rule, key) == value
        assert response_json[key] == value


@pytest.mark.asyncio
async def test_disable_rule(db_session: AsyncSession, test_client: AsyncClient) -> None:
    test_rule = RuleModel(
        **RULE_DATA,
        enable=True,
    )
    db_session.add(test_rule)
    await db_session.commit()
    await db_session.refresh(test_rule)

    result: Response = await test_client.patch(
        f'{URL_PREFIX}/rule/{test_rule.id}/status',
        json={"status": False},
    )

    assert result.status_code == HTTPStatus.OK
    assert not result.json()['enable']


@pytest.mark.asyncio
async def test_delete_rule(db_session: AsyncSession, test_client: AsyncClient) -> None:
    test_rule = RuleModel(
        **RULE_DATA,
        enable=True,
    )
    db_session.add(test_rule)
    await db_session.commit()
    await db_session.refresh(test_rule)

    result: Response = await test_client.delete(
        f'{URL_PREFIX}/rule/{test_rule.id}',
    )

    assert result.status_code == HTTPStatus.NO_CONTENT
    query_result: RuleModel = await db_session.execute(select(RuleModel))
    assert not query_result.first()


@pytest.mark.asyncio
async def test_get_rules(db_session: AsyncSession, test_client: AsyncClient) -> None:
    methods = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
    for idx, method in enumerate(methods):
        test_rule = RuleModel(
            method=method,
            url=f'test_url/api/api_{method}/id_{idx}',
            call_backend=False,
            status_code=HTTPStatus.OK,
            response="""{"method": method}""",
            enable=True,
        )
        db_session.add(test_rule)
        await db_session.commit()

    result: Response = await test_client.get(f'{URL_PREFIX}/rules')

    assert result.status_code == HTTPStatus.OK
    result_json = result.json()
    assert len(result_json) == len(methods)


@pytest.mark.asyncio
async def test_patch_rule_mock_count(db_session: AsyncSession, test_client: AsyncClient) -> None:
    test_rule = RuleModel(**RULE_DATA)
    db_session.add(test_rule)
    await db_session.commit()
    await db_session.refresh(test_rule)

    result: Response = await test_client.patch(
        f'{URL_PREFIX}/rule/{test_rule.id}/mock_count',
        json={"mock_count": 10},
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json()['mock_count'] == 10
