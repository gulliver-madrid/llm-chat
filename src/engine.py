from collections.abc import Sequence

from src.command_handler import CommandHandler
from src.controllers.command_interpreter import (
    CommandInterpreter,
    CommandNoValid,
)
from src.controllers.select_model import SelectModelController
from src.domain import Model
from src.protocols import ViewProtocol
from src.view import Raw


class MainEngine:

    def __init__(
        self,
        models: Sequence[Model],
        command_interpreter: CommandInterpreter,
        command_handler: CommandHandler,
        select_model_controler: SelectModelController,
        view: ViewProtocol,
    ) -> None:
        self._models = models
        select_model_controler = select_model_controler
        self._command_interpreter = command_interpreter
        self._command_handler = command_handler
        self._view = view

    def initiate(self) -> None:
        self._command_handler.prompt_to_select_model()

    def process_raw_query(self, raw_query: str) -> None:
        try:
            action, remaining_input = self._command_interpreter.parse_user_input(
                raw_query
            )
        except CommandNoValid as err:
            self._view.show_error_msg(Raw(str(err)))
            return
        self._command_handler.process_action(action, remaining_input)
