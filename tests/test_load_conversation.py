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


def test_load_conversation_from_text_1() -> None:
    conversation = convert_text_to_conversation_object(
        TEXT_1, preserve_model=True, check_model_exists=False
    )
    expected_messages = COMPLETE_MESSAGES_1
    expected = Conversation(
        ConversationId("0001"), "0.2", 4, "2024-03-16 14:50:15", expected_messages
    )
    assert conversation == expected


def test_load_conversation_from_text_2() -> None:
    conversation = convert_text_to_conversation_object(
        TEXT_2, preserve_model=True, check_model_exists=False
    )
    expected_messages = COMPLETE_MESSAGES_2
    expected = Conversation(
        ConversationId("0002"), "0.2", 2, "2023-05-20 13:00:02", expected_messages
    )
    assert conversation == expected


def test_load_messages_from_text_1() -> None:
    result = convert_conversation_into_messages(
        TEXT_1, preserve_model=True, check_model_exists=False
    )
    assert result == COMPLETE_MESSAGES_1


def test_load_messages_from_text_2() -> None:
    result = convert_conversation_into_messages(
        TEXT_2, preserve_model=True, check_model_exists=False
    )
    assert result == COMPLETE_MESSAGES_2


def test_is_tag() -> None:
    # no tags
    assert_is_tag(False, "")
    # something before
    assert_is_tag(False, " [META id=0001]")
    # something after
    assert_is_tag(False, "[META id=0001] ")
    # missing space
    assert_is_tag(False, "[METAid]")

    # tags
    assert_is_tag(True, "[META id=0001]")
    assert_is_tag(True, "[ROLE ASSISTANT model=model_1]")


def test_get_tag_type() -> None:
    # no tags
    assert_tag_type(None, "")
    # something before
    assert_tag_type(None, " [META id=0001]")
    # something after
    assert_tag_type(None, "[META id=0001] ")
    # missing space
    assert_tag_type(None, "[METAid]")

    # tags
    assert_tag_type(TagType.META, "[META id=0001]")
    assert_tag_type(TagType.ROLE, "[ROLE ASSISTANT model=model_1]")


def assert_is_tag(expected: bool, string: str) -> None:
    assert expected == ParsedLine(string).is_tag()


def assert_tag_type(expected: TagType | None, string: str) -> None:
    assert expected == ParsedLine(string).get_tag_type()
