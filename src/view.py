from rich import print
from rich.console import Console
from rich.markdown import Markdown

from typing import Mapping, Sequence

from src.io_helpers import (
    get_input,
)
from src.models.placeholders import (
    Placeholder,
)

HELP_TEXT = """
## Consultas
Puedes usar placeholders con el formato `$0<nombre>`. Ejemplo: `¿Quién fue $0persona y que hizo en el ámbito de $0tema?` El programa te pedirá luego que completes los placeholders uno por uno.
Si empiezas el contenido de un placeholder con `/for` y pones las variantes separadas por comas, se generará una consulta con cada variante. Por ejemplo, si en la pregunta anterior introduces como valor de $0persona `/for Alexander Flemming,Albert Einstein` se generarán 2 consultas, una para cada nombre introducido.
### Comandos
Para empezar una nueva conversación en lugar de seguir con la actual, usa el comando `/new` al inicio de tu consulta.
Puedes iniciar tu consulta con `/d` para activar el modo depuración.
"""


class View:

    def show_help(self) -> None:
        console = Console()
        markdown = Markdown(HELP_TEXT)
        console.print(markdown, width=60)

    def get_raw_substitutions_from_user(
        self,
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

    def confirm_launching_many_queries(self, number_of_queries: int) -> bool:
        print(
            "Se realizarán",
            number_of_queries,
            "consultas. Quieres continuar? Y/n",
        )
        user_input_continue = get_input()
        return user_input_continue.lower() in ["", "y", "yes"]

    def write_object(self, texto: object) -> None:
        print(texto)
