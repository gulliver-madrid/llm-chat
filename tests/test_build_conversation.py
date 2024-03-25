import unittest

from src.infrastructure.repository import (
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from src.models.shared import ChatMessage, ModelName, CompleteMessage, Model
from tests.objects import TEXT_1


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
        expected_conversation_text = TEXT_1
        result = create_conversation_texts(
            self.complete_messages, conversation_id, "2024-03-16 14:50:15"
        )
        self.assertEqual(expected_conversation_text, result)


if __name__ == "__main__":
    unittest.main()
