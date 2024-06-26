from dotenv import load_dotenv

import os
from typing import Sequence

from src.command_handler import ExitException
from src.controllers.select_model import SelectModelController
from src.engine import setup_engine
from src.generic_view import Raw
from src.infrastructure.llm_connection import ClientWrapper
from src.io_helpers import SimpleView, display_neutral_msg
from src.models.shared import Model
from src.models_data import get_models


PROGRAM_PROMPT = Raw(
    (
        "Introduce tu consulta. Introduce `end` como único contenido de una línea cuando hayas terminado. Para obtener ayuda, introduce únicamente `/help` y pulsa Enter."
    )
)


class Main:
    def __init__(self, models: Sequence[Model]) -> None:
        self._select_model_controler = SelectModelController(models)
        self._view = SimpleView()
        load_dotenv()
        mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self._engine = setup_engine(
            models,
            ClientWrapper(
                mistral_api_key=mistral_api_key, openai_api_key=openai_api_key
            ),
        )

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""

        self._engine.initiate()

        while True:
            raw_query = self._view.get_input(PROGRAM_PROMPT)

            if not raw_query:
                continue

            self._engine.process_raw_query(raw_query)


def main() -> None:
    main_instance = Main(get_models())
    try:
        main_instance.execute()
    except ExitException:
        pass
    display_neutral_msg(Raw("Saliendo"))


if __name__ == "__main__":
    main()
