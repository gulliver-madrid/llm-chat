from __future__ import annotations

from typing import Final, Sequence

from src.domain import CompleteMessage, QueryResult
from src.model_manager import ModelManager
from src.models.placeholders import QueryText
from src.protocols import ChatRepositoryProtocol, ViewProtocol
from src.view import Raw


class QueryAnswerer:
    __slots__ = (
        "_view",
        "_repository",
        "_model_manager",
        "_prev_messages",
    )
    _view: Final[ViewProtocol]
    _repository: Final[ChatRepositoryProtocol]
    _model_manager: Final[ModelManager]
    _prev_messages: Final[list[CompleteMessage]]

    def __init__(
        self,
        *,
        view: ViewProtocol,
        repository: ChatRepositoryProtocol,
        model_manager: ModelManager,
        prev_messages: list[CompleteMessage],
    ):
        self._view = view
        self._repository = repository
        self._model_manager = model_manager
        self._prev_messages = prev_messages

    def answer_queries(self, queries: Sequence[QueryText], debug: bool = False) -> None:
        """If there are multiple queries, the conversation ends after executing them."""
        assert queries
        messages = None
        for i, query in enumerate(queries):
            messages = self._answer_query(debug, i + 1, len(queries), query)
        self._prev_messages[:] = messages or []

    def _answer_query(
        self, debug: bool, current: int, total: int, query: QueryText
    ) -> list[CompleteMessage] | None:
        self._view.display_processing_query_text(current=current, total=total)
        query_result = self._get_simple_response_from_model(query, debug)
        self._print_interaction(query, query_result)
        self._repository.save_messages(query_result.messages)
        return query_result.messages if current == 1 else None

    def _get_simple_response_from_model(
        self, query: QueryText, debug: bool = False
    ) -> QueryResult:
        return self._model_manager.get_simple_response(
            query, self._prev_messages, debug=debug
        )

    def _print_interaction(self, query: QueryText, query_result: QueryResult) -> None:
        model = self._model_manager.model_wrapper.model
        assert model
        self._view.print_interaction(
            model.model_name,
            Raw(query),
            Raw(query_result.content),
        )
