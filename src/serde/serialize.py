from typing import Sequence, cast

from src.domain import CompleteMessage, ConversationId

from .deserialize import TagType
from .shared import SCHEMA_VERSION


NUMBER_OF_DIGITS = 4


class SerializedConversationBuilder:
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


def serialize_conversation(
    complete_messages: Sequence[CompleteMessage],
    conversation_id: ConversationId,
    current_time: str,
) -> str:
    number_of_messages = len(complete_messages)
    builder = SerializedConversationBuilder()
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


def convert_digits_to_conversation_id(string: str) -> ConversationId:
    if not string.isdigit() or len(string) > NUMBER_OF_DIGITS:
        raise ValueError(f'"{string} "no pudo convertirse en un ConversationId')
    return cast(ConversationId, string.zfill(NUMBER_OF_DIGITS))


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
