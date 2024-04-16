from typing import Any, cast
from unittest.mock import Mock

import pytest

from src.command_handler import CommandHandler
from src.controllers.command_interpreter import Action, ActionType
from src.controllers.select_model import SelectModelController
from src.generic_view import Raw
from src.infrastructure.ahora import TimeManager
from src.infrastructure.llm_connection import ClientWrapper
from src.infrastructure.llm_connection.client_wrapper import QueryResult
from src.infrastructure.repository import ChatRepository
from src.models.shared import CompleteMessage, Model, ModelName
from src.view import View


class TestCommandHandlerBase:
    """This class should not be directly instantiated"""

    def setup_method(self) -> None:
        self.mock_view = Mock(spec=View)
        self.mock_select_model_controler = Mock(spec=SelectModelController)
        self.mock_repository = Mock(spec=ChatRepository)
        self.mock_time_manager = Mock(spec=TimeManager)
        self.mock_time_manager.get_current_time.return_value = "2024-03-01 01:30:00"
        self.mock_client_wrapper = Mock(spec=ClientWrapper)
        self.prev_messages_stub: list[CompleteMessage] = []
        self.command_handler = CommandHandler(
            view=self.mock_view,
            select_model_controler=self.mock_select_model_controler,
            repository=self.mock_repository,
            time_manager=self.mock_time_manager,
            client_wrapper=self.mock_client_wrapper,
            prev_messages=self.prev_messages_stub,
        )


class TestCommandHandlerMultipleActions(TestCommandHandlerBase):
    def test_process_system(self) -> None:
        system_prompt = "System prompt string"
        self.command_handler.process_action(
            Action(ActionType.SYSTEM_PROMPT), system_prompt
        )
        assert len(self.prev_messages_stub) == 1
        first_chat_msg = self.prev_messages_stub[0].chat_msg
        assert first_chat_msg.role == "system"
        assert first_chat_msg.content == system_prompt
        self.mock_view.write_object.assert_called_once_with("System prompt established")


class TestCommandHandlerShowModel(TestCommandHandlerBase):
    def setup_method(self) -> None:
        super().setup_method()
        self.model_name = ModelName("Model name test")
        self.user_prompt_lines = ["something more", "end"]

    def _select_model(self) -> None:
        self.mock_select_model_controler.select_model.return_value = Model(
            None, self.model_name
        )
        self.command_handler.prompt_to_select_model()

    def test_show_model_works_when_no_extra_prompt(self) -> None:
        remaining = ""
        self._select_model()

        self.command_handler.process_action(Action(ActionType.SHOW_MODEL), remaining)

        assert len(self.prev_messages_stub) == 0
        self.mock_view.display_neutral_msg.assert_called_once_with(
            Raw("El modelo actual es Model name test")
        )

    def test_show_model_fails_when_there_is_extra_prompt(self) -> None:
        remaining = "some text"
        self._select_model()

        with pytest.raises(ValueError):
            self.command_handler.process_action(
                Action(ActionType.SHOW_MODEL), remaining
            )

    def test_chat_with_model(self) -> None:
        self.mock_view.input_extra_line.side_effect = self.user_prompt_lines
        self.mock_client_wrapper.get_simple_response.side_effect = (
            get_simple_response_stub
        )

        remaining = "hello, how are you?"
        self._select_model()

        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), remaining
        )
        self.mock_view.print_interaction.assert_called()
        calls = self.mock_view.print_interaction.mock_calls
        assert len(calls) == 1

        assert len(self.prev_messages_stub) == 2

    def test_chat_with_model_continue(self) -> None:
        """Simula una conversacion que continua (aunque el modelo repite lo mismo por simplificar)"""

        self.mock_view.input_extra_line.side_effect = (
            self.user_prompt_lines + self.user_prompt_lines
        )
        self.mock_client_wrapper.get_simple_response.side_effect = (
            get_simple_response_stub
        )

        user_prompt = "hello, how are you?"
        self._select_model()

        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), user_prompt
        )
        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), "then, again, how are you?"
        )
        self.mock_view.print_interaction.assert_called()
        calls = self.mock_view.print_interaction.mock_calls
        assert len(calls) == 2
        assert len(self.prev_messages_stub) == 4

    def test_show_help_wait_user_press_enter(self) -> None:
        remaining = ""
        self._select_model()

        self.command_handler.process_action(Action(ActionType.HELP), remaining)

        assert len(self.prev_messages_stub) == 0
        self.mock_view.simple_view.get_input.assert_called_once()
        calls = self.mock_view.simple_view.get_input.mock_calls
        assert len(calls) == 1
        prompt_for_user = calls[0].args[0]
        assert isinstance(prompt_for_user, Raw)
        assert "enter" in prompt_for_user.value.lower()


def get_simple_response_stub(
    _model: Model,
    messages: list[CompleteMessage],
    debug: bool = False,
) -> QueryResult:
    messages.append(Mock(spec=CompleteMessage))
    return QueryResult(
        "",
        messages,
    )


def get_print_interaction_content_arg(call: Any) -> Raw:
    return cast(Raw, call.args[3])
