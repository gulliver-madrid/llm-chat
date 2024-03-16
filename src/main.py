from rich import print
from rich.console import Console
from rich.markdown import Markdown

import os
from typing import Final, Mapping, Sequence

from src.infrastructure.client_wrapper import ClientWrapper
from src.controllers.select_model import SelectModelController
from src.io_helpers import (
    display_neutral_msg,
    get_input,
    show_error_msg,
)
from src.controllers.command_interpreter import ActionName, CommandInterpreter
from src.models.model_choice import ModelName, build_model_name
from src.models.placeholders import (
    FOR_COMMAND_PREFFIX,
    Placeholder,
    find_placeholders,
    get_placeholders_with_for,
    replace_placeholders_with_one_for,
    replace_question_with_substitutions,
)
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

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""
        api_key = os.environ["MISTRAL_API_KEY"]
        client_wrapper = ClientWrapper(api_key)
        model = self.select_model()

        while True:
            debug = False

            raw_question = get_input(PROGRAM_PROMPT)

            if not raw_question:
                continue
            action = CommandInterpreter.parse_user_input(raw_question)
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
                        raw_question = raw_question.removeprefix("/d").strip()
                        debug = True
                    case _:
                        raise RuntimeError(f"Acción no válida: {action}")

            if not raw_question:
                continue

            while (more := input()).lower() != "end":
                raw_question += "\n" + more

            occurrences = find_placeholders(raw_question)

            if occurrences:
                user_substitutions = get_raw_substitutions_from_user(occurrences)
                questions = build_questions(raw_question, user_substitutions)
                if questions is None:
                    continue
                print("Placeholders sustituidos exitosamente")
            else:
                questions = [raw_question]
            del raw_question
            number_of_questions = len(questions)
            if number_of_questions > QUERY_NUMBER_LIMIT_WARNING:
                print(
                    "Se realizarán",
                    number_of_questions,
                    "consultas. Quieres continuar? Y/n",
                )
                user_input_continue = get_input()
                if user_input_continue.lower() not in ["", "y", "yes"]:
                    continue

            for i, question in enumerate(questions):
                print(
                    "\n...procesando consulta número", i + 1, "de", number_of_questions
                )

                content = client_wrapper.get_simple_response(model, question, debug)
                print_interaction(model, question, content)

    def select_model(self) -> ModelName:
        return build_model_name(
            self._select_model_controler.select_model(), self._models
        )


def show_help() -> None:
    console = Console()
    markdown = Markdown(HELP_TEXT)
    console.print(markdown, width=60)


def build_questions(
    raw_question: str, substitutions: Mapping[Placeholder, str]
) -> list[str] | None:
    """
    Constructs a list of questions by replacing placeholders in the raw question with user-provided substitutions.
    If a 'for' command is detected, it generates multiple questions by iterating over the specified range.

    Args:
        raw_question: The original question template containing placeholders.
        substitutions: A dictionary mapping placeholders to their substitutions.

    Returns:
        A list of questions with placeholders replaced by their substitutions, or None if an error occurs.
    """
    placeholders_with_for = get_placeholders_with_for(substitutions)
    questions = None
    number_of_placeholders_with_for = len(placeholders_with_for)
    if number_of_placeholders_with_for > 1:
        show_error_msg(
            f"El uso de varios '{FOR_COMMAND_PREFFIX}' con los placeholders no está soportado"
        )
    elif number_of_placeholders_with_for == 1:
        questions = replace_placeholders_with_one_for(
            raw_question, substitutions, placeholders_with_for[0]
        )
    else:
        questions = [replace_question_with_substitutions(raw_question, substitutions)]
    return questions


def get_raw_substitutions_from_user(
    occurrences: Sequence[Placeholder],
) -> Mapping[Placeholder, str]:
    """
    Prompts the user to provide values for each unique placeholder found in the question.

    Args:
        occurrences: A sequence of placeholders found in the question.

    Returns:
        A dictionary mapping placeholders to the user-provided values.
    """
    substitutions: dict[Placeholder, str] = {}
    unique_ocurrences: list[Placeholder] = []
    for occurrence in occurrences:
        if occurrence not in unique_ocurrences:
            unique_ocurrences.append(occurrence)
    for placeholder in unique_ocurrences:
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
