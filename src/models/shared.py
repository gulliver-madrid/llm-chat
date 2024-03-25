from dataclasses import dataclass
from enum import Enum
from typing import NewType

__all__ = ["ModelName", "Model", "ChatMessage", "CompleteMessage"]

ModelName = NewType("ModelName", str)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


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
