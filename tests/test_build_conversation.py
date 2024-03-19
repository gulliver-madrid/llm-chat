from dataclasses import dataclass
from typing import cast
import unittest
from src.infrastructure.client_wrapper import ChatMessage, CompleteMessage
from src.infrastructure.repository import (
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from src.models.model_choice import ModelName


@dataclass(frozen=True)
class CustomChatMessage:
    role: str
    content: str


def create_chat_msg(role: str, content: str) -> ChatMessage:
    return cast(ChatMessage, CustomChatMessage(role, content))


class TestCreateConversationTexts(unittest.TestCase):
    def setUp(self) -> None:
        self.complete_messages = [
            CompleteMessage(create_chat_msg("user", "Hello"), None),
            CompleteMessage(create_chat_msg("assistant", "Hi"), ModelName("model_1")),
            CompleteMessage(create_chat_msg("user", "How are you?"), None),
            CompleteMessage(
                create_chat_msg("assistant", "I'm fine."), ModelName("model_2")
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
