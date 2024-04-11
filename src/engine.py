from typing import Sequence

from src.command_handler import CommandHandler
from src.generic_view import Raw
from src.infrastructure.client_wrapper import (
    ClientWrapper,
)
from src.controllers.command_interpreter import (
    CommandInterpreter,
    CommandNoValid,
)
from src.controllers.select_model import SelectModelController
from src.infrastructure.repository import ChatRepository
from src.io_helpers import (
    show_error_msg,
)
from src.models.shared import (
    Model,
)
from src.view import View


class MainEngine:

    def __init__(self, models: Sequence[Model], client_wrapper: ClientWrapper) -> None:
        self._models = models
        select_model_controler = SelectModelController(models)
        repository = ChatRepository()
        client_wrapper = client_wrapper
        view = View()

        self._command_interpreter = CommandInterpreter()
        self._command_handler = CommandHandler(
            view,
            select_model_controler,
            repository,
            client_wrapper,
        )

    def initiate(self) -> None:
        self._command_handler.prompt_to_select_model()

    def process_raw_query(self, raw_query: str) -> None:
        try:
            action, remaining_input = self._command_interpreter.parse_user_input(
                raw_query
            )
        except CommandNoValid as err:
            show_error_msg(Raw(str(err)))
            return
        self._command_handler.process_action(action, remaining_input)
