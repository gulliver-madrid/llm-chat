import re
from typing import Mapping, NewType

from src.utils import remove_duplicates

Placeholder = NewType("Placeholder", str)

FOR_COMMAND_PREFFIX = "/for"


class QueryBuildException(Exception): ...


def build_queries(
    raw_query: str, substitutions: Mapping[Placeholder, str]
) -> list[str]:
    """
    Constructs a list of queries by replacing placeholders in the raw query with user-provided substitutions.
    If a 'for' command is detected, it generates multiple queries by iterating over the specified range.

    Args:
        raw_query: The original query template containing placeholders.
        substitutions: A dictionary mapping placeholders to their substitutions.

    Returns:
        A list of queries with placeholders replaced by their substitutions, or None if an error occurs.
    """
    placeholders_with_for = get_placeholders_with_for(substitutions)
    number_of_placeholders_with_for = len(placeholders_with_for)
    if number_of_placeholders_with_for > 1:
        raise QueryBuildException(
            f"El uso de varios '{FOR_COMMAND_PREFFIX}' con los placeholders no está soportado"
        )
    elif number_of_placeholders_with_for == 1:
        queries = replace_placeholders_with_one_for(
            raw_query, substitutions, placeholders_with_for[0]
        )
    else:
        queries = [replace_query_with_substitutions(raw_query, substitutions)]
    return queries


def find_unique_placeholders(s: str) -> list[Placeholder]:
    """
    Finds all unique placeholders in a given string.
    """
    pattern = re.compile(
        r"""
        (?:[^|^a-zA-Z0-9])      # not alphanumeric before
        (\$0[a-zA-Z_]+[0-9]*)   # the placeholder to find
        (?:[^a-zA-Z0-9]|$)      # the end of the string or a not alphanumeric character after
        """,
        re.VERBOSE,
    )
    return remove_duplicates(pattern.findall(s))


def replace_placeholders_with_one_for(
    query: str,
    substitutions: Mapping[Placeholder, str],
    placeholder_with_for: Placeholder,
) -> list[str]:
    replacements_in_for_str = substitutions[placeholder_with_for]
    assert replacements_in_for_str.startswith(FOR_COMMAND_PREFFIX)
    replacements_in_for_str = replacements_in_for_str.removeprefix(
        FOR_COMMAND_PREFFIX
    ).strip()

    replacements_in_for = replacements_in_for_str.split(",")
    queries: list[str] = []
    for replacement in replacements_in_for:
        queries.append(query.replace(placeholder_with_for, replacement))
    substitutions = {
        placeholder: value
        for placeholder, value in substitutions.items()
        if placeholder != placeholder_with_for
    }
    new_queries: list[str] = []
    for query in queries:
        new_queries.append(replace_query_with_substitutions(query, substitutions))
    queries = new_queries
    return queries


def replace_query_with_substitutions(
    query: str, substitutions: Mapping[Placeholder, str]
) -> str:
    for placeholder, replacement in substitutions.items():
        query = query.replace(placeholder, replacement)
    return query


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
