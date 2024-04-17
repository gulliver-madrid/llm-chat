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
from src.models.serialization import ConversationId
from src.models.shared import CompleteMessage, Model, ModelName
from src.view import View
from tests.objects import TEXT_1


class TestCommandHandlerBase:
    """
    Base class for testing command handlers. This class should not be directly instantiated.
    Therefore it should not include tests.
    """

    def setup_method(self) -> None:
        """
        Sets up necessary mock objects and initial state for each test method.
        """
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
        """
        Tests that system prompts can be processed and the result is added to previous
        messages correctly.
        """
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
        """
        Sets up additional variables and inherits the base setup, define a multiline
        user prompt to ensure that tests avoid infinite loops in mutation testing.
        """
        super().setup_method()
        self.model_name = ModelName("Model name test")
        # if a line is not sent before the `end` command, there is a risk
        # of creating an infinite loop when running the mutation tests
        self.user_prompt_lines = ["something more", "end"]

    def _select_model(self) -> None:
        """
        Private helper method for selecting a model using the SelectModelController mock.
        """
        self.mock_select_model_controler.select_model.return_value = Model(
            None, self.model_name
        )
        self.command_handler.prompt_to_select_model()

    def test_show_model_works_when_no_extra_chat(self) -> None:
        """
        Tests that displaying the current model works correctly when no extra chat is present.
        """
        remaining = ""
        self._select_model()

        self.command_handler.process_action(Action(ActionType.SHOW_MODEL), remaining)

        assert len(self.prev_messages_stub) == 0
        self.mock_view.display_neutral_msg.assert_called_once_with(
            Raw("El modelo actual es Model name test")
        )

    def test_show_model_fails_when_there_is_extra_prompt(self) -> None:
        """
        Tests that an error is raised when extraneous text is present in the prompt after
        the command to show the model.
        """
        remaining = "some text"
        self._select_model()

        with pytest.raises(ValueError):
            self.command_handler.process_action(
                Action(ActionType.SHOW_MODEL), remaining
            )

    def test_chat_with_model(self) -> None:
        """
        Simulates a conversation with the model, checking the correct continuation of interaction.
        """
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
        print_interaction_calls = self.mock_view.print_interaction.mock_calls
        assert len(print_interaction_calls) == 1
        assert len(self.prev_messages_stub) == 2

    def test_chat_with_model_using_placeholder(self) -> None:
        """
        Checks that substitutions are made in the user's message, and a model response
        is requested.
        """
        user_substitutions = {"$0something": "anything"}
        self.mock_view.input_extra_line.side_effect = self.user_prompt_lines
        self.mock_view.get_raw_substitutions_from_user.return_value = user_substitutions
        self.mock_client_wrapper.get_simple_response.side_effect = (
            get_simple_response_stub
        )
        remaining = "hello, how are you? What is $0something?"
        expected_user_content_replaced = (
            "hello, how are you? What is anything?\nsomething more"
        )
        self._select_model()

        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), remaining
        )

        self.mock_client_wrapper.get_simple_response.assert_called()
        calls = self.mock_client_wrapper.get_simple_response.mock_calls
        print(calls)
        assert len(calls) == 1
        messages = calls[0].args[1]
        assert len(messages) == 2
        user_message_replaced = messages[0]
        assert user_message_replaced.chat_msg.content == expected_user_content_replaced

    def test_chat_with_model_continue(self) -> None:
        """
        Simulates a conversation with the model, checking the correct continuation of
        interaction (although the model repeats the same thing for simplicity).
        """
        # arrange
        self.mock_view.input_extra_line.side_effect = (
            self.user_prompt_lines + self.user_prompt_lines
        )
        self.mock_client_wrapper.get_simple_response.side_effect = (
            get_simple_response_stub
        )
        user_prompt = "hello, how are you?"
        self._select_model()

        # act
        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), user_prompt
        )
        self.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), "then, again, how are you?"
        )

        # assert
        self.mock_client_wrapper.get_simple_response.assert_called()
        self.mock_view.print_interaction.assert_called()
        calls = self.mock_view.print_interaction.mock_calls
        assert len(calls) == 2
        assert len(self.prev_messages_stub) == 4

    def test_show_help_wait_user_press_enter(self) -> None:
        """
        Tests the help display functionality, requiring the user to press enter to proceed.
        """
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

    def test_debug_command_works(self) -> None:
        """
        Tests the debug functionality within the model interaction, ensuring the debug flag
        is correctly sent to ClientWrapper instance.
        """
        remaining = "some text"
        self.mock_view.input_extra_line.side_effect = self.user_prompt_lines
        self.mock_client_wrapper.get_simple_response.return_value = QueryResult("", [])

        self._select_model()

        self.command_handler.process_action(Action(ActionType.DEBUG), remaining)

        calls = self.mock_client_wrapper.get_simple_response.mock_calls
        assert len(calls) == 1
        assert calls[0].kwargs["debug"] == True

    def test_load_conversation(self) -> None:
        """
        Tests the loading of a specific conversation by ID, checking calls to retrieval
        and display of conversation data.
        """
        remaining = "42"
        self.mock_repository.load_conversation_as_text.return_value = TEXT_1

        self._select_model()

        self.command_handler.process_action(
            Action(ActionType.LOAD_CONVERSATION), remaining
        )

        self.mock_repository.load_conversation_as_text.assert_called_once()
        self.mock_view.display_conversation.assert_called_once()
        calls = self.mock_view.display_conversation.mock_calls
        assert calls[0].args[0] == ConversationId("0042")
        self.mock_view.display_neutral_msg.assert_called_once_with(
            Raw("La conversación ha sido cargada")
        )


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
