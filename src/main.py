import os
from typing import Final, Sequence

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse
from rich import print

from src.ahora import get_current_time
from src.io_helpers import (
    HIGHLIGHT_ROLE,
    NEUTRAL_MSG,
    end,
    get_input,
    show_error_msg,
)
from src.model_choice import select_model


modelos: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]


def print_interaction(model: str, question: str, content: str) -> None:
    """Prints an interaction between user and model"""
    print("\n" + get_current_time())
    print(HIGHLIGHT_ROLE + "\nUSER: " + end(HIGHLIGHT_ROLE) + question + "\n")
    print(HIGHLIGHT_ROLE + model.upper() + ": " + end(HIGHLIGHT_ROLE) + content + "\n")


class MenuManager:
    @staticmethod
    def enter_debug_mode(response: ChatCompletionResponse | None) -> None:
        from src.debug import show  # pyright: ignore [reportUnusedImport]

        print(NEUTRAL_MSG + "Entrando en modo de depuracion\n")
        print(response)
        breakpoint()
        print(NEUTRAL_MSG + "\nSaliendo del modo de depuración\n")

    @staticmethod
    def enter_inner_menu(response: ChatCompletionResponse | None) -> bool:
        salir = False
        while True:
            entrada = get_input(
                "Pulsa Enter para continuar con otra consulta, d para entrar en el modo de depuración, q para salir."
            ).lower()
            print()
            if not entrada:
                break
            elif entrada in ["q", "quit", "exit"]:
                salir = True
                break
            elif entrada in ["d", "debug"]:
                MenuManager.enter_debug_mode(response)
                break
            else:
                show_error_msg("Entrada no válida")
        return salir


def main() -> None:
    """Runs the text interface to Mistral models"""
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-" + select_model(modelos)
    chat_response = None

    client = MistralClient(api_key=api_key)

    while True:
        # modo multilinea por defecto
        question = get_input(
            "Introduce tu consulta (o pulsa Enter para ver más opciones). Introduce `end` como único contenido de una línea cuando hayas terminado."
        )

        if not question:
            salir = MenuManager.enter_inner_menu(chat_response)
            if salir:
                break
            continue

        assert question

        while (more := input()).lower() != "end":
            question += "\n" + more

        print("...procesando")

        chat_response = client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=question)],
        )
        choices = chat_response.choices
        content = choices[0].message.content
        assert isinstance(content, str)
        print_interaction(model, question, content)

    print(NEUTRAL_MSG + "Saliendo")
    exit()


if __name__ == "__main__":
    main()
