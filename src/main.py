from typing import Mapping, Sequence
from rich import print

import os

from src.client_wrapper import ClientWrapper
from src.io_helpers import (
    NEUTRAL_MSG,
    get_input,
)
from src.menu_manager import CHANGE_MODEL, SALIR, MenuManager
from src.model_choice import build_model_name, models, select_model
from src.placeholders import find_placeholders, replace_placeholders_including_for
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
                if not action:
                    continue
                elif action.name == SALIR:
                    break
                elif action.name == CHANGE_MODEL:
                    model = build_model_name(select_model(models))
                    continue
                else:
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
    raw_question: str, substitutions: dict[str, str]
) -> list[str] | None:
    """
    Return the result of replacing placeholders with their corresponding values, and also applying possible use of 'for' command.
    """
    for_placeholders = get_placeholders_with_for(substitutions)
    questions = None
    number_of_placeholders_with_for = len(for_placeholders)
    if number_of_placeholders_with_for > 1:
        print("El uso de varios '/for' con los placeholders no está soportado")
    elif number_of_placeholders_with_for == 1:
        questions = replace_placeholders_including_for(
            raw_question, substitutions, for_placeholders
        )
    else:
        question_in_process = raw_question
        del raw_question
        for placeholder, replacement in substitutions.items():
            question_in_process = question_in_process.replace(placeholder, replacement)
        questions = [question_in_process]
    return questions


def get_placeholders_with_for(substitutions: Mapping[str, str]) -> list[str]:
    return [
        placeholder
        for placeholder, subs in substitutions.items()
        if subs.startswith("/for")
    ]


def get_raw_substitutions_from_user(occurrences: Sequence[str]) -> dict[str, str]:
    substitutions: dict[str, str] = {}
    unique_ocurrences: list[str] = []
    for occurrence in occurrences:
        if occurrence not in unique_ocurrences:
            unique_ocurrences.append(occurrence)
    for placeholder in unique_ocurrences:
        subs = get_input("Por favor indica el valor de " + placeholder)
        substitutions[placeholder] = subs
    return substitutions


def main() -> None:
    main_instance = Main()
    main_instance.execute()
    print(NEUTRAL_MSG + "Saliendo")


if __name__ == "__main__":
    main()
