import os
from typing import Final, Sequence

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from rich import print

from .ahora import get_current_time

modelos: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]


def elegir_modelo() -> str:
    # Mostrar opciones al usuario
    print(
        "[bright_cyan]Por favor, elige un modelo introduciendo el número correspondiente:"
    )
    for i, modelo in enumerate(modelos, start=1):
        print(f"{i}. mistral-{modelo}")
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
        if 1 <= eleccion_numerica <= len(modelos):
            modelo_elegido = modelos[eleccion_numerica - 1]
        else:
            print("[red]Número fuera de rango. Seleccionando el modelo por defecto.")
            modelo_elegido = modelos[0]
    except ValueError:
        print("[red]Entrada no válida. Seleccionando el modelo por defecto.")
        modelo_elegido = modelos[0]
    print(f"\nModelo elegido: mistral-{modelo_elegido}\n")
    return modelo_elegido


def main() -> None:
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-" + elegir_modelo()

    client = MistralClient(api_key=api_key)

    while True:
        print("\n[bright_cyan]Introduce tu consulta:\n")
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
        print("\n[light_green]USER:[/light_green] " + question + "\n")
        print("[light_green]" + model.upper() + ":[/light_green] " + content + "\n")
        print(
            "\n[dark_goldenrod]Pulsa Enter para seguir, d para entrar en el modo de depuración, q para salir"
        )
        entrada = input("\n")
        if entrada == "q":
            break
        elif entrada == "d":
            from .debug import show  # pyright: ignore [reportUnusedImport]

            print("[dark_goldenrod]Entrando en modo de depuracion")
            breakpoint()
            print("[dark_goldenrod]Saliendo del modo de depuración\n")
    print("Saliendo")
    exit()


if __name__ == "__main__":
    main()
