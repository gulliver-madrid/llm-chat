class LLMChatException(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)


class ClientNotDefined(LLMChatException):
    def __init__(self, client_name: str, api_name: str):
        super().__init__(
            f"{client_name} client not defined. Did you forget to provide an api key for {api_name} API?"
        )


class TooManyRequests(LLMChatException):
    def __init__(self, total: int, seconds: float):
        super().__init__(f"Too many API requests: {total} in {seconds} seconds")


class APIConnectionError(LLMChatException):
    def __init__(self, api_name: str):
        super().__init__(
            f"Connection error with the {api_name} API. Please check your internet connection."
        )
