from dataclasses import dataclass, field
from typing import TypedDict, TypeGuard

from src.infrastructure.exceptions import LLMChatException

from .types import is_object_mapping


class WrongFunctionName(LLMChatException):
    def __init__(self, function_name: str):
        super().__init__(function_name)


class FunctionCallDict(TypedDict):
    """Represents a dictionary with a function call as loaded from JSON"""

    name: str
    arguments: object


def is_function_call_mapping(obj: object) -> TypeGuard[FunctionCallDict]:
    if not is_object_mapping(obj):
        return False
    for key in ("name", "arguments"):
        if not key in obj:
            return False
    if not isinstance(obj["name"], str):
        return False
    return True


@dataclass(frozen=True)
class FunctionCall:
    """Object with the same format as the 'function' member of the ToolCall object received from the Mistral API"""

    name: str
    arguments: str


@dataclass(frozen=True)
class ToolCall:
    """Object with the same format as the original received from the Mistral API"""

    function: FunctionCall
    id: str | None = field(kw_only=True, default=None)
