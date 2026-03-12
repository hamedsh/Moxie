from typing import Union, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, or_, and_, func, text
from sqlalchemy.sql.operators import is_not

from api.db_models.models import RuleModel
from api.deps import logger
from api.schemas.rule import Rule, RuleStatusChange
from core.context import get_db_session


async def create_rule(rule: Rule) -> RuleModel:
    db_session = get_db_session()
    if rule.url.startswith('/'):
        rule.url = rule.url[1:]
    item_in_data = jsonable_encoder(rule)
    item: RuleModel = RuleModel(**item_in_data)
    db_session.add(item)
    try:
        await db_session.commit()
    except Exception as ex:  # pylint: disable=broad-except
        logger.error('error while creating rule: %s', ex)
        await db_session.rollback()
        raise ex
    await db_session.refresh(item)
    return item


async def execute_raw_query(query: str) -> Any:
    session = get_db_session()
    query_executer = await session.execute(text(query))
    return query_executer.scalars().first()


async def get_rule_by_id(rule_id: int) -> RuleModel:
    session = get_db_session()
    query_executer = await session.execute(select(RuleModel).where(RuleModel.id == rule_id))
    return query_executer.scalars().first()


async def disable_rule(rule_id: int, status: RuleStatusChange) -> RuleModel:
    session = get_db_session()
    query: RuleModel = select(RuleModel).where(RuleModel.id == rule_id)
    query_result: RuleModel = await session.execute(query)
    db_rule = query_result.scalar()
    db_rule.enable = status.enable
    await session.commit()
    await session.refresh(db_rule)
    return db_rule


async def delete_rule(rule_id: int) -> None:
    session = get_db_session()
    query: RuleModel = delete(RuleModel).where(RuleModel.id == rule_id)
    await session.execute(query)
    await session.commit()


async def reduce_use_count(rule: RuleModel) -> None:
    session = get_db_session()
    await session.refresh(rule)
    logger.debug('set rule usage. id: %s, current mock_count: %s', rule.id, rule.mock_count)
    if rule.mock_count in (-1, 0):
        return
    if rule.mock_count > 0:
        rule.mock_count -= 1
    await session.commit()
    await session.refresh(rule)
    logger.debug('set rule usage. id: %s, new mock_count: %s', rule.id, rule.mock_count)


async def search_rule(method: str, url: str) -> Union[RuleModel, None]:
    session = get_db_session()
    logger.debug('search rule, method: %s, url: %s', method, url)
    query = select(RuleModel).filter(and_(
        RuleModel.enable.is_(True),
        RuleModel.method == method,
        is_not(func.regexp_match(url, RuleModel.url), None),
        or_(RuleModel.mock_count == -1, RuleModel.mock_count > 0),
    ))
    query_result = await session.execute(query)
    return query_result.scalars().first()


async def get_all_rules() -> list[RuleModel]:
    session = get_db_session()
    query = select(RuleModel)
    query_result = await session.execute(query)
    return query_result.scalars().all()


async def set_rule_mock_count(rule_id: int, new_value: int) -> RuleModel:
    session = get_db_session()
    query: RuleModel = select(RuleModel).where(RuleModel.id == rule_id)
    query_result: RuleModel = await session.execute(query)
    db_rule: RuleModel = query_result.scalar()
    db_rule.mock_count = new_value
    await session.commit()
    await session.refresh(db_rule)
    return db_rule
