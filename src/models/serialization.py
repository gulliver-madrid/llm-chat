from dataclasses import dataclass
from typing import NewType, Sequence, cast

from src.models.parsed_line import ParsedLine, TagType
from src.models.shared import ChatMessage, CompleteMessage, Model, ModelName
from src.models_data import get_models

ConversationId = NewType("ConversationId", str)


NUMBER_OF_DIGITS = 4
SCHEMA_VERSION = "0.2"


@dataclass(frozen=True)
class Conversation:
    id: ConversationId
    schema_version: str
    number_of_messages: int
    current_time: str
    messages: Sequence[CompleteMessage]


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


def convert_conversation_text_into_messages(
    text: str, *, preserve_model: bool = False, check_model_exists: bool = True
) -> list[CompleteMessage]:
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


def cast_string_to_conversation_id(string: str) -> ConversationId:
    if not string.isdigit() or len(string) != NUMBER_OF_DIGITS:
        raise ValueError(f'"{string} "no pudo convertirse en un ConversationId')
    return cast(ConversationId, string)


def convert_text_to_conversation_object(
    text: str, *, preserve_model: bool = False, check_model_exists: bool = True
) -> Conversation:
    conversation_id = None
    number_of_messages = None
    current_time = None

    lines = text.split("\n")
    for line in lines:
        parsed = ParsedLine(line)
        if parsed.get_tag_type() == TagType.META:
            key, value = parsed.get_property()
            match key:
                case "id":
                    assert not conversation_id
                    conversation_id = ConversationId(value)
                case "schema_version":
                    assert value == SCHEMA_VERSION
                case "number_of_messages":
                    assert number_of_messages is None
                    assert value.isdigit()
                    number_of_messages = int(value)
                case "current_time":
                    assert current_time is None
                    current_time = value
                case _:
                    raise ValueError(f"Key {key} not recognized")

    assert conversation_id
    assert number_of_messages
    assert current_time
    return Conversation(
        conversation_id,
        SCHEMA_VERSION,
        number_of_messages,
        current_time,
        convert_conversation_text_into_messages(
            text, preserve_model=preserve_model, check_model_exists=check_model_exists
        ),
    )


def create_role_tag(complete_message: CompleteMessage) -> str:
    message = complete_message.chat_msg
    tag_identifier = f"ROLE {message.role.upper()}"
    if model := complete_message.model:
        assert message.role == "assistant"
        return create_tag(tag_identifier, ("model", model.model_name))
    return create_tag(tag_identifier)


def create_meta_tag(key: str, value: object) -> str:
    return create_tag_with_property(TagType.META, key, value)


def create_tag_with_property(tag_type: TagType, key: str, value: object) -> str:
    return create_tag(tag_type.value.upper(), (key, value))


def create_tag(tag_identifier: str, property: tuple[str, object] | None = None) -> str:
    assert tag_identifier.isupper()
    parts = [tag_identifier]
    if property:
        key, value = property
        extra = f"{key}={value}"
        parts.append(extra)
    inner = " ".join(parts)
    return f"[{inner}]"
