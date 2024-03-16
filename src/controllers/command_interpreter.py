from dataclasses import dataclass


from src.io_helpers import show_error_msg


class ActionName:
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    DEBUG = "DEBUG"
    HELP = "HELP"


@dataclass
class Action:
    name: str


class CommandInterpreter:

    @staticmethod
    def parse_user_input(raw_query: str) -> Action | None:
        possible_commands = raw_query.strip().split()
        if not possible_commands:
            return None
        match possible_commands[0]:
            case "/q" | "/quit" | "/exit":
                return Action(ActionName.SALIR)
            case "/d" | "/debug":
                return Action(ActionName.DEBUG)
            case "/h" | "/help":
                return Action(ActionName.HELP)
            case "/change":
                return Action(ActionName.CHANGE_MODEL)
            case other if other.startswith("/"):
                show_error_msg("Comando no válido")
                return None
            case _:
                return None
