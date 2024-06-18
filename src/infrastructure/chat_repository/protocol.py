from collections.abc import Sequence
from typing import Protocol

from src.domain import CompleteMessage, ConversationId, ConversationText


class ChatRepositoryProtocol(Protocol):

    def get_conversation_ids(self) -> list[ConversationId]: ...

    def save_messages(self, complete_messages: Sequence[CompleteMessage]) -> None: ...

    def load_conversation(
        self, conversation_id: ConversationId
    ) -> list[CompleteMessage]: ...

    def load_conversation_as_conversation_text(
        self, conversation_id: ConversationId
    ) -> ConversationText: ...
