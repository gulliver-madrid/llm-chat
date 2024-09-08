from dataclasses import dataclass

from src.protocols import ChatRepositoryProtocol, ViewProtocol
from src.settings import QUERY_NUMBER_LIMIT_WARNING


@dataclass(frozen=True)
class DataChecker:
    _repository: ChatRepositoryProtocol

    def check_data(self) -> None:
        ids = self._repository.get_conversation_ids()
        print(f"{len(ids)=}")
        for id_ in ids:
            try:
                self._repository.load_conversation(id_)
            except Exception as err:
                print(type(err))
                print(err)
                raise


@dataclass(frozen=True)
class QueriesNumberChecker:
    _view: ViewProtocol

    def should_cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )
