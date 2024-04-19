from pathlib import Path


_MAIN_DIRECTORY = Path(__file__).parents[2]


def get_main_directory() -> Path:
    return _MAIN_DIRECTORY
