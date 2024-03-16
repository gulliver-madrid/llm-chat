from typing import Sequence, TypeVar

T = TypeVar("T")


def remove_duplicates(seq: Sequence[T]) -> list[T]:
    """Removes duplicates while maintaining the original sequence order."""
    return list(dict.fromkeys(seq))
