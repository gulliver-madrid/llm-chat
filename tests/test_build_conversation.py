import unittest

from src.models.serialization import (
    ConversationId,
    convert_digits_to_conversation_id,
    create_conversation_texts,
)
from tests.objects import COMPLETE_MESSAGES_1, TEXT_1


class TestCreateConversationTexts(unittest.TestCase):

    def test_create_conversation_texts(self) -> None:
        expected_conversation_text = TEXT_1
        result = create_conversation_texts(
            COMPLETE_MESSAGES_1, ConversationId("0001"), "2024-03-16 14:50:15"
        )
        self.assertEqual(expected_conversation_text, result)

    def test_convert_digits_to_conversation_id(self) -> None:
        conversation_id = convert_digits_to_conversation_id("1")
        self.assertEqual(ConversationId("0001"), conversation_id)

    def test_convert_digits_to_conversation_id_wrong(self) -> None:
        """Too much digits"""
        with self.assertRaises(ValueError):
            convert_digits_to_conversation_id("11111")


if __name__ == "__main__":
    unittest.main()
