from src.serde.deserialize import ParsedLine, TagType

NO_TAGS = [
    "",
    # something before
    " [META id=0001]",
    # something after
    "[META id=0001] ",
    # missing space
    "[METAid]",
]
TAGS_WITH_TYPES = [
    ("[META id=0001]", TagType.META),
    ("[ROLE ASSISTANT model=model_1]", TagType.ROLE),
]


def test_is_tag() -> None:
    for no_tag in NO_TAGS:
        assert_is_tag(False, no_tag)

    for tag, _ in TAGS_WITH_TYPES:
        assert_is_tag(True, tag)


def test_get_tag_type() -> None:
    for no_tag in NO_TAGS:
        assert_tag_type(None, no_tag)

    for tag, expected_type in TAGS_WITH_TYPES:
        assert_tag_type(expected_type, tag)


def assert_is_tag(expected: bool, string: str) -> None:
    assert expected == ParsedLine(string).is_tag()


def assert_tag_type(expected: TagType | None, string: str) -> None:
    assert expected == ParsedLine(string).get_tag_type()
