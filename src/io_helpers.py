import time
from typing import NewType

from rich import print

StyleTag = NewType("StyleTag", str)

ERROR = StyleTag("[bright_red]")
CALL_TO_ACTION = StyleTag("[bright_cyan]")
HIGHLIGHT_ROLE = StyleTag("[light_green]")
NEUTRAL_MSG = StyleTag("[dark_goldenrod]")

BLUE_VIOLET_COLOR = StyleTag("[blue_violet]")

BOLD_STYLE = StyleTag("[bold]")


def end_style_tag(s: StyleTag) -> str:
    """Create a end tag"""
    assert s[0] == "["
    assert s[-1] == "]"
    return f"[/{s[1:-1]}]"


def get_input(text: str = "") -> str:
    """Prompts the user to provide an input, in a styled way"""
    text_with_breakline_before = f"\n{text}" if text else ""
    print(
        CALL_TO_ACTION + f"{text_with_breakline_before}\n> ",
        end="",
    )
    return input()


def show_error_msg(text: str) -> None:
    """Displays an error message with the given text and make a short pause before returning"""
    print(ERROR + f"\n{text}")
    time.sleep(1)


def apply_style_tag(s: str, tag: StyleTag) -> str:
    assert tag.startswith("[")
    assert tag.endswith("]")
    return tag + s + end_style_tag(tag)


def highlight_role(role_string: str) -> str:
    return HIGHLIGHT_ROLE + role_string + end_style_tag(HIGHLIGHT_ROLE)


def display_neutral_msg(text: str) -> None:
    print(NEUTRAL_MSG + text)
