from collections.abc import Sequence


from src.python_modules.FileSystemWrapper.file_manager import FileManager


from src.command_handler import CommandHandler
from src.controllers.command_interpreter import (
    CommandInterpreter,
    CommandNoValid,
)
from src.controllers.select_model import SelectModelController
from src.domain import Model
from src.infrastructure.chat_repository.implementer import ChatRepositoryImplementer
from src.infrastructure.chat_repository.repository import ChatRepository
from src.infrastructure.main_path_provider import get_main_directory
from src.infrastructure.now import TimeManager
from src.infrastructure.llm_connection import ClientWrapper
from src.view import Raw, View


def setup_engine(
    models: Sequence[Model], client_wrapper: ClientWrapper
) -> "MainEngine":
    select_model_controler = SelectModelController(models)
    chat_repository = ChatRepository(
        get_main_directory(),
        file_manager=FileManager(),
        time_manager=TimeManager(),
        chat_repository_implementer=ChatRepositoryImplementer(),
    )
    view = View()
    command_interpreter = CommandInterpreter()
    command_handler = CommandHandler(
        view=view,
        select_model_controler=select_model_controler,
        repository=chat_repository,
        client_wrapper=client_wrapper,
        time_manager=TimeManager(),
    )
    return MainEngine(
        models, command_interpreter, command_handler, select_model_controler, view
    )


class MainEngine:

    def __init__(
        self,
        models: Sequence[Model],
        command_interpreter: CommandInterpreter,
        command_handler: CommandHandler,
        select_model_controler: SelectModelController,
        view: View,
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
