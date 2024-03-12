import os
from typing import Final, Sequence

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage, ChatCompletionResponse
from rich import print

from src.io_helpers import (
    CALL_TO_ACTION,
    HIGHLIGHT_ROLE,
    NEUTRAL_MSG,
    end,
    get_input,
    show_error_msg,
)

from src.ahora import get_current_time

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


def parse_model_choice(modelos: Sequence[str], eleccion: str) -> str | None:
    # Asegurarse de que la eleccion es valida
    try:
        eleccion_numerica = int(eleccion)
    except ValueError:
        show_error_msg(
            "Entrada no válida. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )
        return None

    if 1 <= eleccion_numerica <= len(modelos):
        modelo_elegido = modelos[eleccion_numerica - 1]
        return modelo_elegido
    else:
        show_error_msg(
            "Número fuera de rango. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )
        return None


def elegir_modelo() -> str:
    """Prompt the user to choose a model. Returns the model name without the 'mistral' preffix."""
    default_model = modelos[0]
    while True:
        # Mostrar opciones al usuario
        print(
            CALL_TO_ACTION
            + "\nPor favor, elige un modelo introduciendo el número correspondiente:"
        )
        for i, modelo in enumerate(modelos, start=1):
            print(f"{i}. mixtral-{modelo}")
        print(
            NEUTRAL_MSG
            + f"\nPresiona enter sin seleccionar un número para elegir el modelo [blue_violet]mistral-{default_model}[/blue_violet] por defecto."
        )

        # Leer la eleccion del usuario
        num_opciones = len(modelos)
        eleccion = get_input(f"[bold]Introduce tu elección (1-{num_opciones})")

        if not eleccion:
            modelo_elegido = default_model
        else:
            modelo_elegido = parse_model_choice(modelos, eleccion)
        if modelo_elegido:
            break

    print(f"\nModelo elegido: mistral-{modelo_elegido}")
    return modelo_elegido


def main() -> None:
    """Runs the text interface to Mistral models"""
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-" + elegir_modelo()
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
