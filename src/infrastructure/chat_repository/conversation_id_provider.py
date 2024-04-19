from collections.abc import Sequence
from typing import Iterable

from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper

from src.infrastructure.chat_repository.chat_file_detecter import ChatFileDetecter
from src.setup_logging import configure_logger
from src.models.serialization import (
    NUMBER_OF_DIGITS,
    ConversationId,
    convert_digits_to_conversation_id,
)

logger = configure_logger(__name__)

TOO_MUCH_CHATS = 10**NUMBER_OF_DIGITS  # pragma: no mutate
WARNING_THRESHOLD = TOO_MUCH_CHATS * 0.9  # pragma: no mutate


class FreeConversationIdProvider:
    """
    Clase especializada en proveer el siguiente ConversationId libre de acuerdo al contenido
    del directorio de chats.
    """

    def __init__(
        self,
        file_manager: FileManager,
        chat_detecter: ChatFileDetecter,
        chats_dir: PathWrapper,
    ):
        self._file_manager = file_manager
        self._chat_detecter = chat_detecter
        self._chats_dir = chats_dir

    def get_next_free_conversation_id(self) -> ConversationId:
        max_number = self._find_max_file_number(self._chats_dir)
        new_number = (max_number + 1) if max_number is not None else 0
        if new_number > WARNING_THRESHOLD:
            logger.warning("Warning: running short of chat id numbers")
        assert 0 <= new_number < TOO_MUCH_CHATS, new_number
        return convert_digits_to_conversation_id(str(new_number))

    def _find_max_file_number(self, directory_path: PathWrapper) -> int | None:
        assert self._file_manager.path_is_dir(directory_path)
        children = self._file_manager.get_children(directory_path)
        chat_files = self._chat_detecter.filter_chat_files(children)
        log_ignored_paths(children, chat_files)
        return get_max_stem_value(chat_files)


def get_max_stem_value(chat_files: Iterable[PathWrapper]) -> int | None:
    values = (int(p.stem) for p in chat_files)
    return max(values, default=None)


def log_ignored_paths(
    children: Sequence[PathWrapper], chat_files: Sequence[PathWrapper]
) -> None:
    ignored_count = len(children) - len(chat_files)
    if ignored_count > 0:
        logger.info(f"Se ignoraron {ignored_count} rutas")
