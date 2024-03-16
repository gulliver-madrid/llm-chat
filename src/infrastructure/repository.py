from pathlib import Path
import re
from typing import Sequence

from src.infrastructure.ahora import get_current_time
from src.infrastructure.client_wrapper import CompleteMessage

NUMBER_OF_DIGITS = 4
SCHEMA_VERSION = "0.2"


class Repository:
    def __init__(self) -> None:
        self._data_dir = Path(__file__).parent.parent.parent / "data"
        self._data_dir.mkdir(exist_ok=True)

    def save(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._get_new_conversation_id()
        texts = create_conversation_texts(complete_messages, conversation_id)
        self._save_conversation(conversation_id, texts)

    def _get_new_conversation_id(self) -> str:
        max_number = find_max_file_number(self._data_dir)
        new_number = max_number + 1 if max_number is not None else 0
        assert 0 <= new_number < 10**NUMBER_OF_DIGITS
        return str(new_number).zfill(NUMBER_OF_DIGITS)

    def _save_conversation(self, conversation_id: str, texts: Sequence[str]) -> None:
        assert conversation_id.isdigit()
        filepath = self._data_dir / (conversation_id + ".chat")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("\n".join(texts))


def create_conversation_texts(
    complete_messages: Sequence[CompleteMessage], conversation_id: str
) -> Sequence[str]:
    number_of_messages = len(complete_messages)
    texts = [create_meta_tag("id", conversation_id) + "\n"]
    texts.append(create_meta_tag("schema_version", SCHEMA_VERSION))
    texts.append(create_meta_tag("number_of_messages", number_of_messages))
    texts.append(create_meta_tag("current_time", get_current_time()))
    for complete_message in complete_messages:
        texts.append("\n" + create_role_tag(complete_message))
        message = complete_message.chat_msg
        assert isinstance(message.content, str)
        texts.append(message.content)
    return texts


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


def create_role_tag(complete_message: CompleteMessage) -> str:
    message = complete_message.chat_msg
    optional_model_info = ""
    if model := complete_message.model:
        optional_model_info = f" model={model}"
        assert message.role == "assistant"
    return f"[ROLE {message.role.upper()}{optional_model_info}]"


def create_meta_tag(tag_name: str, value: object) -> str:
    return f"[META {tag_name}={value}]"
