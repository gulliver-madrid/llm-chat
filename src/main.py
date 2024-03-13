from rich import print

import os

from src.client_wrapper import ClientWrapper
from src.io_helpers import (
    NEUTRAL_MSG,
    get_input,
)
from src.menu_manager import CHANGE_MODEL, SALIR, MenuManager
from src.model_choice import build_model_name, models, select_model
from src.placeholders import find_placeholders, replace_placeholders
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
            question = get_input(
                "Introduce tu consulta (o pulsa Enter para ver más opciones). Introduce `end` como único contenido de una línea cuando hayas terminado."
            )

            if not question:
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

            assert question

            while (more := input()).lower() != "end":
                question += "\n" + more

            occurrences = find_placeholders(question)

            if occurrences:
                substitutions: dict[str, str] = {}
                set_occurrences = set(occurrences)
                for placeholder in set_occurrences:
                    subs = get_input("Por favor indica el valor de " + placeholder)
                    substitutions[placeholder] = subs
                for_placeholders = [
                    placeholder
                    for placeholder, subs in substitutions.items()
                    if subs.startswith("/for")
                ]
                if len(for_placeholders) > 1:
                    print(
                        "El uso de varios '/for' con los placeholders no está soportado"
                    )
                    continue
                elif len(for_placeholders) == 1:
                    questions = replace_placeholders(
                        question, substitutions, for_placeholders
                    )
                else:
                    for placeholder, subs in substitutions.items():
                        question = question.replace(placeholder, subs)
                    questions = [question]
                print("Placeholders sustituidos exitosamente")
            else:
                questions = [question]

            for i, question in enumerate(questions):
                print("\n...procesando consulta número", i + 1)

                content = client_wrapper.get_simple_response(model, question)
                print_interaction(model, question, content)


def main() -> None:
    main_instance = Main()
    main_instance.execute()
    print(NEUTRAL_MSG + "Saliendo")


if __name__ == "__main__":
    main()
