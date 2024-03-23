import os
from typing import Final, Sequence

from src.engine import ExitException, MainEngine
from src.infrastructure.client_wrapper import ClientWrapper, Model
from src.controllers.select_model import SelectModelController
from src.io_helpers import (
    display_neutral_msg,
    get_input,
)
from src.models.model_choice import MISTRAL_MODEL_PREFIX
from src.models.shared import ModelName, Platform

PROGRAM_PROMPT = "Introduce tu consulta. Introduce `end` como único contenido de una línea cuando hayas terminado. Para obtener ayuda, introduce únicamente `/help` y pulsa Enter."


class Main:
    def __init__(self, models: Sequence[Model]) -> None:
        self._select_model_controler = SelectModelController(models)
        mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self._engine = MainEngine(
            models,
            ClientWrapper(
                mistral_api_key=mistral_api_key, openai_api_key=openai_api_key
            ),
        )

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""

        self._engine.select_model()

        while True:
            raw_query = get_input(PROGRAM_PROMPT)

            if not raw_query:
                continue

            self._engine.process_raw_query(raw_query)


def main() -> None:
    mistral_models: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]
    openai_models: Final[Sequence[str]] = ["gpt-3.5-turbo", "gpt-4-1106-preview"]

    main_instance = Main(
        [
            Model(Platform.Mistral, ModelName(MISTRAL_MODEL_PREFIX + "-" + model))
            for model in mistral_models
        ]
        + [Model(Platform.OpenAI, ModelName(model)) for model in openai_models]
    )
    try:
        main_instance.execute()
    except ExitException:
        pass
    display_neutral_msg("Saliendo")


if __name__ == "__main__":
    main()
