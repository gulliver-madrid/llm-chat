from typing import Sequence
from rich import print

import os

from src.client_wrapper import ClientWrapper
from src.io_helpers import (
    NEUTRAL_MSG,
    get_input,
    show_error_msg,
)
from src.menu_manager import ActionName, MenuManager
from src.model_choice import build_model_name, models, select_model
from src.placeholders import (
    FOR_COMMAND_PREFFIX,
    Placeholder,
    find_placeholders,
    get_placeholders_with_for,
    replace_placeholders_with_one_for,
    replace_question_with_substitutions,
)
from src.views import print_interaction


class Main:

    def execute(self) -> None:
        """Runs the text interface to Mistral models"""
        api_key = os.environ["MISTRAL_API_KEY"]
        client_wrapper = ClientWrapper(api_key)
        model = build_model_name(select_model(models))
        chat_response = None

        while True:
            # modo multilinea por defecto
            raw_question = get_input(
                "Introduce tu consulta (o pulsa Enter para ver más opciones). Introduce `end` como único contenido de una línea cuando hayas terminado."
            )

            if not raw_question:
                action = MenuManager.enter_inner_menu(chat_response)
                match action.name:
                    case ActionName.NEW_QUERY:
                        continue
                    case ActionName.SALIR:
                        break
                    case ActionName.CHANGE_MODEL:
                        model = build_model_name(select_model(models))
                        continue
                    case _:
                        raise RuntimeError(f"Acción no válida: {action}")

            assert raw_question

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

            for i, question in enumerate(questions):
                print("\n...procesando consulta número", i + 1)

                content = client_wrapper.get_simple_response(model, question)
                print_interaction(model, question, content)


def build_questions(
    raw_question: str, substitutions: dict[Placeholder, str]
) -> list[str] | None:
    """
    Return the result of replacing placeholders with their corresponding values, and also applying possible use of 'for' command.
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
) -> dict[Placeholder, str]:
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
    main_instance = Main()
    main_instance.execute()
    print(NEUTRAL_MSG + "Saliendo")


if __name__ == "__main__":
    main()
