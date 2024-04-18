from src.infrastructure.chat_repository_implementer import match_chat_file_pattern


def test_match_filename() -> None:
    assert match_chat_file_pattern("0033.chat")
    assert not match_chat_file_pattern("33.chat")
    assert not match_chat_file_pattern("033.chat")
    assert not match_chat_file_pattern("00033.chat")
    assert not match_chat_file_pattern("0033.txt")
    assert not match_chat_file_pattern("0033")
    assert not match_chat_file_pattern("hola.chat")
