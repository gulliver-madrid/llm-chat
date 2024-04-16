from dataclasses import dataclass
import time
from typing import Any, Sequence

from src.infrastructure.exceptions import (
    ClientNotDefined,
    TooManyRequests,
    LLMChatException,
)
from src.logging import configure_logger
from src.models.shared import (
    ChatMessage,
    CompleteMessage,
    Model,
    Platform,
    extract_chat_messages,
)
from .mistral_client_wrapper import MistralClientWrapper
from .openai_client_wrapper import OpenAIClientWrapper

__all__ = ["QueryResult", "ClientWrapper"]


logger = configure_logger(__name__)


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[CompleteMessage]


def add_user_query_in_place(messages: list[CompleteMessage], query: str) -> None:
    messages.append(CompleteMessage(ChatMessage(role="user", content=query)))


prev_times: list[float] = []


def prevent_too_many_queries() -> None:
    # debe fallar si se han hecho 10 consultas en menos de 20 segundos,
    # para evitar llamadas a la API sin control debido a algun bug
    prev_times.append(time.time())
    if len(prev_times) >= 10:
        if (seconds := (prev_times[-1] - prev_times[0])) < 20:
            raise TooManyRequests(10, seconds)
        prev_times.pop(0)


class ClientWrapper:

    def __init__(
        self, *, mistral_api_key: str | None = None, openai_api_key: str | None = None
    ):
        self._mistralai_client_wrapper = None
        self._openai_client_wrapper = None
        if mistral_api_key:
            self._mistralai_client_wrapper = MistralClientWrapper(mistral_api_key)
        if openai_api_key:
            self._openai_client_wrapper = OpenAIClientWrapper(openai_api_key)

    def get_simple_response_to_query(
        self,
        model: Model,
        query: str,
        prev_messages: Sequence[CompleteMessage] | None,
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
        random_seed: int | None = None,
    ) -> QueryResult:
        """
        Retrieves a simple response from the LLM client.
        """

        complete_messages = list(prev_messages) if prev_messages else []
        add_user_query_in_place(complete_messages, query)
        return self.get_simple_response(
            model,
            complete_messages,
            debug=debug,
            tools=tools,
            tool_choice=tool_choice,
            random_seed=random_seed,
        )

    def get_simple_response(
        self,
        model: Model,
        complete_messages: list[CompleteMessage],
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
        random_seed: int | None = None,
    ) -> QueryResult:
        """
        Retrieves a simple response from the LLM client.
        """
        prevent_too_many_queries()
        # type annotated here for safety because MistralClient define messages type as list[Any]
        messages: list[ChatMessage] = extract_chat_messages(complete_messages)

        if model.platform == Platform.OpenAI:
            if random_seed is not None:
                raise LLMChatException(
                    "Error: random_seed not currently supported with OpenAI API"
                )
            if not self._openai_client_wrapper:
                raise ClientNotDefined("OpenAI", "OpenAI")
            chat_msg = self._openai_client_wrapper.answer(model, messages, tools=tools)

        elif model.platform == Platform.Mistral:
            if not self._mistralai_client_wrapper:
                raise ClientNotDefined("Mistral AI", "Mistral")
            chat_msg = self._mistralai_client_wrapper.answer(
                model,
                messages,
                tools=tools,
                tool_choice=tool_choice,
                random_seed=random_seed,
            )

        else:
            raise ValueError(f"Missing platform in model: {model}")

        if debug:
            print(f"{chat_msg=}")
            breakpoint()
        complete_messages.append(CompleteMessage(chat_msg, model))
        return QueryResult(chat_msg.content, complete_messages)
