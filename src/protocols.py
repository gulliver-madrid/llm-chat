from collections.abc import Sequence
from typing import Any, Protocol

from src.domain import (
    CompleteMessage,
    ConversationId,
    ConversationText,
    Model,
    QueryResult,
)


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
