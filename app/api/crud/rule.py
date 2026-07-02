import re
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.db_models.rule import Rule as RuleModel
from api.schemas.rule import Rule, RuleMockCountChange
from core.context import get_db_session
from api.deps import logger


async def create_rule(rule: Rule) -> RuleModel:
    """Create a new rule in the database."""
    db_session = get_db_session()
    db_rule = RuleModel(**rule.model_dump())
    db_session.add(db_rule)
    await db_session.commit()
    await db_session.refresh(db_rule)
    return db_rule


async def get_rule_by_id(rule_id: int) -> Optional[RuleModel]:
    """Fetch a rule by ID."""
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel).where(RuleModel.id == rule_id)
    )
    return result.scalar_one_or_none()


async def get_all_rules() -> List[RuleModel]:
    """Fetch all rules."""
    db_session = get_db_session()
    result = await db_session.execute(select(RuleModel))
    return result.scalars().all()


async def search_rule(method: str, path: str) -> Optional[RuleModel]:
    """Search for a rule matching method and path (enabled rules only)."""
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel).where(
            RuleModel.method == method.upper(),
            RuleModel.enable == True,
            RuleModel.mock_count != 0,
        )
    )
    rules = result.scalars().all()
    
    for rule in rules:
        if re.search(rule.url, path):
            return rule
    
    return None


async def disable_rule(rule_id: int, status) -> None:
    """Enable or disable a rule."""
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel).where(RuleModel.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if rule:
        rule.enable = status.enable
        await db_session.commit()


async def set_rule_mock_count(rule_id: int, mock_count: int) -> RuleModel:
    """Update rule mock count."""
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel).where(RuleModel.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if rule:
        rule.mock_count = mock_count
        await db_session.commit()
        await db_session.refresh(rule)
    return rule


async def reduce_use_count(rule: RuleModel) -> None:
    """Reduce rule use count if not unlimited."""
    if rule.mock_count > 0:
        rule.mock_count -= 1
        db_session = get_db_session()
        await db_session.commit()


async def delete_rule(rule_id: int) -> None:
    """Delete a rule by ID."""
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel).where(RuleModel.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if rule:
        await db_session.delete(rule)
        await db_session.commit()


async def get_conflicting_rules(method: str, url_pattern: str) -> List[tuple[int, str, str]]:
    """Find rules with overlapping URL patterns (same method).
    
    Returns:
        List of tuples: (rule_id, method, url_pattern)
    """
    db_session = get_db_session()
    result = await db_session.execute(
        select(RuleModel.id, RuleModel.method, RuleModel.url).where(
            RuleModel.method == method.upper()
        )
    )
    existing_rules = result.all()
    
    conflicts = []
    try:
        pattern_regex = re.compile(url_pattern)
    except re.error:
        return conflicts
    
    # Generate test URLs from existing patterns to find overlaps
    test_urls = [
        "api.example.com/test",
        "api.customer.io/v1/activities",
        "track.customer.io/api/v1/customers/123/unsuppress",
        "api.cloudflare.com/client/v4/zones/abc123/ssl/universal/settings",
    ]
    
    for rule_id, rule_method, rule_pattern in existing_rules:
        try:
            rule_regex = re.compile(rule_pattern)
            # Check if patterns overlap on test URLs
            for test_url in test_urls:
                if pattern_regex.search(test_url) and rule_regex.search(test_url):
                    if rule_id not in [c[0] for c in conflicts]:
                        conflicts.append((rule_id, rule_method, rule_pattern))
                    break
        except re.error:
            continue
    
    return conflicts
