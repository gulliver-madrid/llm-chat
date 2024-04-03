from typing import Any, cast
import tomlkit
from pathlib import Path

default_config_file = Path(__file__).parent / "config.toml"


def read_use_system_config(config_file: Path | str = default_config_file) -> bool:
    default_config = {"use_system": True}
    try:
        if Path(config_file).exists():
            with open(config_file, "r", encoding="utf-8") as file:
                config: Any = tomlkit.load(file)
            value = cast(bool, config.get("use_system", default_config["use_system"]))
            return value
        else:
            return default_config["use_system"]
    except Exception as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return default_config["use_system"]


def read_model_config(config_file: Path | str = default_config_file) -> str | None:
    try:
        if Path(config_file).exists():
            with open(config_file, "r", encoding="utf-8") as file:
                config: Any = tomlkit.load(file)
            value = config.get("model")
            assert isinstance(value, str)
            return value
        else:
            return None
    except Exception as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return None


if __name__ == "__main__":
    use_system = read_use_system_config()
    print(f"Use system: {use_system}")
    model = read_model_config()
    print(f"Model: {model}")
