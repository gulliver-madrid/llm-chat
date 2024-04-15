from unittest.mock import Mock

from src.python_modules.FileSystemWrapper.file_manager import FileManager

from src.infrastructure.repository import ChatRepository, ChatRepositoryImplementer


def test_create_chat_repository() -> None:
    file_manager_mock = Mock(spec=FileManager)
    file_manager_mock.get_children.return_value = []
    chat_repository_implementer_mock = Mock(spec=ChatRepositoryImplementer)

    ChatRepository(
        file_manager=file_manager_mock,
        chat_repository_implementer=chat_repository_implementer_mock,
    )

    file_manager_mock.mkdir_if_not_exists.assert_called()

    calls = file_manager_mock.mkdir_if_not_exists.mock_calls
    assert any(call.args[0].name == "data" for call in calls)
    assert any(call.args[0].name == "chats" for call in calls)
    assert not any(call.args[0].name == "another_name" for call in calls)

    chat_repository_implementer_mock.move_chat_files_from_data_dir_to_chat_dir.assert_called_once()
