from pathlib import PurePath

_MAIN_DIRECTORY = PurePath(__file__).parents[2]


def get_main_directory() -> PurePath:
    return _MAIN_DIRECTORY
