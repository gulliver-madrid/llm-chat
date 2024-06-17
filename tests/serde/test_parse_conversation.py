from src.domain import ChatMessage
from src.models.shared import (
    ConversationId,
    ConversationText,
    SchemaVersionId,
)
from src.serde import (
    deserialize_conversation_text_into_messages,
    Conversation,
)
from src.serde.deserialize import deserialize_into_conversation_object

from tests.objects import COMPLETE_MESSAGES_1, COMPLETE_MESSAGES_2, TEXT_1, TEXT_2


def create_chat_msg(role: str, content: str) -> ChatMessage:
    return ChatMessage(role=role, content=content)


SCHEMA_VERSION = SchemaVersionId("0.2")
CASES = [
    (
        TEXT_1,
        Conversation(
            ConversationId("0001"),
            SCHEMA_VERSION,
            4,
            "2024-03-16 14:50:15",
            COMPLETE_MESSAGES_1,
        ),
    ),
    (
        TEXT_2,
        Conversation(
            ConversationId("0002"),
            SCHEMA_VERSION,
            2,
            "2023-05-20 13:00:02",
            COMPLETE_MESSAGES_2,
        ),
    ),
]


def test_deserialize_conversation() -> None:
    for text, expected_conversation in CASES:
        conversation = deserialize_into_conversation_object(
            ConversationText(text, SCHEMA_VERSION),
            preserve_model=True,
            check_model_exists=False,
        )
        assert conversation == expected_conversation


def test_deserialize_messages() -> None:
    for text, messages in [
        (TEXT_1, COMPLETE_MESSAGES_1),
        (TEXT_2, COMPLETE_MESSAGES_2),
    ]:
        result = deserialize_conversation_text_into_messages(
            ConversationText(text, SCHEMA_VERSION),
            preserve_model=True,
            check_model_exists=False,
        )
        assert result == messages
