from typing import Final

from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    QueryText,
    build_queries,
    find_unique_placeholders,
)
from src.protocols import ViewProtocol
from src.view import Raw, ensure_escaped, show_error_msg

DELIBERATE_INPUT_TIME = 0.02


class FinalQueryExtractor:
    __slots__ = ("_view",)
    _view: Final[ViewProtocol]

    def __init__(self, *, view: ViewProtocol):
        self._view = view

    def get_final_queries(self, remaining_input: str) -> list[QueryText] | None:
        remaining_input = self._get_extra_lines(remaining_input)
        placeholders = find_unique_placeholders(remaining_input)
        return self._define_final_queries(remaining_input, placeholders)

    def _get_extra_lines(self, remaining_input: str) -> str:
        while True:
            more, elapsed = self._view.input_extra_line()
            should_end = (elapsed >= DELIBERATE_INPUT_TIME) and (more == "end")
            if should_end:
                break
            remaining_input += "\n" + more
        return remaining_input

    def _define_final_queries(
        self, remaining_input: str, placeholders: list[Placeholder]
    ) -> list[QueryText] | None:
        if not placeholders:
            return [QueryText(remaining_input)]

        user_substitutions = self._view.get_raw_substitutions_from_user(placeholders)
        try:
            queries = build_queries(remaining_input, user_substitutions)
        except QueryBuildException as err:
            show_error_msg(ensure_escaped(Raw(str(err))))
            return None

        self._view.write_object("Placeholders sustituidos exitosamente")
        return queries
