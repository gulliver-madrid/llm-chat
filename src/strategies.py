from abc import ABC, abstractmethod

from src.models.shared import CompleteMessage, define_system_prompt
from src.view import View


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, remaining_input: str) -> None:
        pass


class EstablishSystemPromptAction(ActionStrategy):
    def __init__(self, view: View, prev_messages: list[CompleteMessage]):
        self._view = view
        self._prev_messages = prev_messages

    def execute(self, remaining_input: str) -> None:
        # TODO: allow multiline
        self._prev_messages[:] = [define_system_prompt(remaining_input)]
        self._view.write_object("System prompt established")
