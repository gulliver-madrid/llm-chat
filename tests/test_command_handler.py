from unittest.mock import Mock

import pytest
from src.command_handler import CommandHandler
from src.controllers.command_interpreter import Action, ActionType
from src.controllers.select_model import SelectModelController
from src.generic_view import Raw
from src.infrastructure.client_wrapper import ClientWrapper
from src.infrastructure.repository import ChatRepository
from src.models.shared import CompleteMessage, Model, ModelName
from src.view import View


class TestCommandHandler:
    def setup_method(self) -> None:
        self.mock_view = Mock(spec=View)
        self.mock_select_model_controler = Mock(spec=SelectModelController)
        self.mock_repository = Mock(spec=ChatRepository)
        self.mock_client_wrapper = Mock(spec=ClientWrapper)
        self.prev_messages_stub: list[CompleteMessage] = []
        self.command_handler = CommandHandler(
            self.mock_view,
            self.mock_select_model_controler,
            self.mock_repository,
            self.mock_client_wrapper,
            prev_messages=self.prev_messages_stub,
        )

    def test_process_system(self) -> None:
        system_prompt = "System prompt string"
        self.command_handler.process_action(
            Action(ActionType.SYSTEM_PROMPT), system_prompt
        )
        assert len(self.prev_messages_stub) == 1
        assert self.prev_messages_stub[0].chat_msg.role == "system"
        assert self.prev_messages_stub[0].chat_msg.content == system_prompt
        self.mock_view.write_object.assert_called_once_with("System prompt established")

    def test_show_model_right(self) -> None:
        remaining = ""
        model_name = ModelName("Model name test")
        self.mock_select_model_controler.select_model.return_value = Model(
            None, model_name
        )

        self.command_handler.prompt_to_select_model()
        self.command_handler.process_action(Action(ActionType.SHOW_MODEL), remaining)

        assert len(self.prev_messages_stub) == 0
        self.mock_view.display_neutral_msg.assert_called_once_with(
            Raw("El modelo actual es Model name test")
        )

    def test_show_model_wrong(self) -> None:
        remaining = "some text"
        model_name = ModelName("Model name test")
        self.mock_select_model_controler.select_model.return_value = Model(
            None, model_name
        )

        self.command_handler.prompt_to_select_model()
        with pytest.raises(ValueError):
            self.command_handler.process_action(
                Action(ActionType.SHOW_MODEL), remaining
            )
