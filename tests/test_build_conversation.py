import unittest

from src.models.serialization import (
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from tests.objects import COMPLETE_MESSAGES_1, TEXT_1


class TestCreateConversationTexts(unittest.TestCase):

    def test_create_conversation_texts(self) -> None:
        conversation_id = cast_string_to_conversation_id("0001")
        expected_conversation_text = TEXT_1
        result = create_conversation_texts(
            COMPLETE_MESSAGES_1, conversation_id, "2024-03-16 14:50:15"
        )
        self.assertEqual(expected_conversation_text, result)


if __name__ == "__main__":
    unittest.main()
