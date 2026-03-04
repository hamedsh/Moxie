from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.crud.rule as rule_crud
from api.deps import get_db
from api.schemas.rule import RuleResponseSchema, Rule, RuleStatusChange, RuleMockCountChange

api_management = APIRouter()


@api_management.post("/rule", response_model=RuleResponseSchema, status_code=HTTPStatus.CREATED)
async def add_rule(rule: Rule, db_session: AsyncSession = Depends(get_db)):
    rule = await rule_crud.create_rule(db_session, rule)
    return rule


@api_management.patch("/rule/{rule_id:int}/status", response_model=RuleResponseSchema, status_code=HTTPStatus.OK)
async def change_rule_status(rule_id: int, status: RuleStatusChange, db_session: AsyncSession = Depends(get_db)):
    await rule_crud.disable_rule(db_session, rule_id, status)
    return await rule_crud.get_rule_by_id(db_session, rule_id)


@api_management.patch("/rule/{rule_id:int}/mock_count", response_model=RuleResponseSchema, status_code=HTTPStatus.OK)
async def change_rule_mock_count(
        rule_id: int, mock_count: RuleMockCountChange, db_session: AsyncSession = Depends(get_db),
):
    return await rule_crud.set_rule_mock_count(db_session, rule_id, mock_count.mock_count)


@api_management.get("/rules", response_model=List[RuleResponseSchema], status_code=HTTPStatus.OK)
async def get_rules(db_session: AsyncSession = Depends(get_db)):
    return await rule_crud.get_all_rules(db_session)


@api_management.delete("/rule/{rule_id:int}", status_code=HTTPStatus.NO_CONTENT)
async def delete(rule_id: int, db_session: AsyncSession = Depends(get_db)):
    await rule_crud.delete_rule(db_session, rule_id)
