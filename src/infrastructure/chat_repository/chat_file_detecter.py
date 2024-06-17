import re
from typing import Iterable


from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)
from src.python_modules.FileSystemWrapper.path_wrapper import PathWrapper

from src.serde import NUMBER_OF_DIGITS

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")


class ChatFileDetecter:
    """Clase que identifica y filtra los chat files de un iterable de PathWrappers"""

    def __init__(self, file_manager: FileManagerProtocol):
        self._file_manager = file_manager

    def filter_chat_files(
        self, path_wrappers: Iterable[PathWrapper]
    ) -> list[PathWrapper]:
        return [p for p in path_wrappers if self._is_chat_file(p)]

    def _is_chat_file(self, path_wrapper: PathWrapper) -> bool:
        assert self._file_manager.path_exists(path_wrapper)
        if self._file_manager.path_is_dir(path_wrapper):
            return False
        return match_chat_file_pattern(path_wrapper.name)


def match_chat_file_pattern(filename: str) -> bool:
    assert "/" not in filename
    assert "\\" not in filename
    return bool(CHAT_NAME_PATTERN.match(filename))
