from typing import Sequence

from rich import print

from src.io_helpers import (
    BLUE_VIOLET_COLOR,
    BOLD_STYLE,
    CALL_TO_ACTION,
    NEUTRAL_MSG,
    apply_tag,
    get_input,
    show_error_msg,
)
from src.model_choice import MODEL_PREFIX, parse_model_choice


def select_model(modelos: Sequence[str]) -> str:
    """Prompt the user to choose a model. Returns the model name without the 'mistral' preffix."""
    default_model = modelos[0]
    modelo_elegido = None
    while not modelo_elegido:
        # Mostrar opciones al usuario
        print(
            apply_tag(
                "\nPor favor, elige un modelo introduciendo el número correspondiente:",
                CALL_TO_ACTION,
            )
        )
        for i, modelo in enumerate(modelos, start=1):
            print(f"{i}. {MODEL_PREFIX}-{modelo}")
        model_name_styled = apply_tag(
            f"{MODEL_PREFIX}-{default_model}", BLUE_VIOLET_COLOR
        )
        default_model_explanation = (
            "\nPresiona enter sin seleccionar un número para elegir el modelo "
            + model_name_styled
            + " por defecto."
        )
        styled_default_model_explanation = apply_tag(
            default_model_explanation,
            NEUTRAL_MSG,
        )
        print(styled_default_model_explanation)

        # Leer la eleccion del usuario
        num_opciones = len(modelos)
        eleccion = get_input(
            apply_tag(f"Introduce tu elección (1-{num_opciones})", BOLD_STYLE)
        )
        try:
            modelo_elegido = (
                parse_model_choice(modelos, eleccion) if eleccion else default_model
            )
        except ValueError as err:
            show_error_msg(str(err))

    print(f"\nModelo elegido: {MODEL_PREFIX}-{modelo_elegido}")
    return modelo_elegido
