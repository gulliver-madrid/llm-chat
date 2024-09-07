from src.infrastructure.exceptions import LLMChatException
from src.view import Raw, show_error_msg

from .main import Main

if __name__ == "__main__":
    main = Main()
    try:
        main.execute()
    except LLMChatException as err:
        show_error_msg(Raw(str(err)))
        print()
