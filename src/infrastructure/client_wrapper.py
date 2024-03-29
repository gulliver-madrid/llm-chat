from dataclasses import dataclass
from typing import Any, Sequence, cast
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from mistralai.exceptions import MistralConnectionException
from openai import OpenAI

from src.models.shared import (
    ChatMessage,
    CompleteMessage,
    Model,
    Platform,
    extract_chat_messages,
)


__all__ = ["QueryResult", "ClientWrapper"]


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[CompleteMessage]


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

    def get_simple_response(
        self,
        model: Model,
        query: str,
        prev_messages: Sequence[CompleteMessage] | None,
        *,
        debug: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "none",
        append_query: bool = True,
    ) -> QueryResult:
        """
        Retrieves a simple response from the LLM client.
        """

        complete_messages = list(prev_messages) if prev_messages else []
        if append_query:
            complete_messages.append(
                CompleteMessage(ChatMessage(role="user", content=query))
            )
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
        mistral_chat_msg = choices[0].message
        assert isinstance(mistral_chat_msg.content, str)
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
