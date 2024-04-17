from src.controllers.select_model import SelectModelController
from src.models_data import get_models


def test_default_model() -> None:
    select_model_controller = SelectModelController(get_models())
    assert (
        select_model_controller._default_model.model_name  # pyright: ignore [reportPrivateUsage]
        == "mistral-tiny"
    )
