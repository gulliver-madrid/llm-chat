from src.models.parsed_line import ParsedLine, TagType
from src.models.serialization import (
    Conversation,
    convert_conversation_into_messages,
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
        result = convert_conversation_into_messages(
            text, preserve_model=True, check_model_exists=False
        )
        assert result == messages


NO_TAGS = [
    "",
    # something before
    " [META id=0001]",
    # something after
    "[META id=0001] ",
    # missing space
    "[METAid]",
]
TAGS_WITH_TYPES = [
    ("[META id=0001]", TagType.META),
    ("[ROLE ASSISTANT model=model_1]", TagType.ROLE),
]


def test_is_tag() -> None:
    for no_tag in NO_TAGS:
        assert_is_tag(False, no_tag)

    for tag, _ in TAGS_WITH_TYPES:
        assert_is_tag(True, tag)


def test_get_tag_type() -> None:
    for no_tag in NO_TAGS:
        assert_tag_type(None, no_tag)

    for tag, expected_type in TAGS_WITH_TYPES:
        assert_tag_type(expected_type, tag)


def assert_is_tag(expected: bool, string: str) -> None:
    assert expected == ParsedLine(string).is_tag()


def assert_tag_type(expected: TagType | None, string: str) -> None:
    assert expected == ParsedLine(string).get_tag_type()
