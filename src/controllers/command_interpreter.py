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


class CommandNoValid(Exception):
    def __init__(self) -> None:
        super().__init__("Comando no válido")


class CommandInterpreter:

    def parse_user_input(self, raw_query: str) -> tuple[Action | None, str]:
        splitted = raw_query.strip().split()
        if not splitted:
            return (None, raw_query)
        action = None
        match splitted[0]:
            case "/q" | "/quit" | "/exit":
                action = Action(ActionName.SALIR)
            case "/h" | "/help":
                action = Action(ActionName.HELP)
            case "/d" | "/debug":
                action = Action(ActionName.DEBUG)
            case "/load":
                action = Action(ActionName.LOAD_CONVERSATION)
            case "/new":
                action = Action(ActionName.NEW_CONVERSATION)
            case "/change":
                action = Action(ActionName.CHANGE_MODEL)
            case "/sys" | "/system":
                action = Action(ActionName.SYSTEM_PROMPT)
            case other if other.startswith("/"):
                raise CommandNoValid()
            case _:
                return (None, raw_query)
        assert action
        return (action, " ".join(splitted[1:]))
