from src.domain import CompleteMessage
from src.model_manager import ModelManager
from src.protocols import ChatRepositoryProtocol, ViewProtocol

from .controllers import Controllers
from .conversation_loader import ConversationLoader
from .query_answerer import QueryAnswerer
from .select_model import SelectModelController


def build_controllers(
    select_model_controler: SelectModelController,
    view: ViewProtocol,
    repository: ChatRepositoryProtocol,
    model_manager: ModelManager,
    prev_messages: list[CompleteMessage],
) -> Controllers:
    conversation_loader = ConversationLoader(
        view=view,
        repository=repository,
        prev_messages=prev_messages,
    )
    query_answerer = QueryAnswerer(
        view=view,
        repository=repository,
        model_manager=model_manager,
        prev_messages=prev_messages,
    )
    return Controllers(
        select_model_controler=select_model_controler,
        conversation_loader=conversation_loader,
        query_answerer=query_answerer,
    )
