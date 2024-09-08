from __future__ import annotations

from typing import Final

from src.controllers.query_answerer import QueryAnswerer

from .controllers.command_interpreter import Action, ActionType
from .controllers.conversation_loader import ConversationLoader
from .controllers.select_model import SelectModelController
from .domain import CompleteMessage
from .model_manager import ModelManager
from .models.placeholders import (
    Placeholder,
    QueryBuildException,
    QueryText,
    build_queries,
    find_unique_placeholders,
)
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
from .view import Raw, ensure_escaped, show_error_msg

PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")
DELIBERATE_INPUT_TIME = 0.02


class ExitException(Exception): ...


class CommandHandler:
    __slots__ = (
        "_view",
        "_select_model_controler",
        "_model_manager",
        "_repository",
        "_conversation_loader",
        "_query_answerer",
        "_prev_messages",
    )
    _view: Final[ViewProtocol]
    _select_model_controler: Final[SelectModelController]
    _model_manager: Final[ModelManager]
    _repository: Final[ChatRepositoryProtocol]
    _conversation_loader: Final[ConversationLoader]
    _query_answerer: Final[QueryAnswerer]
    _prev_messages: Final[list[CompleteMessage]]

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
        self._select_model_controler = select_model_controler
        self._model_manager = ModelManager(client_wrapper)
        self._repository = repository
        self._prev_messages = prev_messages if prev_messages is not None else []
        self._conversation_loader = ConversationLoader(
            view=self._view,
            repository=self._repository,
            prev_messages=self._prev_messages,
        )
        self._query_answerer = QueryAnswerer(
            view=self._view,
            repository=self._repository,
            model_manager=self._model_manager,
            prev_messages=self._prev_messages,
        )

    def prompt_to_select_model(self) -> None:
        self._model_manager.model_wrapper.change(
            self._select_model_controler.select_model()
        )

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
            ids = self._repository.get_conversation_ids()
            print(f"{len(ids)=}")
            for id_ in ids:
                try:
                    self._repository.load_conversation(id_)
                except Exception as err:
                    print(type(err))
                    print(err)
                    raise
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
            self._conversation_loader.load_conversation(action, conversation_to_load)
            return

        if not remaining_input:
            return

        remaining_input = self._get_extra_lines(remaining_input)

        placeholders = find_unique_placeholders(remaining_input)

        queries = self._define_final_queries(remaining_input, placeholders)
        if queries is None:
            return

        number_of_queries = len(queries)
        if self._should_cancel_for_being_too_many_queries(number_of_queries):
            return

        if new_conversation:
            self._prev_messages.clear()
        self._query_answerer.answer_queries(queries, debug)

    def _get_extra_lines(self, remaining_input: str) -> str:
        while True:
            more, elapsed = self._view.input_extra_line()
            should_end = (elapsed >= DELIBERATE_INPUT_TIME) and (more == "end")
            if should_end:
                break
            remaining_input += "\n" + more
        return remaining_input

    def _define_final_queries(
        self, remaining_input: str, placeholders: list[Placeholder]
    ) -> list[QueryText] | None:
        if not placeholders:
            return [QueryText(remaining_input)]

        user_substitutions = self._view.get_raw_substitutions_from_user(placeholders)
        try:
            queries = build_queries(remaining_input, user_substitutions)
        except QueryBuildException as err:
            show_error_msg(ensure_escaped(Raw(str(err))))
            return None

        self._view.write_object("Placeholders sustituidos exitosamente")
        return queries

    def _should_cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )
