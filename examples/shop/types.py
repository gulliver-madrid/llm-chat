from collections.abc import Mapping, Sequence
from typing import TypeGuard


def is_object_mapping(obj: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(obj, Mapping)


def is_object_sequence(obj: object) -> TypeGuard[Sequence[object]]:
    return isinstance(obj, Sequence)


def is_str_sequence(obj: object) -> TypeGuard[Sequence[str]]:
    if not is_object_sequence(obj):
        return False
    return all(isinstance(item, str) for item in obj)
