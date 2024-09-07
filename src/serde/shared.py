from collections.abc import Sequence
from dataclasses import dataclass

from src.domain import CompleteMessage, ConversationId, SchemaVersionId

SCHEMA_VERSION = SchemaVersionId("0.2")


@dataclass(frozen=True)
class Conversation:
    id: ConversationId
    schema_version: SchemaVersionId
    number_of_messages: int
    current_time: str
    messages: Sequence[CompleteMessage]
