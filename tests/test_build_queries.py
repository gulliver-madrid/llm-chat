import unittest
from typing import TypeGuard

from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    build_queries,
)


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


START_TO_END_RAW_query = "List numbers from {start} to {end}"
WHAT_IS_THE_CAPITAL_OF_FRANCE_query = "What is the capital of France?"


class TestBuildqueries(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_queries_no_placeholders(self) -> None:
        substitutions = as_substitutions({})
        expected = [WHAT_IS_THE_CAPITAL_OF_FRANCE_query]
        self.assertEqual(
            build_queries(WHAT_IS_THE_CAPITAL_OF_FRANCE_query, substitutions),
            expected,
        )

    def test_build_queries_with_placeholders(self) -> None:
        raw_query = "What is the capital of {country}?"
        substitutions = as_substitutions({"{country}": "France"})
        expected = [WHAT_IS_THE_CAPITAL_OF_FRANCE_query]
        self.assertEqual(build_queries(raw_query, substitutions), expected)

    def test_build_queries_with_for_command_with_one_element(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "5"})
        expected = ["List numbers from 1 to 5"]
        self.assertEqual(build_queries(START_TO_END_RAW_query, substitutions), expected)

    def test_build_queries_with_for_command_with_two_elements(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 10,20", "{end}": "50"})
        expected = ["List numbers from 10 to 50", "List numbers from 20 to 50"]
        self.assertEqual(build_queries(START_TO_END_RAW_query, substitutions), expected)

    def test_build_queries_multiple_for_not_supported(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "/for 5"})
        with self.assertRaises(QueryBuildException):
            build_queries(START_TO_END_RAW_query, substitutions)


if __name__ == "__main__":
    unittest.main()
