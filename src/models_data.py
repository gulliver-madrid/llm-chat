from typing import Final, Sequence

from src.models.model_choice import MISTRAL_MODEL_PREFIX
from src.models.shared import Model, ModelName, Platform


mistral_models: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]
openai_models: Final[Sequence[str]] = ["gpt-3.5-turbo", "gpt-4-1106-preview"]


def get_models() -> Sequence[Model]:
    return [
        Model(Platform.Mistral, ModelName(MISTRAL_MODEL_PREFIX + "-" + model))
        for model in mistral_models
    ] + [Model(Platform.OpenAI, ModelName(model)) for model in openai_models]
