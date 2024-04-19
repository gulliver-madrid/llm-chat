from src.domain import ChatMessage
from src.models.shared import CompleteMessage


def add_user_query_in_place(messages: list[CompleteMessage], query: str) -> None:
    messages.append(CompleteMessage(ChatMessage(role="user", content=query)))
