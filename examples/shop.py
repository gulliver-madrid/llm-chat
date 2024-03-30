from dataclasses import dataclass
import json
import os
from pprint import pformat
import re
from typing import Any, Final, Mapping, cast

from rich import print
from dotenv import load_dotenv

from examples.shop_data import ProductsData, data
from src.domain import ChatMessage
from src.infrastructure.client_wrapper import ClientWrapper, QueryResult
from src.io_helpers import display_neutral_msg, get_input
from src.logging import configure_logger
from src.models.shared import CompleteMessage, Model, ModelName, Platform

logger = configure_logger(__name__, __file__)


@dataclass(frozen=True)
class Function:
    name: str
    arguments: str


@dataclass(frozen=True)
class ToolCall:
    function: Function


models: Mapping[str, ModelName] = dict(
    medium=ModelName("mistral-medium"), large=ModelName("mistral-large-2402")
)


def _retrieve_product_prices(names_in_english: list[str]) -> dict[str, float | None]:
    prices: dict[str, float | None] = {}
    for name in names_in_english:
        for product in data["products"]:
            if product["name"]["english"] == name:
                prices[name] = product["price"]
                break
        else:
            prices[name] = None
    assert len(prices) == len(names_in_english)
    return prices


def retrieve_product_prices(names_in_english: list[str]) -> str:
    return json.dumps(_retrieve_product_prices(names_in_english))


tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_product_prices",
            "description": "Get prices of a list of articles",
            "parameters": {
                "type": "object",
                "properties": {
                    "names_in_english": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of the products which prices do you want",
                    }
                },
                "required": ["names_in_english"],
            },
        },
    }
]


def format_products_for_assistant(data: ProductsData) -> str:
    lines: list[str] = []
    for product in data["products"]:
        product_name = product["name"]
        lines.append(
            f'- {product_name["english"]} (spanish: {product_name["spanish"]})'
        )
    return "\n".join(lines)


def create_system_prompt() -> str:
    return f"""You are a virtual assistant in a clothing store. Your role is to provide accurate and up-to-date information about the available products, their prices, and anything else the customers may ask. Your tone should be friendly and professional. Your goal is to provide a positive customer experience and help them find what they are looking for. The available products are these:
{format_products_for_assistant(data)}.

You should only provide the prices you can securely obtain through our system.

If you are asked the price of one or more products, you must use the provided tool (the `retrieve_product_prices` function). If you cannot obtain the price of a product, simply say that you cannot provide that information at the moment due to a technical issue. If there are multiple products whose price cannot be obtained, you should not give the explanation for each product, but only once for all of them.

Always respond in the language used by the customer.
"""


class Main:
    _client: ClientWrapper

    def __init__(self) -> None:
        self._messages: Final[list[CompleteMessage]] = []
        self._model = Model(Platform.Mistral, models["large"])

    def execute(self) -> None:
        load_dotenv()
        mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        self._client = ClientWrapper(mistral_api_key=mistral_api_key)
        self._messages.clear()
        self._messages.extend(self._client.define_system_prompt(create_system_prompt()))
        user_query = get_input("Pregunta lo que quieras sobre nuestra tienda")

        response = self._client.get_simple_response_to_query(
            self._model,
            user_query,
            self._messages,
            tools=tools,
            tool_choice="auto",
        )
        self._messages.clear()
        self._messages.extend(response.messages)
        last_message = self._messages[-1]

        tool_calls: list[ToolCall] | None = cast(Any, last_message.chat_msg.tool_calls)

        if not tool_calls:
            tool_calls = self._parse_tool_calls_from_content(last_message)

        if tool_calls:
            response = self._use_price_query_to_answer(tool_calls)

        print(response.content)

        logger.info("self._messages:")
        logger.info(pformat(self._messages))

    def _parse_tool_calls_from_content(
        self, last_message: CompleteMessage
    ) -> list[ToolCall]:
        tool_calls: list[ToolCall] = []
        logger.info("last_message.chat_msg.content:")
        logger.info(last_message.chat_msg.content)

        # Greedily match text enclosed by [{ and }], delimiters included
        pattern = r"(\[\{.+\}\])"

        # Use re.DOTALL so that '.' also matches newline characters
        resultado = re.search(pattern, last_message.chat_msg.content, re.DOTALL)
        if resultado:
            found = resultado.group(1)
            index = resultado.start(1)
            print(last_message.chat_msg.content[:index])
            parsed = json.loads(found)
            for item in parsed:
                name = item["name"]
                assert isinstance(name, str)
                args_parsed = item["arguments"]
                args = json.dumps(args_parsed)
                tool_calls.append(ToolCall(Function(name, args)))
        return tool_calls

    def _use_price_query_to_answer(self, tool_calls: list[ToolCall]) -> QueryResult:
        display_neutral_msg("Realizando consulta de precios...")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            assert function_name == "retrieve_product_prices"
            assert len(function_params) == 1
            assert "names_in_english" in function_params
            names_in_english = function_params.get("names_in_english")
            function_result = retrieve_product_prices(names_in_english)
            tool_response_message = create_tool_response(function_name, function_result)
            self._messages.append(CompleteMessage(tool_response_message))
        response = self._client.get_simple_response(
            self._model,
            self._messages,
            tools=tools,
            tool_choice="none",
        )

        return response


def create_tool_response(function_name: str, function_result: str) -> ChatMessage:
    return ChatMessage(role="tool", name=function_name, content=function_result)


if __name__ == "__main__":
    main = Main()
    main.execute()
