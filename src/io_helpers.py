import time

from rich import print

ERROR = "[bright_red]"
CALL_TO_ACTION = "[bright_cyan]"
HIGHLIGHT_ROLE = "[light_green]"
NEUTRAL_MSG = "[dark_goldenrod]"

BLUE_VIOLET_COLOR = "[blue_violet]"

BOLD_STYLE = "[bold]"


def end(s: str) -> str:
    """Create a end tag"""
    assert s[0] == "["
    assert s[-1] == "]"
    return f"[/{s[1:-1]}]"


def get_input(text: str) -> str:
    """Prompts the user to provide an input, in a styled way"""
    print(
        CALL_TO_ACTION + f"\n{text}\n> ",
        end="",
    )
    return input()


def show_error_msg(text: str) -> None:
    """Displays an error message with the given text and make a short pause before returning"""
    print(ERROR + f"\n{text}")
    time.sleep(1)


def apply_tag(s: str, tag: str) -> str:
    assert tag.startswith("[")
    assert tag.endswith("]")
    return tag + s + end(tag)


def highlight_role(role_string: str) -> str:
    return HIGHLIGHT_ROLE + role_string + end(HIGHLIGHT_ROLE)


def display_neutral_msg(text: str) -> None:
    print(NEUTRAL_MSG + text)
