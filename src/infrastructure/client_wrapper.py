from dataclasses import dataclass
from pprint import pformat
import time
from typing import Any, Sequence, cast

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from mistralai.exceptions import MistralConnectionException
from openai import OpenAI

from src.domain import ChatMessage
from src.logging import configure_logger
from src.models.shared import (
    CompleteMessage,
    Model,
    Platform,
    extract_chat_messages,
)


__all__ = ["QueryResult", "ClientWrapper"]


logger = configure_logger(__name__, __file__)


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[CompleteMessage]


prev_times: list[float] = []


def prevent_too_many_queries() -> None:
    # debe fallar si se han hecho 10 consultas en menos de 20 segundos,
    # para evitar llamadas a la API sin control debido a algun bug
    prev_times.append(time.time())
    if len(prev_times) >= 10:
        if (seconds := (prev_times[-1] - prev_times[0])) < 20:
            raise RuntimeError(
                f"Demasiadas consultas a la API: 10 en {seconds} segundos"
            )
        prev_times.pop(0)


class ClientWrapper:

    def __init__(
        self, *, mistral_api_key: str | None = None, openai_api_key: str | None = None
    ):
        self._mistralai_client = None
        self._openai_client = None
        if mistral_api_key:
            self._mistralai_client = MistralClient(api_key=mistral_api_key)
        if openai_api_key:
            self._openai_client = OpenAI(api_key=openai_api_key)

    def get_simple_response_to_query(
        self,
        model: Model,
        query: str,
        prev_messages: Sequence[CompleteMessage] | None,
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
    ) -> QueryResult:
        """
        Retrieves a simple response from the LLM client.
        """

        complete_messages = list(prev_messages) if prev_messages else []

        complete_messages.append(
            CompleteMessage(ChatMessage(role="user", content=query))
        )
        return self.get_simple_response(
            model, complete_messages, debug=debug, tools=tools, tool_choice=tool_choice
        )

    def get_simple_response(
        self,
        model: Model,
        complete_messages: list[CompleteMessage],
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
    ) -> QueryResult:
        """
        Retrieves a simple response from the LLM client.
        """
        prevent_too_many_queries()
        # type annotated here for safety because MistralClient define messages type as list[Any]
        messages: list[ChatMessage] = extract_chat_messages(complete_messages)
        match model.platform:
            case Platform.OpenAI:
                assert not tools, "Currently tools are not available with OpenAI models"
                chat_msg = self._answer_using_openai(model, messages)
            case Platform.Mistral:
                chat_msg = self._answer_using_mistral(
                    model, messages, tools=tools, tool_choice=tool_choice
                )
            case _:
                raise ValueError(f"Missing platform in model: {model}")
        if debug:
            print(f"{chat_msg=}")
            breakpoint()
        complete_messages.append(CompleteMessage(chat_msg, model))
        return QueryResult(chat_msg.content, complete_messages)

    def _answer_using_openai(
        self, model: Model, messages: Sequence[ChatMessage]
    ) -> ChatMessage:
        assert (
            self._openai_client
        ), "OpenAI client not defined. Did you forget to provide an api key for OpenAI API?"
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

    def _answer_using_mistral(
        self,
        model: Model,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
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
        assert (
            self._mistralai_client
        ), "Mistral AI client not defined. Did you forget to provide an api key for Mistral API?"
        logger.info(f"{tool_choice=}")
        try:
            chat_response = self._mistralai_client.chat(
                model=model.model_name,
                messages=mistral_messages,
                tools=tools,
                tool_choice=tool_choice,
            )
        except MistralConnectionException:
            raise RuntimeError(
                "Error de conexión con la API de Mistral. Por favor, revise su conexión a internet."
            ) from None
        choices = chat_response.choices
        assert len(choices) == 1
        mistral_chat_msg = choices[0].message
        assert isinstance(mistral_chat_msg.content, str)

        logger.info("mistral_chat_msg:")
        logger.info(pformat(mistral_chat_msg))

        return ChatMessage(
            mistral_chat_msg.role,
            mistral_chat_msg.content,
            tool_calls=mistral_chat_msg.tool_calls,
        )

    def define_system_prompt(
        self,
        prompt: str,
    ) -> list[CompleteMessage]:
        return [CompleteMessage(chat_msg=ChatMessage("system", prompt))]
