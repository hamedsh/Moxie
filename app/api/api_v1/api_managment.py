from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException

import api.crud.rule as rule_crud
from api.schemas.rule import (
    RuleResponseSchema,
    Rule,
    RuleStatusChange,
    RuleMockCountChange,
    RuleTestPayload,
    RuleTestResponse,
    RuleConflictReport,
    RuleExport,
)
from api.deps import logger

api_management = APIRouter()


@api_management.post(
    "/rule",
    response_model=RuleResponseSchema,
    status_code=HTTPStatus.CREATED,
    summary="Create a new rule",
    description="Create a new rule for intercepting and manipulating API requests.",
)
async def add_rule(rule: Rule):
    """Create a new rule.
    
    Args:
        rule: Rule configuration
        
    Returns:
        RuleResponseSchema: Created rule with ID and timestamps
        
    Raises:
        HTTPException: 400 if rule validation fails
    """
    try:
        conflicts = await rule_crud.get_conflicting_rules(rule.method, rule.url)
        if conflicts:
            logger.warning(
                f"New rule may conflict with {len(conflicts)} existing rule(s)"
            )
        created_rule = await rule_crud.create_rule(rule)
        return created_rule
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))


@api_management.post(
    "/rule/test",
    response_model=RuleTestResponse,
    status_code=HTTPStatus.OK,
    summary="Test rule regex matching",
    description="Test a URL pattern against a sample URL to verify regex matching without saving.",
)
async def test_rule(payload: RuleTestPayload):
    """Test rule regex matching.
    
    Args:
        payload: Method, URL pattern, and test URL
        
    Returns:
        RuleTestResponse: Whether the pattern matches and explanation
    """
    import re
    
    try:
        pattern = re.compile(payload.url_pattern)
        matches = bool(pattern.search(payload.test_url))
        
        message = (
            f"Pattern '{payload.url_pattern}' matches '{payload.test_url}'"
            if matches
            else f"Pattern '{payload.url_pattern}' does NOT match '{payload.test_url}'"
        )
        
        return RuleTestResponse(
            method=payload.method,
            url_pattern=payload.url_pattern,
            test_url=payload.test_url,
            matches=matches,
            message=message,
        )
    except re.error as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid regex pattern: {e}",
        )


@api_management.post(
    "/rule/check-conflicts",
    response_model=List[RuleConflictReport],
    status_code=HTTPStatus.OK,
    summary="Check for conflicting rules",
    description="Check if a new rule would conflict with existing rules.",
)
async def check_rule_conflicts(rule: Rule):
    """Check for conflicting rules.
    
    Args:
        rule: Rule to check for conflicts
        
    Returns:
        List[RuleConflictReport]: List of conflicting rules
    """
    conflicts = await rule_crud.get_conflicting_rules(rule.method, rule.url)
    
    reports = [
        RuleConflictReport(
            rule_id=conflict[0],
            method=conflict[1],
            url_pattern=conflict[2],
            conflicting_rule_ids=[conflict[0]],
            conflict_severity="warning",
            message=f"Rule {conflict[0]} has overlapping pattern: {conflict[2]}",
        )
        for conflict in conflicts
    ]
    
    return reports


@api_management.patch(
    "/rule/{rule_id:int}/status",
    response_model=RuleResponseSchema,
    status_code=HTTPStatus.OK,
    summary="Enable or disable a rule",
)
async def change_rule_status(rule_id: int, status: RuleStatusChange):
    """Enable or disable a rule.
    
    Args:
        rule_id: ID of the rule
        status: Enable/disable flag
        
    Returns:
        RuleResponseSchema: Updated rule
        
    Raises:
        HTTPException: 404 if rule not found
    """
    if rule_id <= 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Rule ID must be positive",
        )
    
    await rule_crud.disable_rule(rule_id, status)
    rule = await rule_crud.get_rule_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Rule {rule_id} not found",
        )
    
    return rule


@api_management.patch(
    "/rule/{rule_id:int}/mock_count",
    response_model=RuleResponseSchema,
    status_code=HTTPStatus.OK,
    summary="Update rule mock count",
)
async def change_rule_mock_count(rule_id: int, mock_count: RuleMockCountChange):
    """Update rule mock count.
    
    Args:
        rule_id: ID of the rule
        mock_count: New mock count
        
    Returns:
        RuleResponseSchema: Updated rule
        
    Raises:
        HTTPException: 404 if rule not found
    """
    if rule_id <= 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Rule ID must be positive",
        )
    
    rule = await rule_crud.set_rule_mock_count(rule_id, mock_count.mock_count)
    
    if not rule:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Rule {rule_id} not found",
        )
    
    return rule


@api_management.get(
    "/rules",
    response_model=List[RuleResponseSchema],
    status_code=HTTPStatus.OK,
    summary="List all rules",
    description="Retrieve all configured rules.",
)
async def get_rules():
    """Get all rules.
    
    Returns:
        List[RuleResponseSchema]: All rules in the system
    """
    return await rule_crud.get_all_rules()


@api_management.post(
    "/rules/export",
    response_model=RuleExport,
    status_code=HTTPStatus.OK,
    summary="Export all rules",
    description="Export all current rules as JSON for backup or sharing.",
)
async def export_rules():
    """Export all rules.
    
    Returns:
        RuleExport: Export object with all rules and metadata
    """
    rules = await rule_crud.get_all_rules()
    
    return RuleExport(
        version="1.0",
        rules=[Rule(**{k: v for k, v in rule.__dict__.items() if not k.startswith('_')}) for rule in rules],
        metadata={"rule_count": len(rules)},
    )


@api_management.post(
    "/rules/import",
    response_model=dict,
    status_code=HTTPStatus.CREATED,
    summary="Import rules from export",
    description="Import multiple rules from a JSON export file. Existing rules are not affected.",
)
async def import_rules(export: RuleExport):
    """Import rules from export.
    
    Args:
        export: RuleExport object with rules to import
        
    Returns:
        dict: Import result with count and details
        
    Raises:
        HTTPException: 400 if import validation fails
    """
    imported_count = 0
    failed = []
    
    for rule in export.rules:
        try:
            await rule_crud.create_rule(rule)
            imported_count += 1
        except Exception as e:
            failed.append({"rule": rule.url, "error": str(e)})
            logger.error(f"Failed to import rule {rule.url}: {e}")
    
    return {
        "imported": imported_count,
        "failed": len(failed),
        "failed_details": failed,
    }


@api_management.delete(
    "/rule/{rule_id:int}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete a rule",
)
async def delete(rule_id: int):
    """Delete a rule by ID.
    
    Args:
        rule_id: ID of the rule to delete
        
    Raises:
        HTTPException: 400 if rule_id is invalid, 404 if not found
    """
    if rule_id <= 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Rule ID must be positive",
        )
    
    rule = await rule_crud.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Rule {rule_id} not found",
        )
    
    await rule_crud.delete_rule(rule_id)
