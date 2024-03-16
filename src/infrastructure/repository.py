from pathlib import Path
import re
from typing import Sequence

from src.infrastructure.ahora import get_current_time
from src.infrastructure.client_wrapper import CompleteMessage

NUMBER_OF_DIGITS = 4
SCHEMA_VERSION = "0.2"


class ChatRepository:
    def __init__(self) -> None:
        self._data_dir = Path(__file__).parent.parent.parent / "data"
        self._data_dir.mkdir(exist_ok=True)

    def save(self, complete_messages: Sequence[CompleteMessage]) -> None:
        max_number = find_max_file_number(self._data_dir)
        new_number = max_number + 1 if max_number is not None else 0
        assert 0 <= new_number < 10**NUMBER_OF_DIGITS
        conversation_id = str(new_number).zfill(NUMBER_OF_DIGITS)
        texts = [f"[META id={conversation_id}]\n"]
        number_of_messages = len(complete_messages)
        texts.append(create_meta_tag("schema_version", SCHEMA_VERSION))
        texts.append(create_meta_tag("number_of_messages", number_of_messages))
        texts.append(create_meta_tag("current_time", get_current_time()))
        for complete_message in complete_messages:
            message = complete_message.chat_msg
            optional_model_info = ""
            if model := complete_message.model:
                optional_model_info = f" model={model}"
            texts.append(f"\n[ROLE {message.role.upper()}{optional_model_info}]")
            assert isinstance(message.content, str)
            texts.append(message.content)
        assert conversation_id.isdigit()
        with open(
            self._data_dir / (conversation_id + ".chat"), "w", encoding="utf-8"
        ) as file:
            file.write("\n".join(texts))


def find_max_file_number(directory_path: Path) -> int | None:
    assert directory_path.is_dir()
    assert directory_path.exists()

    pattern = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.chat$")

    max_number = -1

    for path in directory_path.iterdir():
        assert not path.is_dir()
        match = pattern.match(path.name)
        assert match, "Archivo incorrecto" + str(path)
        number = int(path.stem)
        if number > max_number:
            max_number = number

    return max_number if max_number >= 0 else None


def create_meta_tag(tag_name: str, value: object) -> str:
    return f"[META {tag_name}={value}]"
