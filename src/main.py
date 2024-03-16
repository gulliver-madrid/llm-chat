from rich import print
from rich.console import Console
from rich.markdown import Markdown

import os
from typing import Final, Mapping, Sequence

from src.infrastructure.client_wrapper import ClientWrapper
from src.controllers.select_model import SelectModelController
from src.infrastructure.repository import ChatRepository
from src.io_helpers import (
    display_neutral_msg,
    get_input,
    show_error_msg,
)
from src.controllers.command_interpreter import ActionName, CommandInterpreter
from src.models.model_choice import ModelName, build_model_name
from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    build_queries,
    find_placeholders,
)
from src.utils import remove_duplicates
from src.views import print_interaction

PROGRAM_PROMPT = "Introduce tu consulta. Introduce `end` como único contenido de una línea cuando hayas terminado. Para obtener ayuda, introduce únicamente `/help` y pulsa Enter."
PRESS_ENTER_TO_CONTINUE = "Pulsa Enter para continuar"

QUERY_NUMBER_LIMIT_WARNING = 5


HELP_TEXT = """
## Consultas
Puedes usar placeholders con el formato `$0<nombre>`. Ejemplo: `¿Quién fue $0persona y que hizo en el ámbito de $0tema?` El programa te pedirá luego que completes los placeholders uno por uno.
Si empiezas el contenido de un placeholder con `/for` y pones las variantes separadas por comas, se generará una consulta con cada variante. Por ejemplo, si en la pregunta anterior introduces como valor de $0persona `/for Alexander Flemming,Albert Einstein` se generarán 2 consultas, una para cada nombre introducido.
### Comandos
Puedes iniciar tu consulta con `/d` para activar el modo depuración.
"""


class Main:
    def __init__(self, models: Sequence[str]) -> None:
        self._models = models
        self._select_model_controler = SelectModelController(models)
        self._repository = ChatRepository()

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""
        api_key = os.environ["MISTRAL_API_KEY"]
        client_wrapper = ClientWrapper(api_key)
        model = self.select_model()
        prev_messages = None
        while True:
            debug = False

            raw_query = get_input(PROGRAM_PROMPT)

            if not raw_query:
                continue
            action = CommandInterpreter.parse_user_input(raw_query)
            if action:
                match action.name:
                    case ActionName.HELP:
                        show_help()
                        get_input(PRESS_ENTER_TO_CONTINUE)
                        continue
                    case ActionName.SALIR:
                        break
                    case ActionName.CHANGE_MODEL:
                        model = self.select_model()
                        continue
                    case ActionName.DEBUG:
                        raw_query = raw_query.removeprefix("/d").strip()
                        debug = True
                    case _:
                        raise RuntimeError(f"Acción no válida: {action}")

            if not raw_query:
                continue

            while (more := input()).lower() != "end":
                raw_query += "\n" + more

            occurrences = find_placeholders(raw_query)

            if occurrences:
                unique_placeholders = remove_duplicates(occurrences)
                del occurrences
                user_substitutions = get_raw_substitutions_from_user(
                    unique_placeholders
                )
                try:
                    queries = build_queries(raw_query, user_substitutions)
                except QueryBuildException as err:
                    show_error_msg(str(err))
                    continue
                print("Placeholders sustituidos exitosamente")
            else:
                queries = [raw_query]
            del raw_query
            number_of_queries = len(queries)
            if (
                number_of_queries > QUERY_NUMBER_LIMIT_WARNING
                and not confirm_launching_many_queries(number_of_queries)
            ):
                continue

            for i, query in enumerate(queries):
                print("\n...procesando consulta número", i + 1, "de", number_of_queries)

                query_result = client_wrapper.get_simple_response(
                    model, query, prev_messages, debug
                )
                print_interaction(model, query, query_result.content)
                self._repository.save(query_result.messages)
                if len(queries) > 1:
                    prev_messages = None
                else:
                    prev_messages = query_result.messages

    def select_model(self) -> ModelName:
        return build_model_name(
            self._select_model_controler.select_model(), self._models
        )


def confirm_launching_many_queries(number_of_queries: int) -> bool:
    print(
        "Se realizarán",
        number_of_queries,
        "consultas. Quieres continuar? Y/n",
    )
    user_input_continue = get_input()
    return user_input_continue.lower() in ["", "y", "yes"]


def show_help() -> None:
    console = Console()
    markdown = Markdown(HELP_TEXT)
    console.print(markdown, width=60)


def get_raw_substitutions_from_user(
    unique_placeholders: Sequence[Placeholder],
) -> Mapping[Placeholder, str]:
    """
    Prompts the user to provide values for each unique placeholder found in the query.

    Args:
        unique_placeholders: A sequence of unique placeholders found in the query.

    Returns:
        A dictionary mapping placeholders to the user-provided values.
    """
    substitutions: dict[Placeholder, str] = {}
    for placeholder in unique_placeholders:
        replacement = get_input("Por favor indica el valor de " + placeholder)
        substitutions[placeholder] = replacement
    return substitutions


def main() -> None:
    models: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]
    main_instance = Main(models)
    main_instance.execute()
    display_neutral_msg("Saliendo")


if __name__ == "__main__":
    main()
