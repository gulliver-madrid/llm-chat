import unittest
from src.infrastructure.client_wrapper import ChatMessage
from src.models.parsed_line import ParsedLine, TagType
from src.infrastructure.repository import ChatRepository


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


class TestLoadConversation(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_load_conversation_from_text(self) -> None:
        repository = ChatRepository()
        result = repository.load_conversation_from_text(TEXT_FROM_FILE)
        for complete_msg, expected_chat_msg in zip(result, expected_messages):
            self.assertEqual(complete_msg.chat_msg.role, expected_chat_msg.role)
            self.assertEqual(complete_msg.chat_msg.content, expected_chat_msg.content)

    def test_is_tag(self) -> None:
        # no tags
        self.assert_is_tag(False, "")
        # something before
        self.assert_is_tag(False, " [META id=0001]")
        # something after
        self.assert_is_tag(False, "[META id=0001] ")
        # missing space
        self.assert_is_tag(False, "[METAid]")

        # tags
        self.assert_is_tag(True, "[META id=0001]")
        self.assert_is_tag(True, "[ROLE ASSISTANT model=model_1]")

    def test_get_tag_type(self) -> None:
        # no tags
        self.assert_tag_type(None, "")
        # something before
        self.assert_tag_type(None, " [META id=0001]")
        # something after
        self.assert_tag_type(None, "[META id=0001] ")
        # missing space
        self.assert_tag_type(None, "[METAid]")

        # tags
        self.assert_tag_type(TagType.META, "[META id=0001]")
        self.assert_tag_type(TagType.ROLE, "[ROLE ASSISTANT model=model_1]")

    def assert_is_tag(self, expected: bool, string: str) -> None:
        self.assertEqual(expected, ParsedLine(string).is_tag())

    def assert_tag_type(self, expected: TagType | None, string: str) -> None:
        self.assertEqual(expected, ParsedLine(string).get_tag_type())


if __name__ == "__main__":
    unittest.main()
