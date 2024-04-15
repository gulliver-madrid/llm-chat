from unittest.mock import Mock

from src.python_modules.FileSystemWrapper.file_manager import FileManager

from src.infrastructure.repository import ChatRepository


def test_create_chat_repository() -> None:
    file_manager_mock = Mock(spec=FileManager)
    file_manager_mock.get_children.return_value = []

    ChatRepository(file_manager_mock)

    file_manager_mock.mkdir_if_not_exists.assert_called()
