import unittest
from src.main import build_questions


class TestBuildQuestions(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_questions_no_placeholders(self) -> None:
        raw_question = "What is the capital of France?"
        substitutions: dict[str, str] = {}
        expected = [raw_question]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_with_placeholders(self) -> None:
        raw_question = "What is the capital of {country}?"
        substitutions = {"{country}": "France"}
        expected = ["What is the capital of France?"]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_with_for_command(self) -> None:
        raw_question = "List numbers from {start} to {end}"
        substitutions = {"{start}": "/for 1", "{end}": "5"}
        expected = ["List numbers from 1 to 5"]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_multiple_for_not_supported(self) -> None:
        raw_question = "List numbers from {start} to {end}"
        substitutions = {"{start}": "/for 1", "{end}": "/for 5"}
        self.assertIsNone(build_questions(raw_question, substitutions))


if __name__ == "__main__":
    unittest.main()
