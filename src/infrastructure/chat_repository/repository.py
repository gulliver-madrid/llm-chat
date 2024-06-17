from collections.abc import Sequence

from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper

from src.infrastructure.now import TimeManager
from src.models.shared import CompleteMessage, ConversationId, ConversationText
from src.serde import serialize_conversation
from src.serde.deserialize import deserialize_conversation_text_into_messages
from src.serde.shared import SCHEMA_VERSION

from .implementer import ChatRepositoryImplementer


class ChatRepository:
    def __init__(
        self,
        main_directory: PathWrapper,
        *,
        file_manager: FileManager | None = None,
        time_manager: TimeManager | None = None,
        chat_repository_implementer: ChatRepositoryImplementer | None = None,
    ) -> None:
        self._file_manager = file_manager or FileManager()
        self._time_manager = time_manager or TimeManager()
        self._chat_repository_implementer = (
            chat_repository_implementer or ChatRepositoryImplementer()
        )
        self.__data_dir = main_directory / "data"
        self._chats_dir = self.__data_dir / "chats"
        self._chat_repository_implementer.init(
            self.__data_dir, self._chats_dir, self._file_manager
        )
        self._setup_file_system()

    def get_conversation_ids(self) -> list[ConversationId]:
        return self._chat_repository_implementer.get_conversation_ids()

    def save_messages(self, complete_messages: Sequence[CompleteMessage]) -> None:
        conversation_id = self._chat_repository_implementer.get_new_conversation_id()
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
        filepath = self._chat_repository_implementer.build_chat_path(conversation_id)
        return ConversationText(self._file_manager.read_file(filepath), SCHEMA_VERSION)

    def _setup_file_system(self) -> None:
        self._file_manager.mkdir_if_not_exists(self.__data_dir)
        self._file_manager.mkdir_if_not_exists(self._chats_dir)
        self._chat_repository_implementer.move_chat_files_from_data_dir_to_chat_dir()

    def _save_conversation(
        self, conversation_id: ConversationId, conversation_as_text: str
    ) -> None:
        filepath = self._chat_repository_implementer.build_chat_path(conversation_id)
        self._file_manager.write_file(filepath, conversation_as_text)
