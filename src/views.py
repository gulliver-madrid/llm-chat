from rich import print

from src.infrastructure.ahora import get_current_time
from src.io_helpers import highlight_role


def print_interaction(model: str, query: str, content: str) -> None:
    """Prints an interaction between user and model"""
    print(get_interaction_styled_view(model, query, content))


def get_interaction_styled_view(model: str, query: str, content: str) -> str:
    """Returns the styled representation of an interaction between user and model"""
    lines: list[str] = []
    lines.append("\n" + get_current_time())
    lines.append("\n" + highlight_role("USER: ") + query)
    lines.append("\n" + highlight_role(model.upper() + ": ") + content)
    return "\n".join(lines)
