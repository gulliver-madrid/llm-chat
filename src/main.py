import os
from typing import Final, Sequence

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from .ahora import get_current_time

modelos: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]


def elegir_modelo() -> str:

    # Mostrar opciones al usuario
    print("Por favor, elige un modelo introduciendo el número correspondiente:")
    for i, modelo in enumerate(modelos, start=1):
        print(f"{i}. mistral-{modelo}")
    print(
        f"Presiona enter sin seleccionar un número para elegir el modelo mistral-{modelos[0]} por defecto."
    )

    # Leer la eleccion del usuario
    eleccion = input("Introduce tu elección (1-{}): ".format(len(modelos)))

    # Establecer el modelo por defecto si el usuario presiona enter directamente
    if eleccion == "":
        eleccion = "1"

    # Asegurarse de que la eleccion es valida
    try:
        eleccion_numerica = int(eleccion)
        if 1 <= eleccion_numerica <= len(modelos):
            modelo_elegido = modelos[eleccion_numerica - 1]
        else:
            print("Número fuera de rango. Seleccionando el modelo por defecto.")
            modelo_elegido = modelos[0]
    except ValueError:
        print("Entrada no válida. Seleccionando el modelo por defecto.")
        modelo_elegido = modelos[0]
    print(f"\nModelo elegido: mistral-{modelo_elegido}\n")
    return modelo_elegido


def main() -> None:
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-" + elegir_modelo()

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
