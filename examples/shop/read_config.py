from typing import Any, cast
import tomlkit
from pathlib import Path

default_config_file = Path(__file__).parent / "config.toml"


class ConfigReader:
    def __init__(self, config_file: str | Path | None = None):
        self._config_file: str | Path = config_file or default_config_file

    def _get_config_doc(self) -> Any | None:
        if not Path(self._config_file).exists():
            print(f"Error al leer el archivo de configuración")
            return None
        with open(self._config_file, "r", encoding="utf-8") as file:
            config: Any = tomlkit.load(file)
        return config

    def read_use_system_config(self) -> bool:
        default_config = {"use_system": True}
        if doc := self._get_config_doc():
            value = cast(
                bool,
                doc.get("use_system", default_config["use_system"]),
            )
            return value
        else:
            return default_config["use_system"]

    def read_model_config(self) -> str | None:
        if doc := self._get_config_doc():
            value = doc.get("model")
            assert isinstance(value, str)
            return value
        else:
            return None


if __name__ == "__main__":
    config_reader = ConfigReader()
    use_system = config_reader.read_use_system_config()
    print(f"Use system: {use_system}")
    model = config_reader.read_model_config()
    print(f"Model: {model}")
