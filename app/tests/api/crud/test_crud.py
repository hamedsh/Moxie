from http import HTTPStatus

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import api.crud.rule as rule_crud
from api.db_models.models import RuleModel
from api.schemas.rule import Rule, RuleStatusChange
from tests.data_test import RULE_DATA


@pytest.mark.asyncio
async def test_create_rule(db_session: AsyncSession) -> None:
    test_rule = Rule(**RULE_DATA)

    await rule_crud.create_rule(test_rule)

    query = select(func.count(RuleModel.id))  # pylint: disable=not-callable
    rule: list[RuleModel] = await db_session.execute(query)
    rule_count = rule.scalar()
    assert rule_count == 1


@pytest.mark.asyncio
async def test_disable_rule(db_session: AsyncSession) -> None:
    test_rule = RuleModel(**RULE_DATA)
    db_session.add(test_rule)
    await db_session.commit()
    rule = await db_session.execute(select(RuleModel))
    rule: RuleModel = rule.scalars().first()

    updated_rule: RuleModel = await rule_crud.disable_rule(rule.id, RuleStatusChange(enable=False))

    assert not updated_rule.enable
    await db_session.refresh(rule)
    assert not rule.enable


@pytest.mark.parametrize(
    'mock_count, expected_value',
    (
        (2, 1),
        (1, 0),
        (0, 0),
        (-1, -1),
    )
)
@pytest.mark.asyncio
async def test_reduce_mock_count(
    db_session: AsyncSession, mock_count: int, expected_value: int,
) -> None:
    test_rule = RuleModel(**RULE_DATA, mock_count=mock_count)
    db_session.add(test_rule)
    await db_session.commit()
    rule = await db_session.execute(select(RuleModel))
    rule: RuleModel = rule.scalars().first()

    await rule_crud.reduce_use_count(rule)

    await db_session.refresh(rule)
    assert rule.mock_count == expected_value


@pytest.mark.asyncio
async def test_delete_rule(db_session: AsyncSession) -> None:
    test_rule = RuleModel(**RULE_DATA)
    db_session.add(test_rule)
    await db_session.commit()
    rule = await db_session.execute(select(RuleModel))
    rule: RuleModel = rule.scalars().first()

    await rule_crud.delete_rule(rule.id)

    query_result: RuleModel = await db_session.execute(select(RuleModel))
    assert not query_result.first()


@pytest.mark.asyncio
async def test_search_rules_if_exist(db_session: AsyncSession) -> None:
    test_method = 'GET'
    test_url = 'test_url/api/.*/id'
    test_rule = RuleModel(
        method=test_method, url=test_url, call_backend=False, status_code=HTTPStatus.OK, response='test response'
    )
    db_session.add(test_rule)
    await db_session.commit()

    result = await rule_crud.search_rule(test_method, 'test_url/api/api_v1/id')

    assert result


@pytest.mark.asyncio
async def test_search_rules_if_not_exist(db_session: AsyncSession) -> None:
    test_method = 'GET'
    test_url = 'test_url/api/api_v1/id'
    test_rule = RuleModel(
        method=test_method, url=test_url, call_backend=False, status_code=HTTPStatus.OK, response='test response'
    )
    db_session.add(test_rule)
    await db_session.commit()

    result = await rule_crud.search_rule('NOT_EXIST', test_url)

    assert not result


@pytest.mark.asyncio
async def test_get_all_rules(db_session: AsyncSession) -> None:
    test_rule = RuleModel(**RULE_DATA)
    db_session.add(test_rule)
    await db_session.commit()

    result = await rule_crud.get_all_rules()

    assert len(result) == 1
