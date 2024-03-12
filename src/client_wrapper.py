from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


class ClientWrapper:
    def __init__(self, api_key: str):
        self._client = MistralClient(api_key=api_key)

    def get_simple_response(self, model: str, question: str) -> str:
        chat_response = self._client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=question)],
        )
        choices = chat_response.choices
        content = choices[0].message.content
        assert isinstance(content, str)
        return content
