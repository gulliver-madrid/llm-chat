from unittest.mock import Mock

import pytest

from src.command_handler import CommandHandler
from src.controllers.command_interpreter import CommandInterpreter, CommandNoValid
from src.controllers.select_model import SelectModelController
from src.engine import MainEngine
from src.generic_view import Raw
from src.view import View


class EngineFixture:
    def __init__(self) -> None:
        """Configura los mocks y la instancia de MainEngine para cada metodo de test."""

        self.mock_command_handler = Mock(spec=CommandHandler)
        self.mock_command_interpreter = Mock(spec=CommandInterpreter)
        self.mock_select_model_controller = Mock(spec=SelectModelController)
        self.mock_view = Mock(spec=View)

        self.engine = MainEngine(
            models=[],
            command_interpreter=self.mock_command_interpreter,
            command_handler=self.mock_command_handler,
            select_model_controler=self.mock_select_model_controller,
            view=self.mock_view,
        )


@pytest.fixture
def engine_fixture() -> EngineFixture:
    return EngineFixture()


def test_initiate(engine_fixture: EngineFixture) -> None:
    """Test to verify that prompt_to_select_model is called"""

    engine_fixture.engine.initiate()

    engine_fixture.mock_command_handler.prompt_to_select_model.assert_called_once()


def test_process_raw_query_successful(engine_fixture: EngineFixture) -> None:
    """
    Checks that MainEngine.process_raw_query() properly processes a successful query.
    """

    action = "action_test"
    remaining_input = "remaining_test"
    query = "dummy query"
    engine_fixture.mock_command_interpreter.parse_user_input.return_value = (
        action,
        remaining_input,
    )

    engine_fixture.engine.process_raw_query(query)

    engine_fixture.mock_command_interpreter.parse_user_input.assert_called_once_with(
        query
    )
    engine_fixture.mock_command_handler.process_action.assert_called_once_with(
        action, remaining_input
    )


def test_process_raw_query_with_exception(engine_fixture: EngineFixture) -> None:
    """
    Checks that MainEngine.process_raw_query() properly handles a query that raises an exception.
    """
    query = "/bad query"
    engine_fixture.mock_command_interpreter.parse_user_input.side_effect = (
        CommandNoValid("bad")
    )

    engine_fixture.engine.process_raw_query(query)

    engine_fixture.mock_command_interpreter.parse_user_input.assert_called_once_with(
        query
    )
    engine_fixture.mock_command_handler.process_action.assert_not_called()
    engine_fixture.mock_view.show_error_msg.assert_called_once_with(
        Raw("No valid command: bad")
    )
