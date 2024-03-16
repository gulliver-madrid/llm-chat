from dataclasses import dataclass
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.models.model_choice import ModelName

__all__ = ["QueryResult", "ClientWrapper", "ChatMessage"]


@dataclass(frozen=True)
class QueryResult:
    content: str
    messages: list[ChatMessage]


class ClientWrapper:
    def __init__(self, api_key: str):
        self._client = MistralClient(api_key=api_key)

    def get_simple_response(
        self, model: ModelName, query: str, debug: bool = False
    ) -> QueryResult:
        """
        Retrieves a simple response from the Mistral AI client.
        """
        messages = [ChatMessage(role="user", content=query)]
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
        messages.append(choices[0].message)
        return QueryResult(content, messages)
