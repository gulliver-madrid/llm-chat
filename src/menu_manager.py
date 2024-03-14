from dataclasses import dataclass

from mistralai.models.chat_completion import ChatCompletionResponse
from rich import print

from src.io_helpers import NEUTRAL_MSG, get_input, show_error_msg


class ActionName:
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    NEW_QUERY = "NEW_QUERY"


@dataclass
class Action:
    name: str


class MenuManager:
    @staticmethod
    def enter_debug_mode(response: ChatCompletionResponse | None) -> None:
        from src.debug import show  # pyright: ignore [reportUnusedImport]

        print(NEUTRAL_MSG + "Entrando en modo de depuracion\n")
        print(response)
        breakpoint()
        print(NEUTRAL_MSG + "\nSaliendo del modo de depuración\n")

    @staticmethod
    def enter_inner_menu(response: ChatCompletionResponse | None) -> Action:

        while True:
            user_input = get_input(
                "Pulsa Enter para continuar con otra consulta. Introduce 'd' para entrar en el modo de depuración, 'q' para salir y 'change' para cambiar de modelo."
            ).lower()
            print()
            match user_input:
                case "":
                    break
                case "q" | "quit" | "exit":
                    return Action(ActionName.SALIR)
                case "change":
                    return Action(ActionName.CHANGE_MODEL)
                case "d" | "debug":
                    MenuManager.enter_debug_mode(response)
                    break
                case _:
                    show_error_msg("Entrada no válida")
        return Action(ActionName.NEW_QUERY)
