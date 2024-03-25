from pathlib import Path
import re
from typing import NewType, Sequence, cast

from src.infrastructure.ahora import get_current_time
from src.models.parsed_line import ParsedLine, TagType
from src.models.shared import ChatMessage, CompleteMessage, ModelName


NUMBER_OF_DIGITS = 4
SCHEMA_VERSION = "0.2"

ConversationId = NewType("ConversationId", str)


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


def cast_string_to_conversation_id(string: str) -> ConversationId:
    assert string.isdigit()
    assert len(string) == NUMBER_OF_DIGITS
    return cast(ConversationId, string)


class ConversationBuilder:
    def __init__(self) -> None:
        self._texts: list[str] = []

    def add_meta_tag(self, name: str, value: object) -> None:
        self._texts.append(create_meta_tag(name, value))

    def add_role_tag(self, complete_message: CompleteMessage) -> None:
        self._texts.append(create_role_tag(complete_message))

    def add_line_break(self) -> None:
        self._texts.append("")

    def add_text(self, text: str) -> None:
        self._texts.append(text)

    def build(self) -> str:
        return "\n".join(self._texts)


def convert_conversation_into_messages(text: str) -> list[CompleteMessage]:
    lines = text.split("\n")
    role_tags_indexes: list[int] = []
    for i, line in enumerate(lines):
        parsed = ParsedLine(line)
        if parsed.get_tag_type() == TagType.ROLE:
            role_tags_indexes.append(i)

    complete_messages: list[CompleteMessage] = []
    role_tags_count = len(role_tags_indexes)
    for i in range(role_tags_count):
        start = role_tags_indexes[i] + 1
        if i < role_tags_count - 1:
            end = role_tags_indexes[i + 1]
            this_role_lines = lines[start:end]
        else:
            assert i == role_tags_count - 1
            this_role_lines = lines[start:]
        this_role_text = "\n".join(this_role_lines).strip()
        role = ParsedLine(lines[role_tags_indexes[i]]).get_role()
        assert isinstance(role, str)
        chat_message = ChatMessage(
            role=role,
            content=this_role_text,
        )
        complete_messages.append(CompleteMessage(chat_msg=chat_message, model=None))

    return complete_messages


def create_conversation_texts(
    complete_messages: Sequence[CompleteMessage],
    conversation_id: ConversationId,
    current_time: str,
) -> str:
    number_of_messages = len(complete_messages)
    builder = ConversationBuilder()
    builder.add_meta_tag("id", conversation_id)
    builder.add_line_break()
    builder.add_meta_tag("schema_version", SCHEMA_VERSION)
    builder.add_meta_tag("number_of_messages", number_of_messages)
    builder.add_meta_tag("current_time", current_time)
    for complete_message in complete_messages:
        builder.add_line_break()
        builder.add_role_tag(complete_message)
        message = complete_message.chat_msg
        assert isinstance(message.content, str)
        builder.add_text(message.content)
    return builder.build()


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
        model_name: ModelName = model.model_name
        optional_model_info = f" model={model_name}"
        assert message.role == "assistant"
    return f"[ROLE {message.role.upper()}{optional_model_info}]"


def create_meta_tag(tag_name: str, value: object) -> str:
    return f"[META {tag_name}={value}]"
