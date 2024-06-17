from collections.abc import Sequence

from src.domain import ChatMessage, CompleteMessage


def extract_chat_messages(
    complete_messages: Sequence[CompleteMessage],
) -> list[ChatMessage]:
    return [complete_chat.chat_msg for complete_chat in complete_messages]


def define_system_prompt(prompt: str, *, use_system: bool = True) -> CompleteMessage:
    return CompleteMessage(
        chat_msg=ChatMessage("system" if use_system else "user", prompt)
    )
