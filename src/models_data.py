from typing import Final, Mapping, Sequence

from src.domain import Model, ModelName, Platform

models_data: Final[Mapping[Platform, Sequence[str]]] = {
    Platform.Mistral: (
        "mistral-tiny",
        "mistral-small-latest",
        "mistral-medium",
        "mistral-large-2402",
    ),
    Platform.OpenAI: ("gpt-3.5-turbo", "gpt-4-1106-preview"),
}


def get_models() -> Sequence[Model]:
    models: list[Model] = []
    for platform, model_name_strings in models_data.items():
        for model_name_str in model_name_strings:
            models.append(Model(platform, ModelName(model_name_str)))
    return models
