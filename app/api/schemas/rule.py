from typing import Optional, List, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator
import re


class RuleStatusEnum(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class JsonModel(BaseModel):
    pass


class Rule(BaseModel):
    """Rule model for API request/response manipulation.
    
    Attributes:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        url: URL pattern as regex (e.g., 'api.customer.io/v1/activities')
        call_backend: Whether to still call the destination or mock
        status_code: HTTP status code to return
        response: Response body as string
        enable: Whether this rule is active
        mock_count: How many times to apply (>0: count, -1: unlimited, 0: never)
        response_delay: Delay in seconds before returning response
        response_media_type: Content-Type for response (e.g., 'application/json')
        custom_headers: Custom headers to add to requests
    """
    method: str = Field(..., description="HTTP method: GET, POST, PUT, PATCH, DELETE")
    url: str = Field(..., description="URL pattern as regex (without http:// or https://)")
    call_backend: bool = Field(default=False, description="Whether to call the actual backend")
    status_code: int = Field(default=200, ge=100, le=599, description="HTTP status code")
    response: str = Field(default="{}", description="Response body")
    enable: bool = Field(default=True, description="Whether rule is enabled")
    mock_count: int = Field(default=-1, description="Execution count (-1: unlimited, 0: never, >0: specific count)")
    response_delay: int = Field(default=0, ge=0, description="Delay in seconds")
    response_media_type: str = Field(default="application/json", description="Content-Type header")
    custom_headers: dict[str, str] = Field(default_factory=dict, description="Custom headers to add")

    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method."""
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if v.upper() not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")
        return v.upper()

    @field_validator('url')
    @classmethod
    def validate_url_regex(cls, v: str) -> str:
        """Validate URL is valid regex."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @field_validator('mock_count')
    @classmethod
    def validate_mock_count(cls, v: int) -> int:
        """Validate mock_count is valid."""
        if v == 0 or v < -1:
            raise ValueError("mock_count must be -1 (unlimited), or > 0")
        return v


class RuleResponseSchema(Rule):
    """Rule response schema with database metadata."""
    id: int = Field(..., description="Unique rule ID")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True


class RuleStatusChange(BaseModel):
    """Payload for enabling/disabling rules."""
    enable: bool = Field(..., description="Enable or disable the rule")


class RuleMockCountChange(BaseModel):
    """Payload for updating rule mock count."""
    mock_count: int = Field(..., description="New mock count (-1 for unlimited)")

    @field_validator('mock_count')
    @classmethod
    def validate_mock_count(cls, v: int) -> int:
        if v == 0 or v < -1:
            raise ValueError("mock_count must be -1 (unlimited), or > 0")
        return v


class RuleTestPayload(BaseModel):
    """Payload for testing rule regex matching."""
    method: str = Field(..., description="HTTP method to test")
    url_pattern: str = Field(..., description="URL pattern (regex) to test")
    test_url: str = Field(..., description="Sample URL to test against pattern")

    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if v.upper() not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")
        return v.upper()

    @field_validator('url_pattern')
    @classmethod
    def validate_url_regex(cls, v: str) -> str:
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class RuleTestResponse(BaseModel):
    """Response from rule testing."""
    method: str
    url_pattern: str
    test_url: str
    matches: bool = Field(..., description="Whether the pattern matches the test URL")
    message: str = Field(..., description="Human-readable explanation")


class RuleConflictReport(BaseModel):
    """Report of conflicting rules."""
    rule_id: int
    method: str
    url_pattern: str
    conflicting_rule_ids: list[int] = Field(default_factory=list)
    conflict_severity: str = Field(..., description="'warning' or 'error'")
    message: str


class RuleExport(BaseModel):
    """Export format for rules (batch import/export)."""
    version: str = Field(default="1.0", description="Export format version")
    rules: List[Rule] = Field(..., description="List of rules to export")
    metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional metadata (timestamp, exported_by, etc.)"
    )
