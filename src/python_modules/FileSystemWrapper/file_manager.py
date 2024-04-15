from .path_wrapper import PathWrapper


class FileManager:
    """Manage all the file R/W operations"""

    def mkdir_if_not_exists(self, path_wrapper: PathWrapper) -> None:
        path_wrapper.path_value.mkdir(exist_ok=True)

    def get_children(self, path_wrapper: PathWrapper) -> list[PathWrapper]:
        return [PathWrapper(p) for p in path_wrapper.path_value.iterdir()]

    def path_exists(self, path_wrapper: PathWrapper) -> bool:
        return path_wrapper.path_value.exists()

    def path_is_dir(self, path_wrapper: PathWrapper) -> bool:
        return path_wrapper.path_value.is_dir()

    def write_file(self, path_wrapper: PathWrapper, text: str) -> None:
        with open(path_wrapper.path_value, "w", encoding="utf-8") as file:
            file.write(text)

    def read_file(self, path_wrapper: PathWrapper) -> str:
        with open(path_wrapper.path_value, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    def rename_path(self, path_wrapper: PathWrapper, new_path: PathWrapper) -> None:
        path_wrapper.path_value.rename(new_path.path_value)

    def unlink_path(self, path_wrapper: PathWrapper) -> None:
        path_wrapper.path_value.unlink()
