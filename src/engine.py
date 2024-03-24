from typing import Sequence

from src.infrastructure.client_wrapper import ClientWrapper, CompleteMessage, Model
from src.controllers.select_model import SelectModelController
from src.infrastructure.repository import ChatRepository, cast_string_to_conversation_id
from src.io_helpers import (
    get_input,
    show_error_msg,
)
from src.controllers.command_interpreter import ActionName, CommandInterpreter
from src.models.placeholders import (
    QueryBuildException,
    build_queries,
    find_unique_placeholders,
)
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
        self._repository = ChatRepository()
        self.client_wrapper = client_wrapper
        self.view = View()
        self._prev_messages: list[CompleteMessage] | None = None

    def process_raw_query(self, raw_query: str) -> None:
        debug = False
        action = CommandInterpreter.parse_user_input(raw_query)
        new_conversation = False
        system_prompt = False
        conversation_to_load = None
        if action:
            match action.name:
                case ActionName.SALIR:
                    raise ExitException()
                case ActionName.HELP:
                    self.view.show_help()
                    get_input(PRESS_ENTER_TO_CONTINUE)
                    return
                case ActionName.CHANGE_MODEL:
                    self.select_model()
                    return
                case ActionName.DEBUG:
                    # TODO: match exact preffix
                    raw_query = raw_query.removeprefix("/d").strip()
                    debug = True
                case ActionName.LOAD_CONVERSATION:
                    raw_query = raw_query.removeprefix("/load").strip()
                    conversation_to_load = raw_query.split()[0]
                case ActionName.NEW_CONVERSATION:
                    raw_query = raw_query.removeprefix("/new").strip()
                    new_conversation = True
                case ActionName.SYSTEM_PROMPT:
                    # TODO: match exact preffix
                    raw_query = raw_query.removeprefix("/sys").strip()
                    system_prompt = True
                case _:
                    raise RuntimeError(f"Acción no válida: {action}")

        if system_prompt:
            self._prev_messages = self.client_wrapper.define_system_prompt(raw_query)
            self.view.write_object("System prompt established")
            return

        if conversation_to_load:
            conversation_id = cast_string_to_conversation_id(conversation_to_load)
            conversation = self._repository.load_conversation(conversation_id)
            self._prev_messages = self._repository.load_conversation_from_text(
                conversation
            )
            self.view.write_object(
                f"### Esta es la conversacion con id {conversation_to_load}"
            )
            self.view.write_object(conversation)
            self.view.write_object(
                f"### Estos son los mensajes de la conversacion con id {conversation_to_load}"
            )
            self.view.write_object(self._prev_messages)
            return

        if not raw_query:
            return

        while (more := input()).lower() != "end":
            raw_query += "\n" + more

        placeholders = find_unique_placeholders(raw_query)

        if placeholders:
            user_substitutions = self.view.get_raw_substitutions_from_user(placeholders)
            try:
                queries = build_queries(raw_query, user_substitutions)
            except QueryBuildException as err:
                show_error_msg(str(err))
                return
            self.view.write_object("Placeholders sustituidos exitosamente")
        else:
            queries = [raw_query]
        del raw_query
        number_of_queries = len(queries)
        if (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self.view.confirm_launching_many_queries(number_of_queries)
        ):
            return
        if new_conversation:
            self._prev_messages = None
        messages = None
        for i, query in enumerate(queries):
            text = f"\n...procesando consulta"
            if number_of_queries > 1:
                extra = f"número {i + 1} de {number_of_queries}"
                text = " ".join([text, extra])

            self.view.write_object(text)

            query_result = self.client_wrapper.get_simple_response(
                self._model, query, self._prev_messages, debug
            )
            print_interaction(self._model.model_name, query, query_result.content)
            self._repository.save(query_result.messages)
            if i == 0:
                messages = query_result.messages
        if len(queries) > 1:
            self._prev_messages = None
        else:
            self._prev_messages = messages

    def select_model(self) -> None:
        self._model = self._select_model_controler.select_model()
