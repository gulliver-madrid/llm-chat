from rich import print

from src.ahora import get_current_time
from src.io_helpers import highlight_role


def print_interaction(model: str, question: str, content: str) -> None:
    """Prints an interaction between user and model"""
    print("\n" + get_current_time())
    print("\n" + highlight_role("USER: ") + question)
    print("\n" + highlight_role(model.upper() + ": ") + content)
