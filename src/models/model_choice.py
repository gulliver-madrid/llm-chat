from typing import NewType, NoReturn, Sequence

ModelName = NewType("ModelName", str)

MODEL_PREFIX = "mistral"


class ModelChoiceParser:

    def parse(self, modelos: Sequence[str], eleccion: str) -> str:
        # Asegurarse de que la eleccion es valida
        try:
            eleccion_numerica = int(eleccion)
        except ValueError:
            self._raise_no_numeric_input_error()

        if 1 <= eleccion_numerica <= len(modelos):
            modelo_elegido = modelos[eleccion_numerica - 1]
            return modelo_elegido

        self._raise_out_of_range_input_error()

    # private methods

    def _raise_out_of_range_input_error(self) -> NoReturn:
        raise ValueError(
            "Número fuera de rango. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )

    def _raise_no_numeric_input_error(self) -> NoReturn:
        raise ValueError(
            "Entrada no válida. Por favor introduce un número válido o solo pulsa Enter para seleccionar el modelo por defecto."
        )


def build_model_name(suffix: str, models: Sequence[str]) -> ModelName:
    assert suffix in models
    return ModelName(MODEL_PREFIX + "-" + suffix)
