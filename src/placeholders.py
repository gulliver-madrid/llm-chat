import re
from typing import NewType, Sequence

Placeholder = NewType("Placeholder", str)

FOR_COMMAND_PREFFIX = "/for"


def find_placeholders(s: str) -> list[Placeholder]:
    return re.findall(r"(?<![a-zA-Z0-9])\$0[a-zA-Z_][a-zA-Z]*[0-9]*", s)


def replace_placeholders_including_for(
    question: str,
    substitutions: dict[Placeholder, str],
    placeholders_with_for: Sequence[Placeholder],
) -> list[str]:
    placeholder_with_for = placeholders_with_for[0]
    replacements_in_for_str = substitutions[placeholder_with_for]
    assert replacements_in_for_str.startswith(FOR_COMMAND_PREFFIX)
    replacements_in_for_str = replacements_in_for_str.removeprefix(
        FOR_COMMAND_PREFFIX
    ).strip()

    replacements_in_for = replacements_in_for_str.split(",")
    questions: list[str] = []
    for sub in replacements_in_for:
        questions.append(question.replace(placeholder_with_for, sub))
    del substitutions[placeholder_with_for]
    new_questions: list[str] = []
    for question in questions:
        for placeholder, subs in substitutions.items():
            question = question.replace(placeholder, subs)
        new_questions.append(question)
    questions = new_questions
    return questions
