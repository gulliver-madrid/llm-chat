from pathlib import PurePath
from typing import Any
from unittest.mock import MagicMock, Mock

from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)

from src.infrastructure.chat_repository.implementer import (
    ChatRepositoryImplementer,
)
from src.infrastructure.chat_repository.repository import ChatRepository
from src.infrastructure.now import TimeManager


def test_create_chat_repository_trigger_filesystem_setup() -> None:
    file_manager_mock = Mock(spec=FileManagerProtocol)
    file_manager_mock.get_children.return_value = []
    main_directory_mock = MagicMock(spec=PurePath)

    def truediv(self: Any, name: str) -> Any:
        pw_mock = MagicMock(spec=PurePath)
        pw_mock.name = name
        pw_mock.__truediv__ = truediv
        return pw_mock

    main_directory_mock.__truediv__ = truediv

    ChatRepository(
        main_directory_mock,
        file_manager=file_manager_mock,
        time_manager=Mock(spec=TimeManager),
    )

    file_manager_mock.mkdir_if_not_exists.assert_called()

    calls = file_manager_mock.mkdir_if_not_exists.mock_calls
    assert calls[0].args[0].name == "data"
    assert calls[1].args[0].name == "chats"
