import time
from typing import Mapping, Sequence

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from src.domain import ChatMessage
from src.infrastructure.ahora import TimeManager
from src.models.placeholders import Placeholder
from src.models.shared import ConversationId, ModelName

from .generic_view import EscapedStr, Raw
from .io_helpers import SimpleView, display_neutral_msg, show_error_msg
from .views import get_interaction_styled_view

HELP_TEXT = """
## Consultas
Puedes usar placeholders con el formato `$0<nombre>`.

Ejemplo: `¿Quién fue $0persona y que hizo en el ámbito de $0tema?` El programa te pedirá luego que completes los placeholders uno por uno.

Si empiezas el contenido de un placeholder con `/for` y pones las variantes separadas por comas, se generará una consulta con cada variante. Por ejemplo, si en la pregunta anterior introduces como valor de $0persona `/for Alexander Flemming,Albert Einstein` se generarán 2 consultas, una para cada nombre introducido.

### Comandos
- Para empezar una nueva conversación en lugar de seguir con la actual, usa el comando `/new` al inicio de tu consulta.
- Puedes iniciar tu consulta con `/d` o `/debug` para activar el modo depuración.
- Usa `/show` para ver cuál es el modelo actual.
- Usa `/change` para cambiar el modelo.
- Usa `/sys <prompt>` o `/system <prompt>` para establecer un nuevo prompt de sistema. Esto iniciará una nueva conversación.
- Usa `/load <id>` para cargar una conversación desde el directorio de datos.
- Usa `/load_msgs <id>` para cargar una conversación desde el directorio de datos obteniendo una vista de los mensajes.
- Usa `/h` o `/help` para mostrar esta ayuda.
- Usa `/q`, `/quit` o `/exit` para salir del programa.
"""


class View:

    def __init__(self) -> None:
        self._simple_view = SimpleView()

    @property
    def simple_view(self) -> SimpleView:
        return self._simple_view

    def print_interaction(
        self, time_manager: TimeManager, model_name: ModelName, query: Raw, content: Raw
    ) -> None:
        """Prints an interaction between user and model"""
        print(get_interaction_styled_view(time_manager, model_name, query, content))

    def input_extra_line(self) -> tuple[str, float]:
        prev_time = time.time()
        line = input()
        elapsed = time.time() - prev_time
        return line, elapsed

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
            replacement = self.simple_view.get_input(
                Raw("Por favor indica el valor de " + placeholder)
            )
            substitutions[placeholder] = replacement
        return substitutions

    def confirm_launching_many_queries(self, number_of_queries: int) -> bool:
        print(
            "Se realizarán",
            number_of_queries,
            "consultas. Quieres continuar? Y/n",
        )
        user_input_continue = self.simple_view.get_input()
        return user_input_continue.lower() in ["", "y", "yes"]

    def write_object(self, obj: object) -> None:
        print(obj)

    def display_neutral_msg(self, texto: Raw) -> None:
        display_neutral_msg(texto)

    def display_conversation(
        self, conversation_id: ConversationId, conversation: str
    ) -> None:
        self.write_object(f"### Esta es la conversacion con id {conversation_id}")
        self.write_object(conversation)

    def display_messages(
        self,
        conversation_id: ConversationId,
        prev_messages: Sequence[ChatMessage],
    ) -> None:
        self.write_object(
            f"### Estos son los mensajes de la conversacion con id {conversation_id}"
        )
        self.write_object(prev_messages)

    def display_processing_query_text(self, *, current: int, total: int) -> None:
        text = define_processing_query_text(current=current, total=total)
        self.write_object(text)

    def show_error_msg(self, text: EscapedStr | Raw) -> None:
        show_error_msg(text)


def define_processing_query_text(*, current: int, total: int) -> str:
    assert total >= current
    text = f"\n...procesando consulta"
    if total > 1:
        extra = f"número {current } de {total}"
        text = " ".join([text, extra])
    return text
