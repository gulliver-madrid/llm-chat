import time

from rich import print

ERROR = "[bright_red]"
CALL_TO_ACTION = "[bright_cyan]"
HIGHLIGHT_ROLE = "[light_green]"
NEUTRAL_MSG = "[dark_goldenrod]"


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


def highlight_role(role_string: str) -> str:
    return HIGHLIGHT_ROLE + role_string + end(HIGHLIGHT_ROLE)
