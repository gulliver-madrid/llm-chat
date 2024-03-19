from dataclasses import dataclass
from enum import Enum
from typing import Sequence
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.models.model_choice import ModelName

__all__ = ["QueryResult", "ClientWrapper", "CompleteMessage", "ChatMessage"]


@dataclass(frozen=True)
class CompleteMessage:
    chat_msg: ChatMessage
    model: ModelName | None = None


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[CompleteMessage]


class Platform(Enum):
    Mistral = "Mistral"
    OpenAI = "OpenAI"


class ClientWrapper:
    def __init__(self, api_key: str):
        self._client = MistralClient(api_key=api_key)

    def get_simple_response(
        self,
        model: ModelName,
        platform: Platform,
        query: str,
        prev_messages: Sequence[CompleteMessage] | None,
        debug: bool = False,
    ) -> QueryResult:
        """
        Retrieves a simple response from the Mistral AI client.
        """
        assert platform == Platform.Mistral
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
        chat_response = self._client.chat(
            model=model,
            messages=messages,
        )
        choices = chat_response.choices
        content = choices[0].message.content
        if debug:
            print(chat_response)
            breakpoint()
        assert isinstance(content, str)
        complete_messages.append(CompleteMessage(choices[0].message, model))
        return QueryResult(content, complete_messages)
