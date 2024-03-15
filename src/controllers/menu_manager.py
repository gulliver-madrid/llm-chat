from dataclasses import dataclass

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from src.io_helpers import get_input, show_error_msg


class ActionName:
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    NEW_QUERY = "NEW_QUERY"


@dataclass
class Action:
    name: str


class MenuManager:

    @staticmethod
    def enter_inner_menu() -> Action:

        while True:
            user_input = get_input(
                "Pulsa Enter para continuar con otra consulta. Introduce 'help' para leer un mensaje de ayuda, 'q' para salir y 'change' para cambiar de modelo."
            ).lower()
            print()
            match user_input:
                case "":
                    break
                case "q" | "quit" | "exit":
                    return Action(ActionName.SALIR)
                case "help":
                    console = Console()
                    markdown = Markdown(
                        """
## Consultas
Puedes usar placeholders con el formato `$0<nombre>`. Ejemplo: `¿Quién fue $0persona y que hizo en el ámbito de $0tema?` El programa te pedirá luego que completes los placeholders uno por uno.

Si empiezas el contenido de un placeholder con `/for` y pones las variantes separadas por comas, se generará una consulta con cada variante. Por ejemplo, si en la pregunta anterior introduces como valor de $0persona `/for Alexander Flemming,Albert Einstein` se generarán 2 consultas, una para cada nombre introducido.

### Comandos
Puedes iniciar tu consulta con `/d` para activar el modo depuración.
"""
                    )
                    console.print(markdown, width=60)

                case "change":
                    return Action(ActionName.CHANGE_MODEL)
                case _:
                    show_error_msg("Entrada no válida")
        return Action(ActionName.NEW_QUERY)
