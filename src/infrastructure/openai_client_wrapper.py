from pprint import pformat
from types import NoneType
from typing import Any, Sequence, cast

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

    def answer(
        self,
        model: Model,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatMessage:
        openai_messages: Any = []
        for msg in messages:
            openai_msg: Any = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            openai_messages.append(openai_msg)

        logger.info(f"{model=}")
        logger.info("openai_messages=" + pformat(openai_messages, width=120))
        logger.info(f"{tools=}")

        openai_chat_completion = self._openai_client.chat.completions.create(
            messages=openai_messages,
            model=model.model_name,
            tools=cast(Any, tools),
        )
        openai_chat_msg = openai_chat_completion.choices[0].message

        logger.info("openai_chat_msg=" + pformat(openai_chat_msg))

        assert isinstance(openai_chat_msg.content, (str, NoneType))
        content = openai_chat_msg.content
        role = openai_chat_msg.role
        return ChatMessage(role, content or "", tool_calls=openai_chat_msg.tool_calls)
