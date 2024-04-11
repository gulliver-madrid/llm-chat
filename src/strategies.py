from abc import ABC, abstractmethod


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
