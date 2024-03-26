from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    SHOW_MODEL = "SHOW_MODEL"
    DEBUG = "DEBUG"
    HELP = "HELP"
    NEW_CONVERSATION = "NEW_CONVERSATION"
    CONTINUE_CONVERSATION = "CONTINUE_CONVERSATION"
    LOAD_CONVERSATION = "LOAD_CONVERSATION"
    LOAD_MESSAGES = "LOAD_MESSAGES"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"


@dataclass
class Action:
    type: ActionType


class CommandNoValid(Exception):
    def __init__(self) -> None:
        super().__init__("Comando no válido")


class CommandInterpreter:

    def parse_user_input(self, raw_query: str) -> tuple[Action, str]:
        splitted = raw_query.strip().split()
        if not splitted:
            return (Action(ActionType.CONTINUE_CONVERSATION), raw_query)
        action = None
        first = splitted[0]
        if not first.startswith("/"):
            return (Action(ActionType.CONTINUE_CONVERSATION), raw_query)

        match first[1:]:
            case "q" | "quit" | "exit":
                action = Action(ActionType.SALIR)
            case "h" | "help":
                action = Action(ActionType.HELP)
            case "d" | "debug":
                action = Action(ActionType.DEBUG)
            case "load":
                action = Action(ActionType.LOAD_CONVERSATION)
            case "load_msgs":
                action = Action(ActionType.LOAD_MESSAGES)
            case "new":
                action = Action(ActionType.NEW_CONVERSATION)
            case "change":
                action = Action(ActionType.CHANGE_MODEL)
            case "show":
                action = Action(ActionType.SHOW_MODEL)
            case "sys" | "system":
                action = Action(ActionType.SYSTEM_PROMPT)
            case _:
                raise CommandNoValid()
        assert action
        return (action, " ".join(splitted[1:]))
