from src.generic_view import Raw
from src.infrastructure.exceptions import LLMChatException
from src.io_helpers import show_error_msg
from examples.shop.main import Main


if __name__ == "__main__":
    main = Main()
    try:
        main.execute()
    except LLMChatException as err:
        show_error_msg(Raw(str(err)))
        print()
