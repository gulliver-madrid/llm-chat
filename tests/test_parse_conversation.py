from src.models.serde.serialize import (
    Conversation,
    deserialize_conversation_text_into_messages,
    convert_text_to_conversation_object,
    ConversationId,
)
from src.models.shared import ChatMessage
from tests.objects import COMPLETE_MESSAGES_1, COMPLETE_MESSAGES_2, TEXT_1, TEXT_2


def create_chat_msg(role: str, content: str) -> ChatMessage:
    return ChatMessage(role=role, content=content)


CASES = [
    (
        TEXT_1,
        Conversation(
            ConversationId("0001"), "0.2", 4, "2024-03-16 14:50:15", COMPLETE_MESSAGES_1
        ),
    ),
    (
        TEXT_2,
        Conversation(
            ConversationId("0002"), "0.2", 2, "2023-05-20 13:00:02", COMPLETE_MESSAGES_2
        ),
    ),
]


def test_parse_conversation_from_text() -> None:
    for text, expected_conversation in CASES:
        conversation = convert_text_to_conversation_object(
            text, preserve_model=True, check_model_exists=False
        )
        assert conversation == expected_conversation


def test_parse_messages_from_text() -> None:
    for text, messages in [
        (TEXT_1, COMPLETE_MESSAGES_1),
        (TEXT_2, COMPLETE_MESSAGES_2),
    ]:
        result = deserialize_conversation_text_into_messages(
            text, preserve_model=True, check_model_exists=False
        )
        assert result == messages
