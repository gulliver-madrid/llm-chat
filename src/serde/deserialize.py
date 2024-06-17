from dataclasses import dataclass
from enum import Enum
import re
from typing import Final, Mapping

from src.models.shared import (
    ChatMessage,
    CompleteMessage,
    ConversationId,
    ConversationText,
    Model,
    ModelName,
)
from src.models_data import get_models

from .shared import SCHEMA_VERSION, Conversation


class TagType(Enum):
    """Type of a tag"""

    META = "META"
    ROLE = "ROLE"


@dataclass(frozen=True)
class RoleInfo:
    role: str
    model_name: ModelName | None = None


tag_types: Final[Mapping[str, TagType]] = dict(META=TagType.META, ROLE=TagType.ROLE)
possible_roles: Final = ("system", "user", "assistant", "tool")


@dataclass
class ParsedLine:
    line: str

    def __post_init__(
        self,
    ) -> None:
        assert "\n" not in self.line
        pattern = re.compile(r"^\[(META|ROLE) .*\]$")
        self.match = pattern.match(self.line)

    def is_tag(self) -> bool:
        return bool(self.match)

    def get_tag_type(self) -> TagType | None:
        if not self.is_tag():
            return None
        assert self.match
        return tag_types[self.match.groups()[0]]

    def get_property(self) -> tuple[str, str]:
        assert self.is_tag()
        pattern = re.compile(r"^\[(META|ROLE)( [A-Z]+)? (.*)\]$")
        match = pattern.match(self.line)
        if not match:
            raise ValueError(self)
        second = match.groups()[2]
        second = second.strip()
        property_match = re.match(r"([a-z_]+)=([ .\-:_a-z0-9]+)", second)
        if not property_match:
            raise ValueError(self)
        groups = property_match.groups()
        return (groups[0], groups[1])

    def get_role_info(self) -> RoleInfo | None:
        if self.get_tag_type() is not TagType.ROLE:
            return None
        assert self.match
        pattern = re.compile(r"^\[ROLE ([A-Z]+)(.*)\]$")
        match = pattern.match(self.line)
        if not match:
            raise ValueError(pattern)
        first = match.groups()[0]
        if not isinstance(first, str) or not first.isupper():
            raise ValueError(first)
        if (role := first.lower()) not in possible_roles:
            raise ValueError("Role unknown: " + first)
        second = match.groups()[1].strip()
        if not second:
            return RoleInfo(role)
        model_match = re.match(r"model=([.-_a-z0-9]+)", second)
        if not model_match:
            raise ValueError(second)
        model_name = ModelName(model_match.groups()[0])
        return RoleInfo(role, model_name)


def deserialize_into_conversation_object(
    conversation_text: ConversationText,
    *,
    preserve_model: bool = False,
    check_model_exists: bool = True,
) -> Conversation:
    conversation_id = None
    number_of_messages = None
    current_time = None

    assert conversation_text.schema_version == SCHEMA_VERSION
    text = conversation_text.text

    lines = text.split("\n")
    for line in lines:
        parsed = ParsedLine(line)
        if parsed.get_tag_type() == TagType.META:
            key, value = parsed.get_property()
            if key == "id":
                assert not conversation_id
                conversation_id = ConversationId(value)
            elif key == "schema_version":
                assert value == SCHEMA_VERSION
            elif key == "number_of_messages":
                assert number_of_messages is None
                assert value.isdigit()
                number_of_messages = int(value)
            elif key == "current_time":
                assert current_time is None
                current_time = value
            else:
                raise ValueError(f"Key {key} not recognized")

    assert conversation_id
    assert number_of_messages
    assert current_time
    return Conversation(
        conversation_id,
        SCHEMA_VERSION,
        number_of_messages,
        current_time,
        deserialize_conversation_text_into_messages(
            conversation_text,
            preserve_model=preserve_model,
            check_model_exists=check_model_exists,
        ),
    )


def deserialize_conversation_text_into_messages(
    conversation_text: ConversationText,
    *,
    preserve_model: bool = False,
    check_model_exists: bool = True,
) -> list[CompleteMessage]:
    assert conversation_text.schema_version == SCHEMA_VERSION
    text = conversation_text.text

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
        role_info = ParsedLine(lines[role_tags_indexes[i]]).get_role_info()
        assert role_info
        chat_message = ChatMessage(
            role=role_info.role,
            content=this_role_text,
        )
        model_name = role_info.model_name if preserve_model else None
        model = None
        if model_name:
            model = determine_model(model_name, check_existence=check_model_exists)

        complete_messages.append(CompleteMessage(chat_msg=chat_message, model=model))

    return complete_messages


def determine_model(
    model_name: ModelName, *, check_existence: bool = True
) -> Model | None:
    models = get_models()
    for model in models:
        if model_name == model.model_name:
            found_model = model
            break
    else:
        if check_existence:
            raise ValueError(f"Model not found: {model_name}")
        else:
            found_model = Model(None, model_name)
    return found_model
