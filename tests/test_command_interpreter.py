from dataclasses import dataclass
import pytest
from src.controllers.command_interpreter import (
    ActionType,
    CommandInterpreter,
    CommandNoValid,
)


@dataclass(frozen=True)
class Case:
    raw_query: str
    expected_action_name: ActionType
    expected_remaining_input: str


def test_command_interpreter_valid_command() -> None:
    command_interpreter = CommandInterpreter()
    for case in [
        Case("/help", ActionType.HELP, ""),
        Case("/debug hola que tal", ActionType.DEBUG, "hola que tal"),
        Case("/d hola que tal", ActionType.DEBUG, "hola que tal"),
        Case("/new hola que tal", ActionType.NEW_CONVERSATION, "hola que tal"),
        Case("/load 5555", ActionType.LOAD_CONVERSATION, "5555"),
        Case(
            "/sys Eres un asistente experto.",
            ActionType.SYSTEM_PROMPT,
            "Eres un asistente experto.",
        ),
        Case(
            "/system Eres un asistente experto.",
            ActionType.SYSTEM_PROMPT,
            "Eres un asistente experto.",
        ),
        Case("hola que tal", ActionType.CONTINUE_CONVERSATION, "hola que tal"),
        Case("", ActionType.CONTINUE_CONVERSATION, ""),
    ]:
        action, remaining_input = command_interpreter.parse_user_input(case.raw_query)
        assert action
        assert action.type == case.expected_action_name
        assert remaining_input == case.expected_remaining_input


def test_command_interpreter_wrong_command() -> None:
    command_interpreter = CommandInterpreter()
    for wrong_command in ["/", "/helper", "/quit99"]:
        with pytest.raises(CommandNoValid):
            command_interpreter.parse_user_input(wrong_command)
