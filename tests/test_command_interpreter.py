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
    expected_rest_query: str


def test_command_interpreter_help() -> None:
    command_interpreter = CommandInterpreter()
    for case in [
        Case("/help", ActionType.HELP, ""),
        Case("/debug hola que tal", ActionType.DEBUG, "hola que tal"),
        Case("/new hola que tal", ActionType.NEW_CONVERSATION, "hola que tal"),
        Case("/load 5555", ActionType.LOAD_CONVERSATION, "5555"),
        Case(
            "/sys Eres un asistente experto.",
            ActionType.SYSTEM_PROMPT,
            "Eres un asistente experto.",
        ),
    ]:
        action, rest_query = command_interpreter.parse_user_input(case.raw_query)
        assert action
        assert action.name == case.expected_action_name
        assert rest_query == case.expected_rest_query


def test_command_interpreter_wrong_command() -> None:
    command_interpreter = CommandInterpreter()
    with pytest.raises(CommandNoValid):
        command_interpreter.parse_user_input("/helper")
