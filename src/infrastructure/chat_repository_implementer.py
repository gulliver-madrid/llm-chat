import re
from typing import Iterable

from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper
from src.python_modules.FileSystemWrapper.safe_file_remover import SafeFileRemover

from src.models.serialization import (
    NUMBER_OF_DIGITS,
    ConversationId,
    cast_string_to_conversation_id,
)

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")


class ChatRepositoryImplementer:
    """Only access to disk using FileManager"""

    is_initialized = False

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
        assert self.is_initialized
        for path_wrapper in self._file_manager.get_children(self.__data_dir):
            if not self._is_chat_file(path_wrapper):
                continue
            new_id = self.get_new_conversation_id()
            content = self._file_manager.read_file(path_wrapper)
            new_path = self.build_chat_path(new_id)
            assert not self._file_manager.path_exists(new_path), new_path
            self._file_manager.write_file(new_path, content)
            self._file_remover.remove_file(path_wrapper)

    def build_chat_path(self, conversation_id: ConversationId) -> PathWrapper:
        filename = conversation_id + "." + CHAT_EXT
        return self._chats_dir / filename

    def get_new_conversation_id(self) -> ConversationId:
        max_number = self._find_max_file_number(self._chats_dir)
        new_number = (max_number + 1) if max_number is not None else 0
        too_much = 10**NUMBER_OF_DIGITS
        if new_number > too_much * 0.9:
            print("Warning: running short of chat id numbers")
        assert 0 <= new_number < too_much, new_number
        return cast_string_to_conversation_id(str(new_number).zfill(NUMBER_OF_DIGITS))

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
            print(f"Se ignoraron {ignored_count} rutas")

        return get_max_stem_value(chat_files)

    def _get_chat_files(
        self, path_wrappers: Iterable[PathWrapper]
    ) -> list[PathWrapper]:
        return [p for p in path_wrappers if not self._is_chat_file(p)]


def get_max_stem_value(chat_files: Iterable[PathWrapper]) -> int | None:
    values = (int(p.stem) for p in chat_files)
    return max(values, default=None)