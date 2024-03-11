from rich import print


def show(chat_response: object) -> None:
    for attr in dir(chat_response):
        if not attr.startswith("_"):
            print("\n", attr, getattr(chat_response, attr))
