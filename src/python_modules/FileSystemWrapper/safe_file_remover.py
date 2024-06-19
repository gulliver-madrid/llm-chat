from pathlib import PurePath
from .file_manager_protocol import (
    FileManagerProtocol,
)


class SafeFileRemover:
    """Only access to disk using an object that implements FileManagerProtocol"""

    def __init__(self, file_manager: FileManagerProtocol) -> None:
        self._file_manager = file_manager

    def remove_file(self, path: PurePath) -> None:
        tmp_delete_path = create_temporary_delete_path(path)
        self._file_manager.rename_path(path, tmp_delete_path)
        assert not self._file_manager.path_exists(path)
        self._file_manager.unlink_path(tmp_delete_path)


def create_temporary_delete_path(path: PurePath) -> PurePath:
    return path.parent / ("_delete_" + path.name + ".tmp")
