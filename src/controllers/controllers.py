from dataclasses import dataclass

from src.controllers.conversation_loader import ConversationLoader
from src.controllers.query_answerer import QueryAnswerer
from src.controllers.select_model import SelectModelController


@dataclass(frozen=True, kw_only=True)
class Controllers:
    select_model_controler: SelectModelController
    conversation_loader: ConversationLoader
    query_answerer: QueryAnswerer
