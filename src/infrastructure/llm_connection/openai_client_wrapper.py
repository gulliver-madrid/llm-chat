from collections.abc import Mapping
from types import NoneType
from typing import Any, Iterable, Sequence, cast

from openai import OpenAI

from src.domain import ChatMessage
from src.setup_logging import configure_logger, format_var
from src.models.shared import Model

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
        logger.info(f"{model=}")
        logger.info(f"{tools=}")

        openai_messages = [convert_to_openai_msg(msg) for msg in messages]

        logger.info(format_var("openai_messages", openai_messages))

        openai_chat_completion = self._openai_client.chat.completions.create(
            messages=cast_openai_messages(openai_messages),
            model=model.model_name,
            tools=cast(Any, tools),
        )
        openai_chat_msg = openai_chat_completion.choices[0].message

        logger.info(format_var("openai_chat_msg", openai_chat_msg))

        assert isinstance(openai_chat_msg.content, (str, NoneType))
        content = openai_chat_msg.content
        role = openai_chat_msg.role
        return ChatMessage(role, content or "", tool_calls=openai_chat_msg.tool_calls)


def convert_to_openai_msg(msg: ChatMessage) -> Mapping[str, object]:
    openai_msg: dict[str, object] = {
        "role": msg.role,
        "content": msg.content,
    }
    if tool_calls := msg.tool_calls:
        assert isinstance(tool_calls, list)
        openai_msg["tool_calls"] = tool_calls
    if id_ := msg.tool_call_id:
        assert isinstance(id_, str)
        openai_msg["tool_call_id"] = id_
    return openai_msg


def cast_openai_messages(openai_messages: list[Mapping[str, object]]) -> Iterable[Any]:
    return cast(Iterable[Any], openai_messages)
