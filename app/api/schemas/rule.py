from enum import auto
from http import HTTPStatus
from typing import Dict, Any, List, Union

from pydantic import BaseModel
from strenum import StrEnum


class Methods(StrEnum):
    GET = auto()
    POST = auto()
    DELETE = auto()
    PUT = auto()
    PATCH = auto()


class Rule(BaseModel):
    description: str = None
    method: Methods = Methods.GET
    url: str = None
    call_backend: bool = False
    custom_headers: dict = None
    status_code: int = HTTPStatus.OK
    response: str = None
    enable: bool = True
    mock_count: int = -1
    response_delay: int = 0
    response_media_type: str = None


class RuleResponseSchema(Rule):
    id: int

    class Config:
        from_attributes = True


class RuleStatusChange(BaseModel):
    enable: bool = False


class RuleMockCountChange(BaseModel):
    mock_count: int


class JsonModel(BaseModel):
    root: Union[Dict[str, Any], List[Any]]
