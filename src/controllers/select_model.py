from typing import Sequence

from rich import print


from src.generic_view import GenericView, Raw
from src.io_helpers import (
    BLUE_VIOLET_COLOR,
    BOLD_STYLE,
    CALL_TO_ACTION,
    NEUTRAL_MSG,
    apply_style_tag,
    escape_for_rich,
    get_input,
    show_error_msg,
    to_styled,
)
from src.models.model_choice import ModelChoiceParser
from src.models.shared import ModelName, Model


class SelectModelController:
    def __init__(self, models: Sequence[Model]) -> None:
        self._model_choice_parser = ModelChoiceParser(models)
        self._models = models
        self._default_model = self._models[0]
        self._view = GenericView()

    def select_model(self) -> Model:
        """
        Prompt the user to choose a model. Returns the model name without the 'mistral' preffix.
        """
        num_options = len(self._models)
        assert num_options > 0
        chosen_model = None
        while not chosen_model:

            self._show_options()

            user_choice = get_input(
                apply_style_tag(
                    Raw(f"Introduce tu elección (1-{num_options})"), BOLD_STYLE
                )
            )
            if user_choice:
                try:
                    chosen_model = self._model_choice_parser.parse(user_choice)
                except ValueError as err:
                    show_error_msg(Raw(str(err)))
            else:
                chosen_model = self._default_model

        self._view.print(
            escape_for_rich(Raw(f"\nModelo elegido: {chosen_model.model_name}"))
        )
        return chosen_model

    def _show_options(self) -> None:
        # Mostrar opciones al usuario
        print(
            apply_style_tag(
                Raw(
                    "\nPor favor, elige un modelo introduciendo el número correspondiente:"
                ),
                CALL_TO_ACTION,
            )
        )
        for i, model in enumerate(self._models, start=1):
            self._view.print(escape_for_rich(Raw(f"{i}. {model.model_name}")))

        styled_default_model_explanation = create_styled_default_model_explanation(
            self._default_model.model_name
        )
        print(styled_default_model_explanation)


def create_styled_default_model_explanation(default_model: ModelName) -> str:
    model_name_styled = apply_style_tag(Raw(f"{default_model}"), BLUE_VIOLET_COLOR)
    explanation = to_styled(
        "\nPresiona enter sin seleccionar un número para elegir el modelo "
        + model_name_styled
        + " por defecto."
    )
    return apply_style_tag(explanation, NEUTRAL_MSG)
