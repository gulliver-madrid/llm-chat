from abc import ABC, abstractmethod

from src.domain import CompleteMessage
from src.models.model_wrapper import ModelWrapper
from src.models.shared import define_system_prompt
from src.protocols import ViewProtocol
from src.view import Raw


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, remaining_input: str) -> None:
        pass


class EstablishSystemPromptAction(ActionStrategy):
    def __init__(self, view: ViewProtocol, prev_messages: list[CompleteMessage]):
        self._view = view
        self._prev_messages = prev_messages

    def execute(self, remaining_input: str) -> None:
        # TODO: allow multiline
        self._prev_messages[:] = [define_system_prompt(remaining_input)]
        self._view.write_object("System prompt established")


class ShowModelAction(ActionStrategy):
    def __init__(self, view: ViewProtocol, model_wrapper: ModelWrapper):
        self._view = view
        self._model_wrapper = model_wrapper

    def execute(self, remaining_input: str) -> None:
        if remaining_input.strip():
            raise ValueError(remaining_input)
        self._show_model()

    def _show_model(self) -> None:
        assert self._model_wrapper.model
        self._view.display_neutral_msg(
            Raw(f"El modelo actual es {self._model_wrapper.model.model_name}")
        )
