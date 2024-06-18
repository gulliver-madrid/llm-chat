from typing import Sequence
from unittest.mock import MagicMock, Mock


from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper

from src.infrastructure.chat_repository.implementer import (
    ChatRepositoryImplementer,
    DataLocation,
    SafeFileContentMover,
)


def test_move_chat_files_from_data_dir_to_chat_dir() -> None:
    mock_file_manager = Mock(spec=FileManagerProtocol)
    mock_data_location = MagicMock(spec=DataLocation)
    repository_implementer = ChatRepositoryImplementer()
    repository_implementer.init(mock_data_location, mock_file_manager)
    content_mover = Mock(spec=SafeFileContentMover)
    repository_implementer._content_mover = (  # pyright: ignore [reportPrivateUsage]
        content_mover
    )

    files = [Mock(spec=PathWrapper), Mock(spec=PathWrapper)]
    files[0].name = "no_es_un_chat.txt"
    files[1].name = "0001.chat"

    def mock_get_children(data_dir: PathWrapper) -> Sequence[PathWrapper]:
        if data_dir is mock_data_location.data_dir:
            return files
        elif data_dir is mock_data_location.chats_dir:
            return []
        else:
            raise ValueError()

    def mock_is_dir(p: PathWrapper) -> bool:
        if p in files:
            return False
        return True

    mock_file_manager.get_children.side_effect = mock_get_children
    mock_file_manager.path_exists.return_value = True
    mock_file_manager.path_is_dir.side_effect = mock_is_dir

    mock_dest_path = Mock(spec=PathWrapper)
    mock_data_location.chats_dir.__truediv__.return_value = mock_dest_path

    repository_implementer.move_chat_files_from_data_dir_to_chat_dir()

    content_mover.move_content.assert_called_once()
