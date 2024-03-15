from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.models.model_choice import ModelName


class ClientWrapper:
    def __init__(self, api_key: str):
        self._client = MistralClient(api_key=api_key)

    def get_simple_response(
        self, model: ModelName, question: str, debug: bool = False
    ) -> str:
        """
        Retrieves a simple response from the Mistral AI client.
        """
        chat_response = self._client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=question)],
        )
        choices = chat_response.choices
        content = choices[0].message.content
        if debug:
            print(chat_response)
            breakpoint()
        assert isinstance(content, str)
        return content
