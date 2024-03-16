import re
from typing import Mapping, NewType

Placeholder = NewType("Placeholder", str)

FOR_COMMAND_PREFFIX = "/for"


class QueryBuildException(Exception): ...


def build_questions(
    raw_question: str, substitutions: Mapping[Placeholder, str]
) -> list[str]:
    """
    Constructs a list of questions by replacing placeholders in the raw question with user-provided substitutions.
    If a 'for' command is detected, it generates multiple questions by iterating over the specified range.

    Args:
        raw_question: The original question template containing placeholders.
        substitutions: A dictionary mapping placeholders to their substitutions.

    Returns:
        A list of questions with placeholders replaced by their substitutions, or None if an error occurs.
    """
    placeholders_with_for = get_placeholders_with_for(substitutions)
    number_of_placeholders_with_for = len(placeholders_with_for)
    if number_of_placeholders_with_for > 1:
        raise QueryBuildException(
            f"El uso de varios '{FOR_COMMAND_PREFFIX}' con los placeholders no está soportado"
        )
    elif number_of_placeholders_with_for == 1:
        questions = replace_placeholders_with_one_for(
            raw_question, substitutions, placeholders_with_for[0]
        )
    else:
        questions = [replace_question_with_substitutions(raw_question, substitutions)]
    return questions


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
