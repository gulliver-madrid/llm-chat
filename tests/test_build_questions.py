from typing import cast
import unittest
from src.main import build_questions
from src.placeholders import Placeholder


def as_substitution_dict(d: dict[str, str]) -> dict[Placeholder, str]:
    assert isinstance(d, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in d.items())
    return cast(dict[Placeholder, str], d)


class TestBuildQuestions(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_questions_no_placeholders(self) -> None:
        raw_question = "What is the capital of France?"
        substitutions = as_substitution_dict({})
        expected = [raw_question]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_with_placeholders(self) -> None:
        raw_question = "What is the capital of {country}?"
        substitutions = as_substitution_dict({"{country}": "France"})
        expected = ["What is the capital of France?"]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_with_for_command(self) -> None:
        raw_question = "List numbers from {start} to {end}"
        substitutions = as_substitution_dict({"{start}": "/for 1", "{end}": "5"})
        expected = ["List numbers from 1 to 5"]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_multiple_for_not_supported(self) -> None:
        raw_question = "List numbers from {start} to {end}"
        substitutions = as_substitution_dict({"{start}": "/for 1", "{end}": "/for 5"})
        self.assertIsNone(build_questions(raw_question, substitutions))


if __name__ == "__main__":
    unittest.main()
