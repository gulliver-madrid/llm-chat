from dataclasses import dataclass

from .conversation_loader import ConversationLoader
from .extras import DataChecker, QueriesNumberChecker
from .final_query_extractor import FinalQueryExtractor
from .query_answerer import QueryAnswerer
from .select_model import SelectModelController


@dataclass(frozen=True, kw_only=True)
class Controllers:
    select_model_controler: SelectModelController
    conversation_loader: ConversationLoader
    query_answerer: QueryAnswerer
    final_query_extractor: FinalQueryExtractor
    data_checker: DataChecker
    queries_checker: QueriesNumberChecker
