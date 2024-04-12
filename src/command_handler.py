from typing import Final, Sequence

from src.generic_view import Raw
from src.infrastructure.client_wrapper import (
    ClientWrapper,
    QueryResult,
)
from src.controllers.command_interpreter import (
    Action,
    ActionType,
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
    QueryText,
    build_queries,
    find_unique_placeholders,
)
from src.models.serialization import (
    ConversationId,
    cast_string_to_conversation_id,
    convert_conversation_text_into_messages,
)
from src.models.shared import (
    CompleteMessage,
    Model,
    define_system_prompt,
    extract_chat_messages,
)
from src.settings import QUERY_NUMBER_LIMIT_WARNING
from src.view import View
from src.views import print_interaction

PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")


class ExitException(Exception): ...


class CommandHandler:
    def __init__(
        self,
        view: View,
        select_model_controler: SelectModelController,
        repository: ChatRepository,
        client_wrapper: ClientWrapper,
        *,
        prev_messages: list[CompleteMessage] | None = None,
    ):
        self._view = view
        self._model: Model | None
        self._select_model_controler = select_model_controler
        self._repository = repository
        self._client_wrapper = client_wrapper
        self._prev_messages: Final[list[CompleteMessage]] = (
            prev_messages if prev_messages is not None else []
        )

    def process_action(self, action: Action, remaining_input: str) -> None:
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
                conversation_to_load = cast_string_to_conversation_id(remaining_input)
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
            # TODO: allow multiline
            self._prev_messages[:] = [define_system_prompt(remaining_input)]
            self._view.write_object("System prompt established")
            return

        if conversation_to_load:
            self._load_conversation(action, conversation_to_load)
            return

        if not remaining_input:
            return

        while (more := input()).lower() != "end":
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
        self._model = self._select_model_controler.select_model()

    def _show_model(self) -> None:
        assert self._model
        self._view.display_neutral_msg(
            Raw(f"El modelo actual es {self._model.model_name}")
        )

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
        self._repository.save(query_result.messages)
        return query_result.messages if current == 1 else None

    def _print_interaction(self, query: QueryText, query_result: QueryResult) -> None:
        assert self._model
        print_interaction(self._model.model_name, Raw(query), Raw(query_result.content))

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

    def _get_simple_response_from_model(
        self, query: QueryText, debug: bool = False
    ) -> QueryResult:
        assert self._model
        return self._client_wrapper.get_simple_response_to_query(
            self._model, query, self._prev_messages, debug=debug
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
