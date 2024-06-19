from typing import Final
from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper
from src.python_modules.FileSystemWrapper.safe_file_remover import SafeFileRemover

from src.domain import ConversationId
from src.setup_logging import configure_logger

from .chat_file_detecter import CHAT_EXT, ChatFileDetecter
from .conversation_id_provider import FreeConversationIdProvider

logger = configure_logger(__name__)


class DataLocation:
    def __init__(self, main_directory: PathWrapper):
        self._data_dir: Final = main_directory / "data"
        self._chats_dir: Final = self.data_dir / "chats"

    @property
    def data_dir(self) -> PathWrapper:
        return self._data_dir

    @property
    def chats_dir(self) -> PathWrapper:
        return self._chats_dir


class ChatRepositoryImplementer:
    """Only access to disk using an object that implements FileManagerProtocol"""

    is_initialized: bool = False

    def init(
        self,
        data_location: DataLocation,
        file_manager: FileManagerProtocol,
    ) -> None:
        assert not self.is_initialized
        self._file_manager = file_manager
        self._chat_detecter = ChatFileDetecter(self._file_manager)
        self._conversation_id_provider = FreeConversationIdProvider(
            self._file_manager, self._chat_detecter, data_location.chats_dir
        )
        self._chats_dir = data_location.chats_dir
        self.is_initialized = True

    def get_conversation_ids(self) -> list[ConversationId]:
        assert self.is_initialized
        children = self._file_manager.get_children(self._chats_dir)
        paths = self._chat_detecter.filter_chat_files(children)
        ids: list[ConversationId] = []
        for path in paths:
            id_as_text = path.name.split(".")[0]
            ids.append(ConversationId(id_as_text))
        return ids

    def build_chat_path(self, conversation_id: ConversationId) -> PathWrapper:
        filename = conversation_id + "." + CHAT_EXT
        return self._chats_dir / filename

    def get_new_conversation_id(self) -> ConversationId:
        return self._conversation_id_provider.get_next_free_conversation_id()
