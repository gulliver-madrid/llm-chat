from pathlib import Path
import re
from typing import Sequence

from src.infrastructure.ahora import get_current_time
from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper
from src.models.serialization import (
    NUMBER_OF_DIGITS,
    ConversationId,
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from src.models.shared import CompleteMessage

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")


class ChatRepository:
    def __init__(self) -> None:
        self._file_manager = FileManager()
        self.__data_dir = PathWrapper(Path(__file__).parent.parent.parent / "data")
        self._chats_dir = self.__data_dir / "chats"
        self._file_manager.mkdir_if_not_exists(self.__data_dir)
        self._file_manager.mkdir_if_not_exists(self._chats_dir)
        self._move_chat_files_from_data_dir_to_chat_dir()

    def _move_chat_files_from_data_dir_to_chat_dir(self) -> None:
        for path_wrapper in self._file_manager.get_children(self.__data_dir):
            if not self._is_chat_file(path_wrapper):
                continue
            new_id = self._get_new_conversation_id()
            text = self._file_manager.read_file(path_wrapper)
            new_path = self._build_chat_path(new_id)
            assert not self._file_manager.path_exists(new_path), new_path
            self._file_manager.write_file(new_path, text)
            self._remove_using_tmp_file(path_wrapper)

    def _remove_using_tmp_file(self, path_wrapper: PathWrapper) -> None:
        tmp_delete_path = create_temporary_delete_path(path_wrapper)
        self._file_manager.rename_path(path_wrapper, tmp_delete_path)
        assert not self._file_manager.path_exists(path_wrapper)
        self._file_manager.unlink_path(tmp_delete_path)

    def save(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._get_new_conversation_id()
        conversation = create_conversation_texts(
            complete_messages, conversation_id, get_current_time()
        )
        self._save_conversation(conversation_id, conversation)

    def load_conversation_as_text(self, conversation_id: ConversationId) -> str:
        filepath = self._build_conversation_filepath(conversation_id)
        return self._file_manager.read_file(filepath)

    def _get_new_conversation_id(self) -> ConversationId:
        max_number = self._find_max_file_number(self._chats_dir)
        new_number = (max_number + 1) if max_number is not None else 0
        assert 0 <= new_number < 10**NUMBER_OF_DIGITS
        return cast_string_to_conversation_id(str(new_number).zfill(NUMBER_OF_DIGITS))

    def _save_conversation(
        self, conversation_id: ConversationId, conversation_as_text: str
    ) -> None:
        filepath = self._build_conversation_filepath(conversation_id)
        self._file_manager.write_file(filepath, conversation_as_text)

    def _build_conversation_filepath(
        self, conversation_id: ConversationId
    ) -> PathWrapper:
        return self._build_chat_path(conversation_id)

    def _build_chat_path(self, conversation_id: ConversationId) -> PathWrapper:
        return self._chats_dir / (conversation_id + "." + CHAT_EXT)

    def _is_chat_file(self, path_wrapper: PathWrapper) -> bool:
        assert self._file_manager.path_exists(path_wrapper)
        if self._file_manager.path_is_dir(path_wrapper):
            return False
        return CHAT_NAME_PATTERN.match(path_wrapper.name) is not None

    def _find_max_file_number(self, directory_path: PathWrapper) -> int | None:
        assert self._file_manager.path_is_dir(directory_path)
        assert self._file_manager.path_exists(directory_path)

        max_number = -1
        ignored_count = 0
        for path_wrapper in self._file_manager.get_children(directory_path):
            if self._file_manager.path_is_dir(path_wrapper):
                ignored_count += 1
                continue
            match = CHAT_NAME_PATTERN.match(path_wrapper.name)
            if not match:
                ignored_count += 1
                continue
            number = int(path_wrapper.stem)
            if number > max_number:
                max_number = number
        if ignored_count:
            print(f"Se ignoraron {ignored_count} rutas")
        if max_number < 0:
            return None
        return max_number


def create_temporary_delete_path(path_wrapper: PathWrapper) -> PathWrapper:
    return PathWrapper(path_wrapper.path_value.parent) / (
        "_delete_" + path_wrapper.name + ".tmp"
    )
