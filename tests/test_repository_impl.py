from unittest.mock import Mock
from src.infrastructure.chat_repository_implementer import (
    ChatRepositoryImplementer,
    match_chat_file_pattern,
)
from src.python_modules.FileSystemWrapper.file_manager import FileManager
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper


def test_match_filename() -> None:
    assert match_chat_file_pattern("0033.chat")
    assert not match_chat_file_pattern("33.chat")
    assert not match_chat_file_pattern("033.chat")
    assert not match_chat_file_pattern("00033.chat")
    assert not match_chat_file_pattern("0033.txt")
    assert not match_chat_file_pattern("0033")
    assert not match_chat_file_pattern("hola.chat")


def test_chat_repository_impl_initialization() -> None:
    repository = ChatRepositoryImplementer()
    repository.init(
        Mock(spec=PathWrapper), Mock(spec=PathWrapper), Mock(spec=FileManager)
    )
    assert repository.is_initialized
