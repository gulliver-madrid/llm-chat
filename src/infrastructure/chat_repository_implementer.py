import re
from typing import Iterable

from src.logging import configure_logger
from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper
from src.python_modules.FileSystemWrapper.safe_file_remover import SafeFileRemover

from src.models.serialization import (
    NUMBER_OF_DIGITS,
    ConversationId,
    convert_digits_to_conversation_id,
)

logger = configure_logger(__name__)

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")

TOO_MUCH_CHATS = 10**NUMBER_OF_DIGITS
WARNING_THRESHOLD = TOO_MUCH_CHATS * 0.9


class ChatRepositoryImplementer:
    """Only access to disk using FileManager"""

    is_initialized: bool = False

    def init(
        self,
        data_dir: PathWrapper,
        chats_dir: PathWrapper,
        file_manager: FileManager,
    ) -> None:
        assert not self.is_initialized
        self._file_manager = file_manager
        self._file_remover = SafeFileRemover(self._file_manager)
        self.__data_dir = data_dir
        self._chats_dir = chats_dir
        self.is_initialized = True

    def move_chat_files_from_data_dir_to_chat_dir(self) -> None:
        """
        In the previous version, chat files were directly stored in the data directory.
        This function migrates them to the chat directory, ensuring that the coherence
        of the ids is maintained throughout the process.
        """
        assert self.is_initialized
        for path_wrapper in self._file_manager.get_children(self.__data_dir):
            if not self._is_chat_file(path_wrapper):
                continue
            new_id = self.get_new_conversation_id()
            new_path = self.build_chat_path(new_id)
            self._move_content(path_wrapper, new_path)

    def build_chat_path(self, conversation_id: ConversationId) -> PathWrapper:
        filename = conversation_id + "." + CHAT_EXT
        return self._chats_dir / filename

    def get_new_conversation_id(self) -> ConversationId:
        max_number = self._find_max_file_number(self._chats_dir)
        new_number = (max_number + 1) if max_number is not None else 0
        if new_number > WARNING_THRESHOLD:
            logger.warning("Warning: running short of chat id numbers")
        assert 0 <= new_number < TOO_MUCH_CHATS, new_number
        return convert_digits_to_conversation_id(str(new_number))

    def _move_content(self, source: PathWrapper, dest: PathWrapper) -> None:
        content = self._file_manager.read_file(source)
        assert not self._file_manager.path_exists(dest), dest
        self._file_manager.write_file(dest, content)
        self._file_remover.remove_file(source)

    def _is_chat_file(self, path_wrapper: PathWrapper) -> bool:
        assert self._file_manager.path_exists(path_wrapper)
        if self._file_manager.path_is_dir(path_wrapper):
            return False
        return CHAT_NAME_PATTERN.match(path_wrapper.name) is not None

    def _find_max_file_number(self, directory_path: PathWrapper) -> int | None:
        assert self._file_manager.path_is_dir(directory_path)

        children = self._file_manager.get_children(directory_path)
        chat_files = self._get_chat_files(children)

        ignored_count = len(children) - len(chat_files)
        if ignored_count > 0:
            logger.info(f"Se ignoraron {ignored_count} rutas")

        return get_max_stem_value(chat_files)

    def _get_chat_files(
        self, path_wrappers: Iterable[PathWrapper]
    ) -> list[PathWrapper]:
        return [p for p in path_wrappers if not self._is_chat_file(p)]


def get_max_stem_value(chat_files: Iterable[PathWrapper]) -> int | None:
    values = (int(p.stem) for p in chat_files)
    return max(values, default=None)