import os

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from .ahora import get_current_time


def main() -> None:
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-tiny"

    client = MistralClient(api_key=api_key)

    while True:
        question = input("Introduce tu consulta:\n")

        if not question:
            break

        chat_response = client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=question)],
        )
        choices = chat_response.choices
        content = choices[0].message.content
        assert isinstance(content, str)
        print("\n" + get_current_time())
        print("\nUSER: " + question + "\n")
        print(model.upper() + ": " + content + "\n")
        print("\nPulsa Enter para seguir, d para entrar en el modo de depuración")
        entrada = input("\n")
        if entrada == "d":
            from .debug import show  # pyright: ignore [reportUnusedImport]

            print("Entrando en modo de depuracion")
            breakpoint()


if __name__ == "__main__":
    main()
