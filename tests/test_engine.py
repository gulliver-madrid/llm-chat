from unittest.mock import Mock

from src.command_handler import CommandHandler
from src.controllers.command_interpreter import CommandInterpreter, CommandNoValid
from src.controllers.select_model import SelectModelController
from src.engine import MainEngine
from src.generic_view import Raw
from src.view import View


class TestMainEngine:
    def setup_method(self) -> None:
        """Configura los mocks y la instancia de MainEngine para cada método de test."""

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

    def test_initiate(self) -> None:
        """Test to verify that prompt_to_select_model is called"""

        self.engine.initiate()

        self.mock_command_handler.prompt_to_select_model.assert_called_once()

    def test_process_raw_query_successful(self) -> None:
        """
        Checks that MainEngine.process_raw_query() properly processes a successful query.
        """

        action = "action_test"
        remaining_input = "remaining_test"
        query = "dummy query"
        self.mock_command_interpreter.parse_user_input.return_value = (
            action,
            remaining_input,
        )

        self.engine.process_raw_query(query)

        self.mock_command_interpreter.parse_user_input.assert_called_once_with(query)
        self.mock_command_handler.process_action.assert_called_once_with(
            action, remaining_input
        )

    def test_process_raw_query_with_exception(self) -> None:
        """
        Checks that MainEngine.process_raw_query() properly handles a query that raises an exception.
        """
        query = "/bad query"
        self.mock_command_interpreter.parse_user_input.side_effect = CommandNoValid(
            "bad"
        )

        self.engine.process_raw_query(query)

        self.mock_command_interpreter.parse_user_input.assert_called_once_with(query)
        self.mock_command_handler.process_action.assert_not_called()
        self.mock_view.show_error_msg.assert_called_once_with(
            Raw("No valid command: bad")
        )
