from typing import TypeGuard
import unittest
from src.main import build_questions
from src.models.placeholders import Placeholder


def as_substitutions(d: dict[str, str]) -> dict[Placeholder, str]:
    assert isinstance(d, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in d.items())
    assert is_substitutions_dict(d)
    return d


def is_substitutions_dict(
    d: dict[str, str], is_test: bool = True
) -> TypeGuard[dict[Placeholder, str]]:
    preffix = "{" if is_test else "$0"
    return all(placeholder.startswith(preffix) for placeholder in d)


START_TO_END_RAW_QUESTION = "List numbers from {start} to {end}"
WHAT_IS_THE_CAPITAL_OF_FRANCE_QUESTION = "What is the capital of France?"


class TestBuildQuestions(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_questions_no_placeholders(self) -> None:
        substitutions = as_substitutions({})
        expected = [WHAT_IS_THE_CAPITAL_OF_FRANCE_QUESTION]
        self.assertEqual(
            build_questions(WHAT_IS_THE_CAPITAL_OF_FRANCE_QUESTION, substitutions),
            expected,
        )

    def test_build_questions_with_placeholders(self) -> None:
        raw_question = "What is the capital of {country}?"
        substitutions = as_substitutions({"{country}": "France"})
        expected = [WHAT_IS_THE_CAPITAL_OF_FRANCE_QUESTION]
        self.assertEqual(build_questions(raw_question, substitutions), expected)

    def test_build_questions_with_for_command_with_one_element(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "5"})
        expected = ["List numbers from 1 to 5"]
        self.assertEqual(
            build_questions(START_TO_END_RAW_QUESTION, substitutions), expected
        )

    def test_build_questions_with_for_command_with_two_elements(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 10,20", "{end}": "50"})
        expected = ["List numbers from 10 to 50", "List numbers from 20 to 50"]
        self.assertEqual(
            build_questions(START_TO_END_RAW_QUESTION, substitutions), expected
        )

    def test_build_questions_multiple_for_not_supported(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "/for 5"})
        self.assertIsNone(build_questions(START_TO_END_RAW_QUESTION, substitutions))


if __name__ == "__main__":
    unittest.main()
