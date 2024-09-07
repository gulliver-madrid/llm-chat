from pathlib import Path
from types import NoneType
from typing import Any, cast

import tomlkit

default_config_file = Path(__file__).parent / "config.toml"


class ConfigReader:
    def __init__(self, config_file: str | Path | None = None):
        self._config_file: str | Path = config_file or default_config_file
        self._config = self._get_config_doc()

    def read_use_system_config(self) -> bool:
        default = True
        if doc := self._config:
            value = cast(
                bool,
                doc.get("use_system", default),
            )
            return value
        return default

    def read_model_config(self) -> str | None:
        if doc := self._config:
            value = doc.get("model")
            assert isinstance(value, (NoneType, str))
            return value
        return None

    def _get_config_doc(self) -> Any | None:
        if not Path(self._config_file).exists():
            if self._config_file != default_config_file:
                print(f"No se encontró el archivo de configuración")
            return None
        with open(self._config_file, "r", encoding="utf-8") as file:
            config: Any = tomlkit.load(file)
        return config


if __name__ == "__main__":
    config_reader = ConfigReader()
    use_system = config_reader.read_use_system_config()
    print(f"Use system: {use_system}")
    model = config_reader.read_model_config()
    print(f"Model: {model}")
