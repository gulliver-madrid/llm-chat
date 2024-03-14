import re
from typing import Mapping, NewType

Placeholder = NewType("Placeholder", str)

FOR_COMMAND_PREFFIX = "/for"


def find_placeholders(s: str) -> list[Placeholder]:
    """
    Finds all placeholders in a given string.

    Args:
        s: The string to search for placeholders.

    Returns:
        A list of placeholders found in the string.
    """
    return re.findall(r"(?<![a-zA-Z0-9])\$0[a-zA-Z_][a-zA-Z]*[0-9]*", s)


def replace_placeholders_with_one_for(
    question: str,
    substitutions: Mapping[Placeholder, str],
    placeholder_with_for: Placeholder,
) -> list[str]:
    replacements_in_for_str = substitutions[placeholder_with_for]
    assert replacements_in_for_str.startswith(FOR_COMMAND_PREFFIX)
    replacements_in_for_str = replacements_in_for_str.removeprefix(
        FOR_COMMAND_PREFFIX
    ).strip()

    replacements_in_for = replacements_in_for_str.split(",")
    questions: list[str] = []
    for replacement in replacements_in_for:
        questions.append(question.replace(placeholder_with_for, replacement))
    substitutions = {
        placeholder: value
        for placeholder, value in substitutions.items()
        if placeholder != placeholder_with_for
    }
    new_questions: list[str] = []
    for question in questions:
        new_questions.append(
            replace_question_with_substitutions(question, substitutions)
        )
    questions = new_questions
    return questions


def replace_question_with_substitutions(
    question: str, substitutions: Mapping[Placeholder, str]
) -> str:
    for placeholder, replacement in substitutions.items():
        question = question.replace(placeholder, replacement)
    return question


def get_placeholders_with_for(
    substitutions: Mapping[Placeholder, str]
) -> list[Placeholder]:
    """
    Identifies placeholders that are associated with a 'for' command in the substitutions.

    Args:
        substitutions: A mapping of placeholders to their substitutions.

    Returns:
        A list of placeholders that have a 'for' command as their substitution.
    """
    return [
        placeholder
        for placeholder, subs in substitutions.items()
        if subs.startswith(FOR_COMMAND_PREFFIX)
    ]
