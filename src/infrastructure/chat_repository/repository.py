from collections.abc import Sequence
from pathlib import PurePath
from typing import TYPE_CHECKING

from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)

from src.domain import CompleteMessage, ConversationId, ConversationText
from src.infrastructure.now import TimeManager
from src.protocols import ChatRepositoryProtocol
from src.serde import serialize_conversation
from src.serde.deserialize import deserialize_conversation_text_into_messages
from src.serde.shared import SCHEMA_VERSION

from .implementer import ChatRepositoryImplementer, DataLocation


class ChatRepository:
    def __init__(
        self,
        main_directory: PurePath,
        *,
        file_manager: FileManagerProtocol,
        time_manager: TimeManager,
    ) -> None:
        self._file_manager = file_manager
        self._time_manager = time_manager
        self._implementer = ChatRepositoryImplementer()
        self._data_location = DataLocation(main_directory)
        self._implementer.init(
            self._data_location,
            self._file_manager,
        )
        self._setup_file_system()

    def get_conversation_ids(self) -> list[ConversationId]:
        return self._implementer.get_conversation_ids()

    def save_messages(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._implementer.get_new_conversation_id()
        current_time = self._time_manager.get_current_time()
        conversation = serialize_conversation(
            complete_messages, conversation_id, current_time
        )
        self._save_conversation(conversation_id, conversation)

    def load_conversation(
        self, conversation_id: ConversationId
    ) -> list[CompleteMessage]:
        conversation = self.load_conversation_as_conversation_text(conversation_id)
        return deserialize_conversation_text_into_messages(conversation)

    def load_conversation_as_conversation_text(
        self, conversation_id: ConversationId
    ) -> ConversationText:
        filepath = self._implementer.build_chat_path(conversation_id)
        return ConversationText(self._file_manager.read_file(filepath), SCHEMA_VERSION)

    def _setup_file_system(self) -> None:
        self._file_manager.mkdir_if_not_exists(self._data_location.data_dir)
        self._file_manager.mkdir_if_not_exists(self._data_location.chats_dir)

    def _save_conversation(
        self, conversation_id: ConversationId, conversation_as_text: str
    ) -> None:
        filepath = self._implementer.build_chat_path(conversation_id)
        self._file_manager.write_file(filepath, conversation_as_text)


if TYPE_CHECKING:
    repository: ChatRepository
    protocol: ChatRepositoryProtocol = repository  # pyright: ignore
