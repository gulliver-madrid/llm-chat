from src.models.parsed_line import ParsedLine, TagType
from src.infrastructure.repository import Repository
from src.models.shared import ChatMessage


def create_chat_msg(role: str, content: str) -> ChatMessage:
    return ChatMessage(role=role, content=content)


TEXT_FROM_FILE = """\
[META id=0001]

[META schema_version=0.2]
[META number_of_messages=4]
[META current_time=2024-03-16 14:50:15]

[ROLE USER]
Hello

[ROLE ASSISTANT model=model_1]
Hi

[ROLE USER]
How are you?

[ROLE ASSISTANT model=model_2]
I'm fine."""

expected_messages = [
    ChatMessage(role="user", content="Hello"),
    ChatMessage(role="assistant", content="Hi"),
    ChatMessage(role="user", content="How are you?"),
    ChatMessage(role="assistant", content="I'm fine."),
]


def test_load_conversation_from_text() -> None:
    repository = Repository()
    result = repository.convert_conversation_into_messages(TEXT_FROM_FILE)
    for complete_msg, expected_chat_msg in zip(result, expected_messages):
        assert complete_msg.chat_msg.role == expected_chat_msg.role
        assert complete_msg.chat_msg.content == expected_chat_msg.content


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
