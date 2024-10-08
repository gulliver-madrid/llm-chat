from src.domain import ModelName
from src.protocols import TimeManagerProtocol

from .generic_view import Raw
from .io_helpers import escape_for_rich, highlight_role


def get_interaction_styled_view(
    time_manager: TimeManagerProtocol, model: ModelName, query: Raw, content: Raw
) -> str:
    """Returns the styled representation of an interaction between user and model"""
    lines: list[str] = []
    lines.append("\n" + time_manager.get_current_time())
    lines.append("\n" + highlight_role(Raw("USER: ")) + escape_for_rich(query))
    lines.append(
        "\n" + highlight_role(Raw(model.upper() + ": ")) + escape_for_rich(content)
    )
    return "\n".join(lines)
