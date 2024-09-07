from collections.abc import Sequence

from src.python_modules.FileSystemWrapper.file_manager import FileManager

from src.command_handler import CommandHandler
from src.controllers.command_interpreter import CommandInterpreter
from src.controllers.select_model import SelectModelController
from src.domain import Model
from src.engine import MainEngine
from src.infrastructure.chat_repository.repository import ChatRepository
from src.infrastructure.main_path_provider import get_main_directory
from src.infrastructure.now import TimeManager
from src.infrastructure.llm_connection import ClientWrapper
from src.view import View


def setup_engine(models: Sequence[Model], client_wrapper: ClientWrapper) -> MainEngine:
    """Returns a default MainEngine"""
    select_model_controler = SelectModelController(models)
    chat_repository = ChatRepository(
        get_main_directory(),
        file_manager=FileManager(),
        time_manager=TimeManager(),
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
