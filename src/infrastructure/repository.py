from pathlib import Path
import re
from typing import Sequence

from src.infrastructure.ahora import get_current_time
from src.models.serialization import (
    NUMBER_OF_DIGITS,
    ConversationId,
    cast_string_to_conversation_id,
    create_conversation_texts,
)
from src.models.shared import CompleteMessage

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")


class Repository:
    def __init__(self) -> None:
        self.__data_dir = Path(__file__).parent.parent.parent / "data"
        self._chats_dir = self.__data_dir / "chats"
        self.__data_dir.mkdir(exist_ok=True)
        self._chats_dir.mkdir(exist_ok=True)
        chat_files_in_data_dir = list(self.__data_dir.iterdir())
        for path in chat_files_in_data_dir:
            if is_chat_file(path):
                new_id = self._get_new_conversation_id()
                text = self._read_file(path)
                new_path = self._build_chat_path(new_id)
                assert not new_path.exists(), new_path
                self._write_file(new_path, text)
                tmp_delete_path_ = create_temporary_delete_path(path)
                path.rename(tmp_delete_path_)
                assert not path.exists()
                tmp_delete_path_.unlink()

    def save(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._get_new_conversation_id()
        conversation = create_conversation_texts(
            complete_messages, conversation_id, get_current_time()
        )
        self._save_conversation(conversation_id, conversation)

    def _get_new_conversation_id(self) -> ConversationId:
        max_number = find_max_file_number(self._chats_dir)
        new_number = (max_number + 1) if max_number is not None else 0
        assert 0 <= new_number < 10**NUMBER_OF_DIGITS
        return cast_string_to_conversation_id(str(new_number).zfill(NUMBER_OF_DIGITS))

    def _save_conversation(
        self, conversation_id: ConversationId, conversation: str
    ) -> None:
        filepath = self._build_conversation_filepath(conversation_id)
        self._write_file(filepath, conversation)

    def load_conversation(self, conversation_id: ConversationId) -> str:
        filepath = self._build_conversation_filepath(conversation_id)
        return self._read_file(filepath)

    def _build_conversation_filepath(self, conversation_id: ConversationId) -> Path:
        return self._build_chat_path(conversation_id)

    def _write_file(self, path: Path, text: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

    def _read_file(self, path: Path) -> str:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    def _build_chat_path(self, conversation_id: ConversationId) -> Path:
        return self._chats_dir / (conversation_id + "." + CHAT_EXT)


def find_max_file_number(directory_path: Path) -> int | None:
    assert directory_path.is_dir()
    assert directory_path.exists()

    max_number = -1

    for path in directory_path.iterdir():
        if path.is_dir():
            print(f"Ignorando ruta {path} por ser un directorio")
            continue
        match = CHAT_NAME_PATTERN.match(path.name)
        assert match, "Archivo incorrecto: " + str(path)
        number = int(path.stem)
        if number > max_number:
            max_number = number

    return max_number if max_number >= 0 else None


def is_chat_file(path: Path) -> bool:
    assert path.exists()
    if path.is_dir():
        return False

    return CHAT_NAME_PATTERN.match(path.name) is not None


def create_temporary_delete_path(path: Path) -> Path:
    return path.parent / ("_delete_" + path.name + ".tmp")
