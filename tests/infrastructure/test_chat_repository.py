from typing import Any
from unittest.mock import MagicMock, Mock


from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper

from src.infrastructure.chat_repository.implementer import ChatRepositoryImplementer
from src.infrastructure.chat_repository.repository import ChatRepository


def test_create_chat_repository_trigger_filesystem_setup() -> None:
    file_manager_mock = Mock(spec=FileManagerProtocol)
    file_manager_mock.get_children.return_value = []
    chat_repository_implementer_mock = Mock(spec=ChatRepositoryImplementer)
    main_directory_mock = MagicMock(spec=PathWrapper)

    def truediv(self: Any, name: str) -> Any:
        pw_mock = MagicMock(spec=PathWrapper)
        pw_mock.name = name
        pw_mock.__truediv__ = truediv
        return pw_mock

    main_directory_mock.__truediv__ = truediv

    ChatRepository(
        main_directory_mock,
        file_manager=file_manager_mock,
        chat_repository_implementer=chat_repository_implementer_mock,
    )

    file_manager_mock.mkdir_if_not_exists.assert_called()

    calls = file_manager_mock.mkdir_if_not_exists.mock_calls
    assert calls[0].args[0].name == "data"
    assert calls[1].args[0].name == "chats"

    chat_repository_implementer_mock.move_chat_files_from_data_dir_to_chat_dir.assert_called_once()
