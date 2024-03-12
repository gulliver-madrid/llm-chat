from typing import Sequence

from rich import print

from src.io_helpers import CALL_TO_ACTION, NEUTRAL_MSG, get_input, show_error_msg

MODEL_PREFIX = "mistral"


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


def select_model(modelos: Sequence[str]) -> str:
    """Prompt the user to choose a model. Returns the model name without the 'mistral' preffix."""
    default_model = modelos[0]
    while True:
        # Mostrar opciones al usuario
        print(
            CALL_TO_ACTION
            + "\nPor favor, elige un modelo introduciendo el número correspondiente:"
        )
        for i, modelo in enumerate(modelos, start=1):
            print(f"{i}. {MODEL_PREFIX}-{modelo}")
        print(
            NEUTRAL_MSG
            + f"\nPresiona enter sin seleccionar un número para elegir el modelo [blue_violet]{MODEL_PREFIX}-{default_model}[/blue_violet] por defecto."
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

    print(f"\nModelo elegido: {MODEL_PREFIX}-{modelo_elegido}")
    return modelo_elegido
