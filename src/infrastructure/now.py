from datetime import datetime
from typing import TYPE_CHECKING

from src.protocols import TimeManagerProtocol


class TimeManager:
    def get_current_time(self) -> str:
        ahora = datetime.now()
        return ahora.strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    # Get current date and time
    now = datetime.now()

    print(f"Fecha y hora actuales: {now}")

    formato = TimeManager().get_current_time()

    print(f"Fecha y hora con formato: {formato}")


if __name__ == "__main__":
    main()


if TYPE_CHECKING:
    time_manager: TimeManager
    protocol: TimeManagerProtocol = time_manager  # pyright: ignore
