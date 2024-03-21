from dataclasses import dataclass

from src.models.placeholders import find_unique_placeholders


@dataclass(frozen=True)
class Case:
    expected: list[str]
    text: str


cases = [
    Case(expected=[], text="there is not placeholders here"),
    Case(expected=["$0placeholder"], text="there is a placeholder here: $0placeholder"),
    Case(
        expected=["$0placeholder"],
        text="there is a unique placeholder here: $0placeholder and $0placeholder",
    ),
    Case(
        expected=["$0placeholder_1", "$0placeholder_2"],
        text="there are two placeholders here: $0placeholder_1 and $0placeholder_2",
    ),
    Case(
        expected=["$0placeholder_1"],
        text="a placeholder followed by a comma: $0placeholder_1, and...",
    ),
    Case(
        expected=[],
        text="this is not a valid placeholder: $0placeholder10more_text_after_the_digits",
    ),
]


def test_find_placeholders() -> None:
    for case in cases:
        result = find_unique_placeholders(case.text)
        assert (
            case.expected == result
        ), f"""

En la cadena:
\t{case.text!r}

Deberían haberse encontrado:
\t{case.expected}

Pero se encontraron:
\t{result}
"""
