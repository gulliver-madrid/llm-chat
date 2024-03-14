from typing import Final, NewType, Sequence

ModelName = NewType("ModelName", str)

MODEL_PREFIX = "mistral"
models: Final[Sequence[str]] = ["tiny", "small", "medium", "large-2402"]


def parse_model_choice(modelos: Sequence[str], eleccion: str) -> str :
    # Asegurarse de que la eleccion es valida
    try:
        eleccion_numerica = int(eleccion)
    except ValueError:
        raise ValueError(
            "Entrada no válida. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )


    if 1 <= eleccion_numerica <= len(modelos):
        modelo_elegido = modelos[eleccion_numerica - 1]
        return modelo_elegido
    else:
        raise ValueError(
            "Número fuera de rango. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )






def build_model_name(suffix: str) -> ModelName:
    assert suffix in models
    return ModelName(MODEL_PREFIX + "-" + suffix)
