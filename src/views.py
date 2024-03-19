from rich import print

from src.infrastructure.ahora import get_current_time
from src.io_helpers import highlight_role
from src.models.shared import ModelName


def print_interaction(model_name: ModelName, query: str, content: str) -> None:
    """Prints an interaction between user and model"""
    print(get_interaction_styled_view(model_name, query, content))


def get_interaction_styled_view(model: ModelName, query: str, content: str) -> str:
    """Returns the styled representation of an interaction between user and model"""
    lines: list[str] = []
    lines.append("\n" + get_current_time())
    lines.append("\n" + highlight_role("USER: ") + escape_for_rich(query))
    lines.append("\n" + highlight_role(model.upper() + ": ") + escape_for_rich(content))
    return "\n".join(lines)


def escape_for_rich(s: str) -> str:
    return s.replace("[", r"\[")
