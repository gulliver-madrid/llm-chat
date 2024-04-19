from typing import Any, Sequence, cast

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from mistralai.exceptions import MistralConnectionException

from src.infrastructure.exceptions import APIConnectionError
from src.setup_logging import configure_logger, format_var
from src.models.shared import (
    ChatMessage,
    Model,
    Platform,
)

logger = configure_logger(__name__)


class MistralClientWrapper:
    def __init__(self, api_key: str | None = None):
        self._mistralai_client = MistralClient(api_key=api_key)

    def answer(
        self,
        model: Model,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
        random_seed: int | None = None,
    ) -> ChatMessage:
        assert model.platform == Platform.Mistral

        mistral_messages = [
            MistralChatMessage(
                role=msg.role,
                content=msg.content,
                name=msg.name,
                tool_calls=cast(Any, msg.tool_calls),
            )
            for msg in messages
        ]
        logger.info(f"{tool_choice=}")
        try:
            chat_response = self._mistralai_client.chat(
                model=model.model_name,
                messages=mistral_messages,
                tools=tools,
                tool_choice=tool_choice,
                random_seed=random_seed,
            )
        except MistralConnectionException:
            raise APIConnectionError("Mistral") from None
        choices = chat_response.choices
        assert len(choices) == 1
        mistral_chat_msg = choices[0].message
        assert isinstance(mistral_chat_msg.content, str)

        logger.info(format_var("mistral_chat_msg", mistral_chat_msg))

        return ChatMessage(
            mistral_chat_msg.role,
            mistral_chat_msg.content,
            tool_calls=mistral_chat_msg.tool_calls,
        )
