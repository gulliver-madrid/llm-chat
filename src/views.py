from rich import print

from src.generic_view import Raw
from src.infrastructure.ahora import TimeManager
from src.io_helpers import escape_for_rich, highlight_role
from src.models.shared import ModelName


def print_interaction(
    time_manager: TimeManager, model_name: ModelName, query: Raw, content: Raw
) -> None:
    """Prints an interaction between user and model"""
    print(get_interaction_styled_view(time_manager, model_name, query, content))


def get_interaction_styled_view(
    time_manager: TimeManager, model: ModelName, query: Raw, content: Raw
) -> str:
    """Returns the styled representation of an interaction between user and model"""
    lines: list[str] = []
    lines.append("\n" + time_manager.get_current_time())
    lines.append("\n" + highlight_role(Raw("USER: ")) + escape_for_rich(query))
    lines.append(
        "\n" + highlight_role(Raw(model.upper() + ": ")) + escape_for_rich(content)
    )
    return "\n".join(lines)
