from src.utils import remove_duplicates


def test_remove_duplicates() -> None:
    empty_list: list[int] = []
    assert remove_duplicates(empty_list) == []
    assert remove_duplicates([1, 2, 3]) == [1, 2, 3]
    assert remove_duplicates([10, 20, 10, 30, 40, 40]) == [10, 20, 30, 40]
    assert remove_duplicates("zabbc") == [
        "z",
        "a",
        "b",
        "c",
    ]
