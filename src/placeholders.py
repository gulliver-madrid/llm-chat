import re
from typing import Sequence


def find_placeholders(s: str) -> list[str]:
    return re.findall(r"(?<![a-zA-Z0-9])\$0[a-zA-Z_][a-zA-Z]*[0-9]*", s)


def replace_placeholders(
    question: str, substitutions: dict[str, str], for_placeholders: Sequence[str]
) -> list[str]:
    placeholder_with_for = for_placeholders[0]
    subs_in_for_str = substitutions[placeholder_with_for]
    subs_in_for_str = subs_in_for_str.removeprefix("/for")
    subs_in_for = subs_in_for_str.split(",")
    questions: list[str] = []
    for sub in subs_in_for:
        questions.append(question.replace(placeholder_with_for, sub))
    del substitutions[placeholder_with_for]
    new_questions: list[str] = []
    for question in questions:
        for placeholder, subs in substitutions.items():
            question = question.replace(placeholder, subs)
        new_questions.append(question)
    questions = new_questions
    return questions
