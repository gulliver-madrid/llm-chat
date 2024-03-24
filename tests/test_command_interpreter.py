import pytest
from src.controllers.command_interpreter import (
    ActionName,
    CommandInterpreter,
    CommandNoValid,
)


def test_command_interpreter_help() -> None:
    command_interpreter = CommandInterpreter()
    action, rest_query = command_interpreter.parse_user_input("/help")
    assert action
    assert action.name == ActionName.HELP
    assert rest_query == ""


def test_command_interpreter_wrong_command() -> None:
    command_interpreter = CommandInterpreter()
    with pytest.raises(CommandNoValid):
        command_interpreter.parse_user_input("/helper")


def test_command_interpreter_debug() -> None:
    command_interpreter = CommandInterpreter()
    action, rest_query = command_interpreter.parse_user_input("/debug hola que tal")
    assert action
    assert action.name == ActionName.DEBUG
    assert rest_query == "hola que tal"


def test_command_interpreter_new() -> None:
    command_interpreter = CommandInterpreter()
    action, rest_query = command_interpreter.parse_user_input("/new hola que tal")
    assert action
    assert action.name == ActionName.NEW_CONVERSATION
    assert rest_query == "hola que tal"


def test_command_interpreter_load() -> None:
    command_interpreter = CommandInterpreter()
    action, rest_query = command_interpreter.parse_user_input("/load 5555")
    assert action
    assert action.name == ActionName.LOAD_CONVERSATION
    assert rest_query == "5555"


def test_command_interpreter_system() -> None:
    command_interpreter = CommandInterpreter()
    action, rest_query = command_interpreter.parse_user_input(
        "/sys Eres un asistente experto."
    )
    assert action
    assert action.name == ActionName.SYSTEM_PROMPT
    assert rest_query == "Eres un asistente experto."
