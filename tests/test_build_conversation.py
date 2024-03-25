import unittest

from src.infrastructure.repository import (
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from src.models.shared import ChatMessage, ModelName, CompleteMessage, Model


class TestCreateConversationTexts(unittest.TestCase):
    def setUp(self) -> None:
        self.complete_messages = [
            CompleteMessage(ChatMessage(role="user", content="Hello"), None),
            CompleteMessage(
                ChatMessage(role="assistant", content="Hi"),
                Model(None, ModelName("model_1")),
            ),
            CompleteMessage(ChatMessage(role="user", content="How are you?"), None),
            CompleteMessage(
                ChatMessage(role="assistant", content="I'm fine."),
                Model(None, ModelName("model_2")),
            ),
        ]

    def test_create_conversation_texts(self) -> None:
        conversation_id = cast_string_to_conversation_id("0001")
        expected_conversation_text = """\
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
        result = create_conversation_texts(
            self.complete_messages, conversation_id, "2024-03-16 14:50:15"
        )
        self.assertEqual(expected_conversation_text, result)


if __name__ == "__main__":
    unittest.main()
