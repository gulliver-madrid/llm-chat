from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper
from src.python_modules.FileSystemWrapper.safe_file_remover import SafeFileRemover

from src.models.shared import ConversationId
from src.setup_logging import configure_logger
from .chat_file_detecter import CHAT_EXT, ChatFileDetecter
from .conversation_id_provider import FreeConversationIdProvider

logger = configure_logger(__name__)


class ChatRepositoryImplementer:
    """Only access to disk using FileManager"""

    is_initialized: bool = False

    def init(
        self,
        data_dir: PathWrapper,
        chats_dir: PathWrapper,
        file_manager: FileManager,
    ) -> None:
        assert not self.is_initialized
        self._file_manager = file_manager
        self._chat_detecter = ChatFileDetecter(self._file_manager)
        self._content_mover = SafeFileContentMover(self._file_manager)
        self._conversation_id_provider = FreeConversationIdProvider(
            self._file_manager, self._chat_detecter, chats_dir
        )
        self.__data_dir = data_dir
        self._chats_dir = chats_dir
        self.is_initialized = True

    def move_chat_files_from_data_dir_to_chat_dir(self) -> None:
        """
        In the previous version, chat files were directly stored in the data directory.
        This function migrates them to the chat directory, ensuring that the coherence
        of the ids is maintained throughout the process.
        """
        assert self.is_initialized
        data_dir_children = self._file_manager.get_children(self.__data_dir)
        files_to_move = self._chat_detecter.filter_chat_files(data_dir_children)
        for path in files_to_move:
            new_id = self.get_new_conversation_id()
            new_path = self.build_chat_path(new_id)
            self._content_mover.move_content(path, new_path)

    def build_chat_path(self, conversation_id: ConversationId) -> PathWrapper:
        filename = conversation_id + "." + CHAT_EXT
        return self._chats_dir / filename

    def get_new_conversation_id(self) -> ConversationId:
        return self._conversation_id_provider.get_next_free_conversation_id()


class SafeFileContentMover:
    def __init__(self, file_manager: FileManager):
        self._file_manager = file_manager
        self._file_remover = SafeFileRemover(self._file_manager)

    def move_content(self, source: PathWrapper, dest: PathWrapper) -> None:
        content = self._file_manager.read_file(source)
        assert not self._file_manager.path_exists(dest), dest
        self._file_manager.write_file(dest, content)
        self._file_remover.remove_file(source)
