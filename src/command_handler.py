from typing import Final, Sequence

from src.controllers.command_interpreter import (
    Action,
    ActionType,
)
from src.controllers.select_model import SelectModelController
from src.generic_view import Raw
from src.infrastructure.ahora import TimeManager
from src.infrastructure.llm_connection import (
    ClientWrapper,
    QueryResult,
)
from src.infrastructure.llm_connection.client_wrapper import add_user_query_in_place
from src.infrastructure.repository import ChatRepository
from src.io_helpers import (
    ensure_escaped,
    get_input,
    show_error_msg,
)
from src.models.model_wrapper import ModelWrapper
from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    QueryText,
    build_queries,
    find_unique_placeholders,
)
from src.models.serialization import (
    ConversationId,
    convert_digits_to_conversation_id,
    convert_conversation_text_into_messages,
)
from src.models.shared import (
    CompleteMessage,
    extract_chat_messages,
)
from src.settings import QUERY_NUMBER_LIMIT_WARNING
from src.strategies import ActionStrategy, EstablishSystemPromptAction, ShowModelAction
from src.view import View


PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")


class ExitException(Exception): ...


class CommandHandler:
    def __init__(
        self,
        *,
        view: View,
        select_model_controler: SelectModelController,
        repository: ChatRepository,
        client_wrapper: ClientWrapper,
        time_manager: TimeManager,
        prev_messages: list[CompleteMessage] | None = None,
    ):
        self._view = view
        self._time_manager: Final = time_manager
        self._model_wrapper: Final = ModelWrapper()
        self._select_model_controler = select_model_controler
        self._repository = repository
        self._client_wrapper = client_wrapper
        self._prev_messages: Final[list[CompleteMessage]] = (
            prev_messages if prev_messages is not None else []
        )

    def process_action(self, action: Action, remaining_input: str) -> None:
        debug = False
        new_conversation = False
        conversation_to_load = None

        action_strategy: ActionStrategy | None = None

        # evalua la accion
        if action.type == ActionType.EXIT:
            raise ExitException()
        elif action.type == ActionType.HELP:
            self._view.show_help()
            get_input(PRESS_ENTER_TO_CONTINUE)
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
            pass
        elif action.type == ActionType.SHOW_MODEL:
            action_strategy = ShowModelAction(self._view, self._model_wrapper)
        elif action.type == ActionType.SYSTEM_PROMPT:
            action_strategy = EstablishSystemPromptAction(
                self._view, self._prev_messages
            )

        if action_strategy:
            action_strategy.execute(remaining_input)
            return

        if conversation_to_load:
            self._load_conversation(action, conversation_to_load)
            return

        if not remaining_input:
            return

        while True:
            more = self._view.input_extra_line()
            if more.lower() == "end":
                break
            remaining_input += "\n" + more

        placeholders = find_unique_placeholders(remaining_input)

        queries = self._define_final_queries(remaining_input, placeholders)
        if queries is None:
            return

        # cancela si hay demasiadas queries
        number_of_queries = len(queries)
        if self._should_cancel_for_being_too_many_queries(number_of_queries):
            return

        if new_conversation:
            self._prev_messages.clear()
        self._answer_queries(queries, debug)

    def prompt_to_select_model(self) -> None:
        self._model_wrapper.change(self._select_model_controler.select_model())

    def _answer_queries(
        self, queries: Sequence[QueryText], debug: bool = False
    ) -> None:
        """If there are multiple queries, the conversation ends after executing them."""
        assert queries
        messages = None
        for i, query in enumerate(queries):
            messages = self._answer_query(debug, i + 1, len(queries), query)
        self._prev_messages[:] = messages or []

    def _answer_query(
        self, debug: bool, current: int, total: int, query: QueryText
    ) -> list[CompleteMessage] | None:
        self._view.display_processing_query_text(current=current, total=total)
        query_result = self._get_simple_response_from_model(query, debug)
        self._print_interaction(query, query_result)
        self._repository.save_messages(query_result.messages)
        return query_result.messages if current == 1 else None

    def _print_interaction(self, query: QueryText, query_result: QueryResult) -> None:
        assert self._model_wrapper.model
        self._view.print_interaction(
            self._time_manager,
            self._model_wrapper.model.model_name,
            Raw(query),
            Raw(query_result.content),
        )

    def _load_conversation(
        self, action: Action, conversation_id: ConversationId
    ) -> None:
        """Load a conversation based in its id"""
        conversation = self._repository.load_conversation_as_text(conversation_id)
        self._prev_messages[:] = convert_conversation_text_into_messages(conversation)
        self._display_loaded_conversation(action, conversation_id, conversation)
        self._view.display_neutral_msg(Raw("La conversación ha sido cargada"))

    def _display_loaded_conversation(
        self,
        action: Action,
        conversation_id: ConversationId,
        conversation: str,
    ) -> None:
        assert self._prev_messages
        if action.type == ActionType.LOAD_CONVERSATION:
            self._view.display_conversation(conversation_id, conversation)
        elif action.type == ActionType.LOAD_MESSAGES:
            self._view.display_messages(
                conversation_id,
                extract_chat_messages(self._prev_messages),
            )
        else:
            raise ValueError(action.type)

    def _get_simple_response_from_model(
        self, query: QueryText, debug: bool = False
    ) -> QueryResult:
        assert self._model_wrapper.model
        add_user_query_in_place(self._prev_messages, query)
        return self._client_wrapper.get_simple_response(
            self._model_wrapper.model, self._prev_messages, debug=debug
        )

    def _should_cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )

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
