from typing import NoReturn, Sequence

from src.models.shared import Model


class ModelChoiceParser:
    def __init__(self, models: Sequence[Model]) -> None:
        self._models = models

    def parse(self, eleccion: str) -> Model:
        # Asegurarse de que la eleccion es valida
        try:
            eleccion_numerica = int(eleccion)
        except ValueError:
            self._raise_no_numeric_input_error()

        if 1 <= eleccion_numerica <= len(self._models):
            return self._models[eleccion_numerica - 1]

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
