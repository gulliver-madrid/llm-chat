import os
from typing import Final, Sequence

from rich import print

from src.ahora import get_current_time
from src.client_wrapper import ClientWrapper
from src.io_helpers import (
    NEUTRAL_MSG,
    get_input,
    highlight_role,
)
from src.menu_manager import CHANGE_MODEL, SALIR, MenuManager
from src.model_choice import MODEL_PREFIX, select_model


modelos: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]


def print_interaction(model: str, question: str, content: str) -> None:
    """Prints an interaction between user and model"""
    print("\n" + get_current_time())
    print("\n" + highlight_role("USER: ") + question)
    print("\n" + highlight_role(model.upper() + ": ") + content)


class Main:

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""
        api_key = os.environ["MISTRAL_API_KEY"]
        client_wrapper = ClientWrapper(api_key)
        model = MODEL_PREFIX + "-" + select_model(modelos)
        chat_response = None

        while True:
            # modo multilinea por defecto
            question = get_input(
                "Introduce tu consulta (o pulsa Enter para ver más opciones). Introduce `end` como único contenido de una línea cuando hayas terminado."
            )

            if not question:
                action = MenuManager.enter_inner_menu(chat_response)
                if not action:
                    continue
                elif action.name == SALIR:
                    break
                elif action.name == CHANGE_MODEL:
                    model = MODEL_PREFIX + "-" + select_model(modelos)
                    continue
                else:
                    raise RuntimeError(f"Acción no válida: {action}")

            assert question

            while (more := input()).lower() != "end":
                question += "\n" + more

            print("...procesando")

            content = client_wrapper.get_simple_response(model, question)
            print_interaction(model, question, content)


def main() -> None:
    main_instance = Main()
    main_instance.execute()
    print(NEUTRAL_MSG + "Saliendo")


if __name__ == "__main__":
    main()
