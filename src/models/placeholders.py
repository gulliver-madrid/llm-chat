import re
from typing import Final, Mapping, NewType

from src.utils import remove_duplicates

__all__ = ["build_queries", "find_unique_placeholders"]

Placeholder = NewType("Placeholder", str)

# Data structure mapping placeholders to their replacements
Substitutions = Mapping[Placeholder, str]

# Final text of the query (any placeholder should have been replaced)
QueryText = NewType("QueryText", str)

FOR_COMMAND_PREFFIX = "/for"


class QueryBuildException(Exception): ...


class MultipleForNotSupported(QueryBuildException):
    def __init__(self) -> None:
        super().__init__(
            f"El uso de varios '{FOR_COMMAND_PREFFIX}' con los placeholders no esta soportado"
        )


def build_queries(raw_query: str, substitutions: Substitutions) -> list[QueryText]:
    """
    Constructs a list of queries by replacing placeholders in the raw query with user-provided substitutions.
    If a 'for' command is detected, it generates multiple queries by iterating over the specified range.

    Args:
        raw_query: The original query template containing placeholders.
        substitutions: See alias definition.

    Returns:
        A list of queries with all placeholders replaced.
    """
    if (placeholders := _get_placeholders_with_for(substitutions)) == []:
        queries = [_replace_single_placeholders(raw_query, substitutions)]
    elif len(placeholders) == 1:
        placeholder = placeholders[0]
        replacer = OneForReplacer(substitutions, placeholder)
        queries = replacer.replace_placeholders_with_one_for(raw_query)
    else:
        raise MultipleForNotSupported()
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


def _get_placeholders_with_for(substitutions: Substitutions) -> list[Placeholder]:
    """
    Returns a list of placeholders that are associated with a 'for' command in the substitutions.
    """
    return [
        placeholder
        for placeholder, subs in substitutions.items()
        if subs.startswith(FOR_COMMAND_PREFFIX)
    ]


class OneForReplacer:
    def __init__(self, substitutions: Substitutions, placeholder_with_for: Placeholder):
        self._substitutions: Final = substitutions
        self._placeholder_with_for: Final = placeholder_with_for

    def replace_placeholders_with_one_for(self, query: str) -> list[QueryText]:
        """
        Replace placeholders when there is only one for-style replacement.

        Args:
            query (str): The initial query containing placeholders.
            substitutions (Substitutions): See alias definition.
            placeholder_with_for (Placeholder): Placeholder to be replaced with 'for' values.

        Returns:
            list[str]: List of new queries after replacing placeholders.
        """
        substitutions_dict = dict(self._substitutions)
        del substitutions_dict[self._placeholder_with_for]

        # Create a query for each 'for' value
        queries = [
            query.replace(self._placeholder_with_for, replacement)
            for replacement in self._get_for_replacements()
        ]

        # Replace the remaining placeholders in the queries
        return [
            _replace_single_placeholders(query, substitutions_dict) for query in queries
        ]

    def _get_for_replacements(self) -> list[str]:
        """Extract the list of individual replacements"""
        for_values_str = self._substitutions[self._placeholder_with_for]
        return self._remove_for_command(for_values_str).split(",")

    def _remove_for_command(self, raw_string: str) -> str:
        if not raw_string.startswith(command := FOR_COMMAND_PREFFIX):
            raise ValueError(f"{raw_string!r} no empieza por el comando {command}")
        return raw_string.removeprefix(command).strip()


def _replace_single_placeholders(query: str, substitutions: Substitutions) -> QueryText:
    for placeholder, replacement in substitutions.items():
        query = query.replace(placeholder, replacement)
    return QueryText(query)
