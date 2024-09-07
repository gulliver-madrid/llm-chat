import re
from pathlib import PurePath
from typing import Iterable

from src.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)

from src.serde import NUMBER_OF_DIGITS

CHAT_EXT = "chat"
CHAT_NAME_PATTERN = re.compile(rf"^(\d{{{NUMBER_OF_DIGITS}}})\.{CHAT_EXT}$")


class ChatFileDetecter:
    """Clase que identifica y filtra los chat files de un iterable de PathWrappers"""

    def __init__(self, file_manager: FileManagerProtocol):
        self._file_manager = file_manager

    def filter_chat_files(self, paths: Iterable[PurePath]) -> list[PurePath]:
        return [p for p in paths if self._is_chat_file(p)]

    def _is_chat_file(self, path: PurePath) -> bool:
        assert self._file_manager.path_exists(path)
        if self._file_manager.path_is_dir(path):
            return False
        return match_chat_file_pattern(path.name)


def match_chat_file_pattern(filename: str) -> bool:
    assert "/" not in filename
    assert "\\" not in filename
    return bool(CHAT_NAME_PATTERN.match(filename))
