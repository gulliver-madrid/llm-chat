from abc import ABC, abstractmethod

from src.models.shared import CompleteMessage, define_system_prompt
from src.view import View


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class EstablishSystemPromptAction(ActionStrategy):
    def __init__(
        self, view: View, prev_messages: list[CompleteMessage], remaining_input: str
    ):
        self._view = view
        self._prev_messages = prev_messages
        self._remaining_input = remaining_input

    def execute(self) -> None:
        # TODO: allow multiline
        self._prev_messages[:] = [define_system_prompt(self._remaining_input)]
        self._view.write_object("System prompt established")
