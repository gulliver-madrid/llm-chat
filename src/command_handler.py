from typing import Final

from .controllers import (
    Action,
    ActionType,
    Controllers,
    FinalQueryExtractor,
    SelectModelController,
    build_controllers,
)
from .domain import CompleteMessage
from .model_manager import ModelManager
from .protocols import (
    ChatRepositoryProtocol,
    ClientWrapperProtocol,
    ViewProtocol,
)
from .serde import convert_digits_to_conversation_id
from .settings import QUERY_NUMBER_LIMIT_WARNING
from .strategies import (
    ActionStrategy,
    EstablishSystemPromptAction,
    ShowModelAction,
)
from .view import Raw

PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")


class ExitException(Exception): ...


class CommandHandler:
    __slots__ = (
        "_view",
        "_model_manager",
        "_repository",
        "_controllers",
        "_final_query_extractor",
        "_prev_messages",
    )
    _view: Final[ViewProtocol]
    _model_manager: Final[ModelManager]
    _repository: Final[ChatRepositoryProtocol]
    _prev_messages: Final[list[CompleteMessage]]
    _controllers: Final[Controllers]
    _final_query_extractor: Final[FinalQueryExtractor]

    def __init__(
        self,
        *,
        view: ViewProtocol,
        select_model_controler: SelectModelController,
        repository: ChatRepositoryProtocol,
        client_wrapper: ClientWrapperProtocol,
        prev_messages: list[CompleteMessage] | None = None,
    ):
        self._view = view
        self._model_manager = ModelManager(client_wrapper)
        self._repository = repository
        self._prev_messages = prev_messages if prev_messages is not None else []
        self._controllers = build_controllers(
            select_model_controler,
            self._view,
            self._repository,
            self._model_manager,
            self._prev_messages,
        )
        self._final_query_extractor = FinalQueryExtractor(view=self._view)

    def prompt_to_select_model(self) -> None:
        model = self._controllers.select_model_controler.select_model()
        self._model_manager.model_wrapper.change(model)

    def process_action(self, action: Action, remaining_input: str) -> None:
        debug = False
        new_conversation = False
        conversation_to_load = None

        action_strategy: ActionStrategy | None = None

        if action.type == ActionType.EXIT:
            raise ExitException()
        elif action.type == ActionType.HELP:
            self._view.show_help()
            self._view.simple_view.get_input(PRESS_ENTER_TO_CONTINUE)
            return
        elif action.type == ActionType.CHANGE_MODEL:
            self.prompt_to_select_model()
            return
        elif action.type == ActionType.DEBUG:
            debug = True
        elif action.type in (ActionType.LOAD_CONVERSATION, ActionType.LOAD_MESSAGES):
            conversation_to_load = convert_digits_to_conversation_id(remaining_input)
        elif action.type == ActionType.NEW_CONVERSATION:
            new_conversation = True
        elif action.type == ActionType.CONTINUE_CONVERSATION:
            # TODO: maybe use ActionType.NEW_CONVERSATION when there is no previous messages
            pass
        elif action.type == ActionType.CHECK_DATA:
            self._check_data()
        elif action.type == ActionType.SHOW_MODEL:
            action_strategy = ShowModelAction(
                self._view, self._model_manager.model_wrapper
            )
        elif action.type == ActionType.SYSTEM_PROMPT:
            action_strategy = EstablishSystemPromptAction(
                self._view, self._prev_messages
            )

        if action_strategy:
            action_strategy.execute(remaining_input)
            return

        if conversation_to_load:
            self._controllers.conversation_loader.load_conversation(
                action, conversation_to_load
            )
            return

        if not remaining_input:
            return

        queries = self._final_query_extractor.get_final_queries(remaining_input)
        if queries is None:
            return

        number_of_queries = len(queries)
        if self._should_cancel_for_being_too_many_queries(number_of_queries):
            return

        if new_conversation:
            self._prev_messages.clear()
        self._controllers.query_answerer.answer_queries(queries, debug)

    def _check_data(self) -> None:
        ids = self._repository.get_conversation_ids()
        print(f"{len(ids)=}")
        for id_ in ids:
            try:
                self._repository.load_conversation(id_)
            except Exception as err:
                print(type(err))
                print(err)
                raise

    def _should_cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )
