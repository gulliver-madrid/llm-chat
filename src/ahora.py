from datetime import datetime


def main() -> None:
    # Obtener la fecha y hora actuales
    ahora = datetime.now()

    print(f"Fecha y hora actuales: {ahora}")

    formato = get_current_time()

    print(f"Fecha y hora con formato: {formato}")


def get_current_time() -> str:
    ahora = datetime.now()
    return ahora.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
