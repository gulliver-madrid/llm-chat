from collections.abc import Sequence
from dataclasses import dataclass

from src.models.shared import CompleteMessage, ConversationId


SCHEMA_VERSION = "0.2"


@dataclass(frozen=True)
class Conversation:
    id: ConversationId
    schema_version: str
    number_of_messages: int
    current_time: str
    messages: Sequence[CompleteMessage]
