from typing import Sequence

from src.infrastructure.client_wrapper import (
    ClientWrapper,
    QueryResult,
)
from src.controllers.select_model import SelectModelController
from src.infrastructure.repository import Repository, cast_string_to_conversation_id
from src.io_helpers import (
    get_input,
    show_error_msg,
)
from src.controllers.command_interpreter import (
    Action,
    ActionType,
    CommandInterpreter,
    CommandNoValid,
)
from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    build_queries,
    find_unique_placeholders,
)
from src.models.shared import CompleteMessage, Model, extract_chat_messages
from src.view import View
from src.views import print_interaction


class ExitException(Exception): ...


# settings
QUERY_NUMBER_LIMIT_WARNING = 5

PRESS_ENTER_TO_CONTINUE = "Pulsa Enter para continuar"


class MainEngine:
    def __init__(self, models: Sequence[Model], client_wrapper: ClientWrapper) -> None:
        self._models = models
        self._select_model_controler = SelectModelController(models)
        self._repository = Repository()
        self._client_wrapper = client_wrapper
        self._view = View()
        self._prev_messages: list[CompleteMessage] | None = None
        self._command_interpreter = CommandInterpreter()

    def process_raw_query(self, raw_query: str) -> None:
        try:
            action, rest_query = self._command_interpreter.parse_user_input(raw_query)
        except CommandNoValid as err:
            show_error_msg(str(err))
            return
        self.process_action(action, rest_query)

    def process_action(self, action: Action, rest_query: str) -> None:
        debug = False
        new_conversation = False
        system_prompt = False
        conversation_to_load = None

        match action.type:
            case ActionType.SALIR:
                raise ExitException()
            case ActionType.HELP:
                self._view.show_help()
                get_input(PRESS_ENTER_TO_CONTINUE)
                return
            case ActionType.CHANGE_MODEL:
                self.select_model()
                return
            case ActionType.DEBUG:
                debug = True
            case ActionType.LOAD_CONVERSATION | ActionType.LOAD_MESSAGES:
                conversation_to_load = rest_query
            case ActionType.NEW_CONVERSATION:
                new_conversation = True
            case ActionType.CONTINUE_CONVERSATION:
                pass
            case ActionType.SYSTEM_PROMPT:
                system_prompt = True

        if system_prompt:
            self._prev_messages = self._client_wrapper.define_system_prompt(rest_query)
            self._view.write_object("System prompt established")
            return

        if conversation_to_load:
            assert action
            conversation_id = cast_string_to_conversation_id(conversation_to_load)
            del conversation_to_load
            conversation = self._repository.load_conversation(conversation_id)
            self._prev_messages = self._repository.convert_conversation_into_messages(
                conversation
            )
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
            return

        if not rest_query:
            return

        while (more := input()).lower() != "end":
            rest_query += "\n" + more

        placeholders = find_unique_placeholders(rest_query)

        queries = self._define_final_queries(rest_query, placeholders)
        if queries is None:
            return

        number_of_queries = len(queries)
        if self._cancel_for_being_too_many_queries(number_of_queries):
            return
        if new_conversation:
            self._prev_messages = None
        messages = None
        for i, query in enumerate(queries):
            text = self._define_processing_query_text(
                number_of_queries=number_of_queries, index_current_query=i
            )
            self._view.write_object(text)

            query_result = self._get_simple_response_from_model(query, debug)
            print_interaction(self._model.model_name, query, query_result.content)
            self._repository.save(query_result.messages)
            if i == 0:
                messages = query_result.messages
        self._prev_messages = None if len(queries) > 1 else messages

    def _get_simple_response_from_model(
        self, query: str, debug: bool = False
    ) -> QueryResult:
        return self._client_wrapper.get_simple_response(
            self._model, query, self._prev_messages, debug
        )

    def _define_processing_query_text(
        self, *, index_current_query: int, number_of_queries: int
    ) -> str:
        assert number_of_queries > index_current_query
        text = f"\n...procesando consulta"
        if number_of_queries > 1:
            extra = f"número {index_current_query + 1} de {number_of_queries}"
            text = " ".join([text, extra])
        return text

    def _cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )

    def _define_final_queries(
        self, rest_query: str, placeholders: list[Placeholder]
    ) -> list[str] | None:
        if placeholders:
            user_substitutions = self._view.get_raw_substitutions_from_user(
                placeholders
            )
            try:
                queries = build_queries(rest_query, user_substitutions)
            except QueryBuildException as err:
                show_error_msg(str(err))
                return None
            self._view.write_object("Placeholders sustituidos exitosamente")
        else:
            queries = [rest_query]
        return queries

    def select_model(self) -> None:
        self._model = self._select_model_controler.select_model()
