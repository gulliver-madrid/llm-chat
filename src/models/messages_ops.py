from src.models.shared import ChatMessage, CompleteMessage


def add_user_query_in_place(messages: list[CompleteMessage], query: str) -> None:
    messages.append(CompleteMessage(ChatMessage(role="user", content=query)))
