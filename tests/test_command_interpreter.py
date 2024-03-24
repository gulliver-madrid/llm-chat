import pytest
from src.controllers.command_interpreter import (
    ActionName,
    CommandInterpreter,
    CommandNoValid,
)


def test_command_interpreter_ok() -> None:
    command_interpreter = CommandInterpreter()
    result = command_interpreter.parse_user_input("/help")
    assert result
    assert result.name == ActionName.HELP


def test_command_interpreter() -> None:
    command_interpreter = CommandInterpreter()
    with pytest.raises(CommandNoValid):
        command_interpreter.parse_user_input("/helper")
