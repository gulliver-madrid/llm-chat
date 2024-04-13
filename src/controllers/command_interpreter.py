from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final


class ActionType(Enum):
    EXIT = "EXIT"
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
    def __init__(self, wrong_command: str) -> None:
        super().__init__(f"Comando no válido: {wrong_command}")


command_map = {
    ActionType.EXIT: ("q", "quit", "exit"),
    ActionType.HELP: ("h", "help"),
    ActionType.DEBUG: ("d", "debug"),
    ActionType.LOAD_CONVERSATION: ("load",),
    ActionType.LOAD_MESSAGES: ("load_msgs",),
    ActionType.NEW_CONVERSATION: ("new",),
    ActionType.CHANGE_MODEL: ("change",),
    ActionType.SHOW_MODEL: ("show",),
    ActionType.SYSTEM_PROMPT: ("sys", "system"),
}


class CommandInterpreter:
    def __init__(self) -> None:
        self._commands_to_actions: Final = self._build_commands_to_actions()

    def parse_user_input(self, raw_query: str) -> tuple[Action, str]:
        splitted = raw_query.strip().split()
        if not splitted:
            return (Action(ActionType.CONTINUE_CONVERSATION), raw_query)
        action = None
        first = splitted[0]
        if not first.startswith("/"):
            return (Action(ActionType.CONTINUE_CONVERSATION), raw_query)

        command = first[1:]
        action_type = self._commands_to_actions.get(command)
        if not action_type:
            raise CommandNoValid(command)
        action = Action(action_type)
        return (action, " ".join(splitted[1:]))

    def _build_commands_to_actions(self) -> Mapping[str, ActionType]:
        commands_to_actions: dict[str, ActionType] = {}
        for action_type, strings in command_map.items():
            for s in strings:
                assert s not in commands_to_actions
                commands_to_actions[s] = action_type
        return commands_to_actions
