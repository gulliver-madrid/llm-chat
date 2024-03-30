from dataclasses import dataclass
from typing import Any, Sequence
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from mistralai.exceptions import MistralConnectionException
from openai import OpenAI

from src.models.shared import ModelName, Platform


__all__ = ["QueryResult", "ClientWrapper", "CompleteMessage", "ChatMessage"]


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class Model:
    platform: Platform | None
    model_name: ModelName


@dataclass(frozen=True)
class CompleteMessage:
    chat_msg: ChatMessage
    model: Model | None = None


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[CompleteMessage]


class ClientWrapper:
    def __init__(self, *, mistral_api_key: str | None, openai_api_key: str | None):
        self._mistralai_client = (
            MistralClient(api_key=mistral_api_key) if mistral_api_key else None
        )
        self._openai_client = (
            OpenAI(
                api_key=openai_api_key,
            )
            if openai_api_key
            else None
        )

    def get_simple_response(
        self,
        model: Model,
        query: str,
        prev_messages: Sequence[CompleteMessage] | None,
        debug: bool = False,
    ) -> QueryResult:
        """
        Retrieves a simple response from the Mistral AI client.
        """
        if prev_messages:
            complete_messages = list(prev_messages)
        else:
            complete_messages = []
        complete_messages.append(
            CompleteMessage(ChatMessage(role="user", content=query))
        )
        # type annotated here for safety because MistralClient define messages type as list[Any]
        messages: list[ChatMessage] = [
            complete_msg.chat_msg for complete_msg in complete_messages
        ]
        content: str
        role: str
        if model.platform == Platform.OpenAI:
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
                model="gpt-3.5-turbo",
            )
            openai_chat_msg = openai_chat_completion.choices[0].message
            assert isinstance(openai_chat_msg.content, str)
            content = openai_chat_msg.content
            role = openai_chat_msg.role
        else:
            mistral_messages = [
                MistralChatMessage(role=msg.role, content=msg.content)
                for msg in messages
            ]

            assert model.platform == Platform.Mistral
            model_name = model.model_name

            try:
                mistral_chat_msg = self.get_mistral_platform_chat_response(
                    model_name, mistral_messages
                )
            except MistralConnectionException:
                raise RuntimeError(
                    "Error de conexión con la API de Mistral. Por favor, revise su conexión a internet."
                ) from None

            del mistral_messages
            assert isinstance(mistral_chat_msg.content, str)
            content = mistral_chat_msg.content
            role = mistral_chat_msg.role
        chat_msg = ChatMessage(role, content)
        if debug:
            print(chat_msg)
            breakpoint()
        complete_messages.append(CompleteMessage(chat_msg, model))
        return QueryResult(content, complete_messages)

    def get_mistral_platform_chat_response(
        self, model_name: ModelName, messages: list[MistralChatMessage]
    ) -> MistralChatMessage:
        assert (
            self._mistralai_client
        ), "Mistral AI client not defined. Did you forget to provide an api key for Mistral API?"
        chat_response = self._mistralai_client.chat(
            model=model_name,
            messages=messages,
        )
        choices = chat_response.choices
        return choices[0].message

    def define_system_prompt(
        self,
        prompt: str,
    ) -> list[CompleteMessage]:
        return [CompleteMessage(chat_msg=ChatMessage("system", prompt))]
