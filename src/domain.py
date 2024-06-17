from dataclasses import dataclass, field
from enum import Enum
from typing import NewType

ConversationId = NewType("ConversationId", str)
ModelName = NewType("ModelName", str)
SchemaVersionId = NewType("SchemaVersionId", str)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    name: str | None = field(kw_only=True, default=None)
    tool_calls: object = field(kw_only=True, default=None)
    tool_call_id: str | None = field(kw_only=True, default=None)


class Platform(Enum):
    Mistral = "Mistral"
    OpenAI = "OpenAI"


@dataclass(frozen=True)
class Model:
    platform: Platform | None
    model_name: ModelName


@dataclass(frozen=True)
class CompleteMessage:
    chat_msg: ChatMessage
    model: Model | None = None


@dataclass
class ConversationText:
    text: str
    schema_version: SchemaVersionId
