from unittest.mock import Mock
from src.command_handler import CommandHandler
from src.controllers.command_interpreter import Action, ActionType
from src.controllers.select_model import SelectModelController
from src.infrastructure.client_wrapper import ClientWrapper
from src.infrastructure.repository import ChatRepository
from src.models.shared import CompleteMessage
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
