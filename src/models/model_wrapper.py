from dataclasses import dataclass, field

from src.domain import Model


@dataclass
class ModelWrapper:
    """Mutable class to hold current model inside"""

    model: Model | None = field(default=None)

    def change(self, model: Model) -> None:
        self.model = model
