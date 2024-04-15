from .file_manager import FileManager
from .path_wrapper import PathWrapper


class SafeFileRemover:
    def __init__(self, file_manager: FileManager) -> None:
        self._file_manager = file_manager

    def remove_file(self, path_wrapper: PathWrapper) -> None:
        tmp_delete_path = create_temporary_delete_path(path_wrapper)
        self._file_manager.rename_path(path_wrapper, tmp_delete_path)
        assert not self._file_manager.path_exists(path_wrapper)
        self._file_manager.unlink_path(tmp_delete_path)


def create_temporary_delete_path(path_wrapper: PathWrapper) -> PathWrapper:
    return PathWrapper(path_wrapper.path_value.parent) / (
        "_delete_" + path_wrapper.name + ".tmp"
    )
