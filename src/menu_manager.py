from mistralai.models.chat_completion import ChatCompletionResponse
from rich import print

from src.io_helpers import NEUTRAL_MSG, get_input, show_error_msg


class MenuManager:
    @staticmethod
    def enter_debug_mode(response: ChatCompletionResponse | None) -> None:
        from src.debug import show  # pyright: ignore [reportUnusedImport]

        print(NEUTRAL_MSG + "Entrando en modo de depuracion\n")
        print(response)
        breakpoint()
        print(NEUTRAL_MSG + "\nSaliendo del modo de depuración\n")

    @staticmethod
    def enter_inner_menu(response: ChatCompletionResponse | None) -> bool:
        salir = False
        while True:
            entrada = get_input(
                "Pulsa Enter para continuar con otra consulta, d para entrar en el modo de depuración, q para salir."
            ).lower()
            print()
            if not entrada:
                break
            elif entrada in ["q", "quit", "exit"]:
                salir = True
                break
            elif entrada in ["d", "debug"]:
                MenuManager.enter_debug_mode(response)
                break
            else:
                show_error_msg("Entrada no válida")
        return salir
