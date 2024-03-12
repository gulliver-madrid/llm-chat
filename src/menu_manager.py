from dataclasses import dataclass

from mistralai.models.chat_completion import ChatCompletionResponse
from rich import print

from src.io_helpers import NEUTRAL_MSG, get_input, show_error_msg

SALIR = "SALIR"
CHANGE_MODEL = "CHANGE_MODEL"


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
    def enter_inner_menu(response: ChatCompletionResponse | None) -> Action | None:

        while True:
            entrada = get_input(
                "Pulsa Enter para continuar con otra consulta. Introduce 'd' para entrar en el modo de depuración, 'q' para salir y 'change' para cambiar de modelo."
            ).lower()
            print()
            if not entrada:
                break
            elif entrada in ["q", "quit", "exit"]:
                return Action(SALIR)

            elif entrada in ["change"]:
                return Action(CHANGE_MODEL)

            elif entrada in ["d", "debug"]:
                MenuManager.enter_debug_mode(response)
                break
            else:
                show_error_msg("Entrada no válida")
        return None
