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


class Repository:
    def __init__(self) -> None:
        self._data_dir = Path(__file__).parent.parent.parent / "data"
        self._data_dir.mkdir(exist_ok=True)

    def save(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._get_new_conversation_id()
        conversation = create_conversation_texts(
            complete_messages, conversation_id, get_current_time()
        )
        self._save_conversation(conversation_id, conversation)

    def _get_new_conversation_id(self) -> ConversationId:
        max_number = find_max_file_number(self._data_dir)
        new_number = max_number + 1 if max_number is not None else 0
        assert 0 <= new_number < 10**NUMBER_OF_DIGITS
        return cast_string_to_conversation_id(str(new_number).zfill(NUMBER_OF_DIGITS))

    def _save_conversation(
        self, conversation_id: ConversationId, conversation: str
    ) -> None:
        filepath = self._build_conversation_filepath(conversation_id)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(conversation)

    def load_conversation(self, conversation_id: ConversationId) -> str:
        filepath = self._build_conversation_filepath(conversation_id)
        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    def _build_conversation_filepath(self, conversation_id: ConversationId) -> Path:
        return self._data_dir / (conversation_id + ".chat")


def find_max_file_number(directory_path: Path) -> int | None:
    assert directory_path.is_dir()
    assert directory_path.exists()

    pattern = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.chat$")

    max_number = -1

    for path in directory_path.iterdir():
        assert not path.is_dir()
        match = pattern.match(path.name)
        assert match, "Archivo incorrecto: " + str(path)
        number = int(path.stem)
        if number > max_number:
            max_number = number

    return max_number if max_number >= 0 else None
