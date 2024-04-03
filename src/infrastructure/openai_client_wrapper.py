from typing import Any, Sequence

from openai import OpenAI

from src.logging import configure_logger
from src.models.shared import (
    ChatMessage,
    Model,
)

logger = configure_logger(__name__)


class OpenAIClientWrapper:
    def __init__(self, api_key: str):
        self._openai_client = OpenAI(api_key=api_key)

    def answer(self, model: Model, messages: Sequence[ChatMessage]) -> ChatMessage:

        openai_messages: Any = [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in messages
        ]
        openai_chat_completion = self._openai_client.chat.completions.create(
            messages=openai_messages,
            model=model.model_name,
        )
        openai_chat_msg = openai_chat_completion.choices[0].message
        assert isinstance(openai_chat_msg.content, str)
        content = openai_chat_msg.content
        role = openai_chat_msg.role
        return ChatMessage(role, content)
