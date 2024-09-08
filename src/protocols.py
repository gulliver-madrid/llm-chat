from collections.abc import Sequence
from typing import Any, Mapping, Protocol, Sequence

from src.domain import (
    ChatMessage,
    CompleteMessage,
    ConversationId,
    ConversationText,
    Model,
    ModelName,
    QueryResult,
)
from src.models.placeholders import Placeholder
from src.view.generic_view import EscapedStr, Raw
from src.view.io_helpers import SimpleView


class ClientWrapperProtocol(Protocol):
    def get_simple_response(
        self,
        model: Model,
        complete_messages: list[CompleteMessage],
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
        random_seed: int | None = None,
    ) -> QueryResult: ...


class ChatRepositoryProtocol(Protocol):

    def get_conversation_ids(self) -> list[ConversationId]: ...

    def save_messages(self, complete_messages: Sequence[CompleteMessage]) -> None: ...

    def load_conversation(
        self, conversation_id: ConversationId
    ) -> list[CompleteMessage]: ...

    def load_conversation_as_conversation_text(
        self, conversation_id: ConversationId
    ) -> ConversationText: ...


class TimeManagerProtocol(Protocol):
    def get_current_time(self) -> str: ...


class ViewProtocol(Protocol):
    @property
    def simple_view(self) -> SimpleView: ...
    def print_interaction(
        self,
        model_name: ModelName,
        query: Raw,
        content: Raw,
    ) -> None: ...
    def get_raw_substitutions_from_user(
        self,
        unique_placeholders: Sequence[Placeholder],
    ) -> Mapping[Placeholder, str]: ...
    def confirm_launching_many_queries(self, number_of_queries: int) -> bool: ...
    def write_object(self, obj: object) -> None: ...
    def show_help(self) -> None: ...
    def input_extra_line(self) -> tuple[str, float]: ...
    def display_neutral_msg(self, texto: Raw) -> None: ...
    def display_conversation(
        self, conversation_id: ConversationId, conversation: ConversationText
    ) -> None: ...
    def display_messages(
        self,
        conversation_id: ConversationId,
        prev_messages: Sequence[ChatMessage],
    ) -> None: ...
    def display_processing_query_text(self, *, current: int, total: int) -> None: ...
    def show_error_msg(self, text: EscapedStr | Raw) -> None: ...
