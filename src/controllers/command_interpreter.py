from dataclasses import dataclass


from src.io_helpers import show_error_msg


class ActionName:
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    DEBUG = "DEBUG"
    HELP = "HELP"
    NEW_CONVERSATION = "NEW_CONVERSATION"
    LOAD_CONVERSATION = "LOAD_CONVERSATION"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"


@dataclass
class Action:
    name: str


class CommandInterpreter:

    def parse_user_input(self, raw_query: str) -> Action | None:
        possible_commands = raw_query.strip().split()
        if not possible_commands:
            return None
        match possible_commands[0]:
            case "/q" | "/quit" | "/exit":
                return Action(ActionName.SALIR)
            case "/h" | "/help":
                return Action(ActionName.HELP)
            case "/d" | "/debug":
                return Action(ActionName.DEBUG)
            case "/load":
                return Action(ActionName.LOAD_CONVERSATION)
            case "/new":
                return Action(ActionName.NEW_CONVERSATION)
            case "/change":
                return Action(ActionName.CHANGE_MODEL)
            case "/sys" | "/system":
                return Action(ActionName.SYSTEM_PROMPT)
            case other if other.startswith("/"):
                show_error_msg("Comando no válido")
                return None
            case _:
                return None
