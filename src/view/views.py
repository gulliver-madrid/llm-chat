from src.domain import ModelName
from src.protocols import TimeManagerProtocol

from .generic_view import Raw
from .io_helpers import escape_for_rich, highlight_role


def get_interaction_styled_view(
    time_manager: TimeManagerProtocol, model: ModelName, query: Raw, content: Raw
) -> str:
    """Returns the styled representation of an interaction between user and model"""
    time_repr = time_manager.get_current_time()
    user_repr = _get_user_repr(query)
    model_repr = _get_model_repr(model, content)
    return "\n".join("\n" + text for text in [time_repr, user_repr, model_repr])


def _get_model_repr(model: ModelName, content: Raw) -> str:
    role_model_repr = highlight_role(Raw(model.upper() + ": "))
    return role_model_repr + escape_for_rich(content)


def _get_user_repr(query: Raw) -> str:
    role_user_repr = highlight_role(Raw("USER: "))
    return role_user_repr + escape_for_rich(query)
