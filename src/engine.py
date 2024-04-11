from typing import Sequence

from src.generic_view import Raw
from src.infrastructure.client_wrapper import (
    ClientWrapper,
    QueryResult,
)
from src.controllers.command_interpreter import (
    Action,
    ActionType,
    CommandInterpreter,
    CommandNoValid,
)
from src.controllers.select_model import SelectModelController
from src.infrastructure.repository import ChatRepository
from src.io_helpers import (
    ensure_escaped,
    get_input,
    show_error_msg,
)
from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    build_queries,
    find_unique_placeholders,
)
from src.models.serialization import (
    ConversationId,
    cast_string_to_conversation_id,
    convert_conversation_into_messages,
)
from src.models.shared import (
    CompleteMessage,
    Model,
    define_system_prompt,
    extract_chat_messages,
)
from src.view import View
from src.views import print_interaction


class ExitException(Exception): ...


# settings
QUERY_NUMBER_LIMIT_WARNING = 5

PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")


class MainEngine:
    _model: Model

    def __init__(self, models: Sequence[Model], client_wrapper: ClientWrapper) -> None:
        self._models = models
        self._select_model_controler = SelectModelController(models)
        self._repository = ChatRepository()
        self._client_wrapper = client_wrapper
        self._view = View()
        self._prev_messages: list[CompleteMessage] | None = None
        self._command_interpreter = CommandInterpreter()

    def process_raw_query(self, raw_query: str) -> None:
        try:
            action, rest_query = self._command_interpreter.parse_user_input(raw_query)
        except CommandNoValid as err:
            show_error_msg(Raw(str(err)))
            return
        self.process_action(action, rest_query)

    def process_action(self, action: Action, rest_query: str) -> None:
        debug = False
        new_conversation = False
        system_prompt = False
        conversation_to_load = None

        # evalua la accion
        match action.type:
            case ActionType.EXIT:
                raise ExitException()
            case ActionType.HELP:
                self._view.show_help()
                get_input(PRESS_ENTER_TO_CONTINUE)
                return
            case ActionType.CHANGE_MODEL:
                self.prompt_to_select_model()
                return
            case ActionType.DEBUG:
                debug = True
            case ActionType.LOAD_CONVERSATION | ActionType.LOAD_MESSAGES:
                conversation_to_load = cast_string_to_conversation_id(rest_query)
            case ActionType.NEW_CONVERSATION:
                new_conversation = True
            case ActionType.CONTINUE_CONVERSATION:
                pass
            case ActionType.SHOW_MODEL:
                self._show_model()
                return
            case ActionType.SYSTEM_PROMPT:
                system_prompt = True

        if system_prompt:
            # establece el system prompt
            self._prev_messages = [define_system_prompt(rest_query)]
            self._view.write_object("System prompt established")
            return

        if conversation_to_load:
            self._load_conversation(action, conversation_to_load)
            return

        if not rest_query:
            return

        while (more := input()).lower() != "end":
            rest_query += "\n" + more

        placeholders = find_unique_placeholders(rest_query)

        queries = self._define_final_queries(rest_query, placeholders)
        if queries is None:
            return

        # cancela si hay demasiadas queries
        number_of_queries = len(queries)
        if self._cancel_for_being_too_many_queries(number_of_queries):
            return

        if new_conversation:
            self._prev_messages = None
        self._answer_queries(queries, debug)

    def prompt_to_select_model(self) -> None:
        self._model = self._select_model_controler.select_model()

    def _show_model(self) -> None:
        self._view.display_neutral_msg(
            Raw(f"El modelo actual es {self._model.model_name}")
        )

    def _answer_queries(self, queries: Sequence[str], debug: bool = False) -> None:
        """If there are multiple queries, the conversation ends after executing them."""
        messages = None
        for i, query in enumerate(queries):
            messages = self._answer_query(debug, i + 1, len(queries), query)
        self._prev_messages = messages

    def _answer_query(
        self, debug: bool, current: int, total: int, query: str
    ) -> list[CompleteMessage] | None:
        self._view.display_processing_query_text(current=current, total=total)
        query_result = self._get_simple_response_from_model(query, debug)
        self._print_interaction(query, query_result)
        self._repository.save(query_result.messages)
        return query_result.messages if current == 1 else None

    def _print_interaction(self, query: str, query_result: QueryResult) -> None:
        print_interaction(self._model.model_name, Raw(query), Raw(query_result.content))

    def _load_conversation(
        self, action: Action, conversation_id: ConversationId
    ) -> None:
        """Load a conversation based in its id"""
        conversation = self._repository.load_conversation(conversation_id)
        self._prev_messages = convert_conversation_into_messages(conversation)
        match action.type:
            case ActionType.LOAD_CONVERSATION:
                self._view.display_conversation(conversation_id, conversation)
            case ActionType.LOAD_MESSAGES:
                self._view.display_messages(
                    conversation_id,
                    extract_chat_messages(self._prev_messages),
                )
            case _:
                raise ValueError(action.type)
        self._view.display_neutral_msg(Raw("La conversación ha sido cargada"))

    def _get_simple_response_from_model(
        self, query: str, debug: bool = False
    ) -> QueryResult:
        return self._client_wrapper.get_simple_response_to_query(
            self._model, query, self._prev_messages, debug=debug
        )

    def _cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )

    def _define_final_queries(
        self, rest_query: str, placeholders: list[Placeholder]
    ) -> list[str] | None:
        if not placeholders:
            return [rest_query]

        user_substitutions = self._view.get_raw_substitutions_from_user(placeholders)
        try:
            queries = build_queries(rest_query, user_substitutions)
        except QueryBuildException as err:
            show_error_msg(ensure_escaped(Raw(str(err))))
            return None
        else:
            self._view.write_object("Placeholders sustituidos exitosamente")
            return queries
