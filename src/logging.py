import logging
from pathlib import Path
from pprint import pformat


# Funcion para configurar un logger y enviar su salida a un archivo
def configure_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    log_file_name = f"{name}.log"
    # Crea un logger especifico
    logger = logging.getLogger(name)
    logger.propagate = False  # Evita la propagacion al logger raiz
    logger.setLevel(level)  # Establece el nivel del logger

    # Crea un FileHandler especifico para escribir en un archivo
    path = Path("logs")
    if not path.exists():
        path.mkdir()
    file_handler = logging.FileHandler(path / log_file_name, encoding="utf-8")
    file_handler.setLevel(level)  # Establece el nivel del FileHandler

    # Crea un formateador y anadelo al FileHandler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Anade el FileHandler al logger
    logger.addHandler(file_handler)
    logger.info("\n")
    logger.info("START")

    return logger


def format_var(name: str, obj: object) -> str:
    return name + "=" + pformat(obj, width=120)
