from enum import Enum
from typing import NewType

ModelName = NewType("ModelName", str)


class Platform(Enum):
    Mistral = "Mistral"
    OpenAI = "OpenAI"
