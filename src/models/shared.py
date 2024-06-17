from dataclasses import dataclass, field
from enum import Enum
from typing import NewType, Sequence


__all__ = ["ModelName", "Model", "ChatMessage", "CompleteMessage"]

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


def extract_chat_messages(
    complete_messages: Sequence[CompleteMessage],
) -> list[ChatMessage]:
    return [complete_chat.chat_msg for complete_chat in complete_messages]


def define_system_prompt(prompt: str, *, use_system: bool = True) -> CompleteMessage:
    return CompleteMessage(
        chat_msg=ChatMessage("system" if use_system else "user", prompt)
    )


@dataclass
class ConversationText:
    text: str
    schema_version: SchemaVersionId
