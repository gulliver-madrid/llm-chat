import os
from typing import Final, Sequence

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from rich import print

from .ahora import get_current_time

modelos: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]

ERROR = "[bright_red]"
CALL_TO_ACTION = "[bright_cyan]"
HIGHLIGHT_ROLE = "[light_green]"
NEUTRAL_MSG = "[dark_goldenrod]"


def end(s: str) -> str:
    assert s[0] == "["
    assert s[-1] == "]"
    return f"[/{s[1:-1]}]"


def elegir_modelo() -> str:
    while True:
        # Mostrar opciones al usuario
        print(
            CALL_TO_ACTION
            + "Por favor, elige un modelo introduciendo el número correspondiente:"
        )
        for i, modelo in enumerate(modelos, start=1):
            print(f"{i}. mixtral-{modelo}")
        print(
            f"Presiona enter sin seleccionar un número para elegir el modelo [blue_violet]mistral-{modelos[0]}[/blue_violet] por defecto.\n"
        )

        # Leer la eleccion del usuario
        print("[bold]Introduce tu elección (1-{}): ".format(len(modelos)))
        eleccion = input()

        if eleccion == "":
            eleccion = "1"

        # Asegurarse de que la eleccion es valida
        try:
            eleccion_numerica = int(eleccion)
        except ValueError:
            print(
                ERROR
                + "Entrada no válida. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto.\n"
            )
            continue

        if 1 <= eleccion_numerica <= len(modelos):
            modelo_elegido = modelos[eleccion_numerica - 1]
            break
        else:
            print(
                ERROR
                + "Número fuera de rango. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto.\n"
            )
            continue

    print(f"\nModelo elegido: mistral-{modelo_elegido}\n")
    return modelo_elegido


def main() -> None:
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-" + elegir_modelo()

    client = MistralClient(api_key=api_key)

    while True:
        print(CALL_TO_ACTION + "\nIntroduce tu consulta:\n")
        question = input()

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
        print(HIGHLIGHT_ROLE + "\nUSER: " + end(HIGHLIGHT_ROLE) + question + "\n")
        print(
            HIGHLIGHT_ROLE + model.upper() + ": " + end(HIGHLIGHT_ROLE) + content + "\n"
        )
        print(
            NEUTRAL_MSG
            + "\nPulsa Enter para seguir, d para entrar en el modo de depuración, q para salir"
        )
        entrada = input("\n")
        if entrada == "q":
            break
        elif entrada == "d":
            from .debug import show  # pyright: ignore [reportUnusedImport]

            print(NEUTRAL_MSG + "Entrando en modo de depuracion")
            breakpoint()
            print(NEUTRAL_MSG + "Saliendo del modo de depuración\n")

    print("Saliendo")
    exit()


if __name__ == "__main__":
    main()
