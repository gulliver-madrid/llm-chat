from typing import Sequence, TypeVar

T = TypeVar("T")


def remove_duplicates(seq: Sequence[T]) -> list[T]:
    return list(dict.fromkeys(seq))
