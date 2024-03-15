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
from src.models.model_choice import MODEL_PREFIX, ModelChoiceParser


class SelectModelController:
    def __init__(self, models: Sequence[str]) -> None:
        self._model_choice_parser = ModelChoiceParser(models)
        self._models = models
        self._default_model = self._models[0]

    def select_model(self) -> str:
        """
        Prompt the user to choose a model. Returns the model name without the 'mistral' preffix.
        """
        num_options = len(self._models)
        assert num_options > 0
        chosen_model = None
        while not chosen_model:

            self._show_options()

            user_choice = get_input(
                apply_tag(f"Introduce tu elección (1-{num_options})", BOLD_STYLE)
            )
            if user_choice:
                try:
                    chosen_model = self._model_choice_parser.parse(user_choice)
                except ValueError as err:
                    show_error_msg(str(err))
            else:
                chosen_model = self._default_model

        print(f"\nModelo elegido: {MODEL_PREFIX}-{chosen_model}")
        return chosen_model

    def _show_options(self) -> None:
        # Mostrar opciones al usuario
        print(
            apply_tag(
                "\nPor favor, elige un modelo introduciendo el número correspondiente:",
                CALL_TO_ACTION,
            )
        )
        for i, modelo in enumerate(self._models, start=1):
            print(f"{i}. {MODEL_PREFIX}-{modelo}")

        styled_default_model_explanation = create_styled_default_model_explanation(
            self._default_model
        )
        print(styled_default_model_explanation)


def create_styled_default_model_explanation(default_model: str) -> str:
    model_name_styled = apply_tag(f"{MODEL_PREFIX}-{default_model}", BLUE_VIOLET_COLOR)
    explanation = (
        "\nPresiona enter sin seleccionar un número para elegir el modelo "
        + model_name_styled
        + " por defecto."
    )
    return apply_tag(explanation, NEUTRAL_MSG)
