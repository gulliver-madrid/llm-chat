from pathlib import Path, PurePath


class FileManager:
    """Manage all the file R/W operations"""

    def mkdir_if_not_exists(self, path: PurePath) -> None:
        Path(path).mkdir(exist_ok=True)

    def get_children(self, path: PurePath) -> list[PurePath]:
        return [PurePath(p) for p in Path(path).iterdir()]

    def path_exists(self, path: PurePath) -> bool:
        return Path(path).exists()

    def path_is_dir(self, path: PurePath) -> bool:
        return Path(path).is_dir()

    def write_file(self, path: PurePath, text: str) -> None:
        with open(Path(path), "w", encoding="utf-8") as file:
            file.write(text)

    def read_file(self, path: PurePath) -> str:
        with open(Path(path), "r", encoding="utf-8") as file:
            text = file.read()
        return text

    def rename_path(self, path: PurePath, new_path: PurePath) -> None:
        Path(path).rename(Path(new_path))

    def unlink_path(self, path: PurePath) -> None:
        Path(path).unlink()
