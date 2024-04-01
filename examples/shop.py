from dataclasses import dataclass
import json
import os
from pprint import pformat
import re
from typing import Any, Final, Mapping, Sequence, cast

from rich import print
from dotenv import load_dotenv

from examples.shop_data import ProductRef, ProductsData, get_products_data
from src.infrastructure.client_wrapper import (
    ClientWrapper,
    QueryResult,
)
from src.infrastructure.exceptions import LLMChatException
from src.io_helpers import display_neutral_msg, get_input, show_error_msg
from src.logging import configure_logger
from src.models.shared import ChatMessage, CompleteMessage, Model, ModelName, Platform

logger = configure_logger(__name__, __file__)


class WrongFunctionName(LLMChatException):
    def __init__(self, function_name: str):
        super().__init__(function_name)


@dataclass(frozen=True)
class Function:
    name: str
    arguments: str


@dataclass(frozen=True)
class ToolCall:
    function: Function


models: Final[Mapping[str, ModelName]] = dict(
    medium=ModelName("mistral-medium"), large=ModelName("mistral-large-2402")
)
products: Final[ProductsData] = get_products_data()


def _retrieve_product_prices(
    product_refs: Sequence[ProductRef],
) -> dict[str, float | None]:
    prices: dict[str, float | None] = {}
    for ref in product_refs:
        for product in products:
            if product["ref"] == ref:
                prices[ref] = product["price"]
                break
        else:
            prices[ref] = None
    assert len(prices) == len(product_refs)
    return prices


def retrieve_product_prices(product_refs: Sequence[ProductRef]) -> str:
    return json.dumps(_retrieve_product_prices(product_refs))


tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_product_prices",
            "description": "Get prices of a list of articles",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_refs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "References of the products which prices do you want",
                    }
                },
                "required": ["product_refs"],
            },
        },
    }
]


def format_products_for_assistant() -> str:
    lines: list[str] = []
    for product in products:
        product_name = product["name"]
        ref = product["ref"]
        english = product_name["english"]
        spanish = product_name["spanish"]
        lines.append(f"- {ref} {english} (spanish: {spanish})")
    return "\n".join(lines)


def create_system_prompt() -> str:
    return f"""You are a virtual assistant in a clothing store. Your role is to provide accurate and up-to-date information about the available products, their prices, and anything else the customers may ask.

You should be aware of the language used by the customer. This should be either english or spanish, and you should use the same language.

# Rules

1. Always start by greeting the customer

2. ALWAYS respond in the language used by the customer. If the customer speak spanish, you should respond in spanish.

3. Your tone should be friendly and professional.

4. Your goal is to provide a positive customer experience and help them find what they are looking for. The available products are these:
{format_products_for_assistant()}.

5. You should only provide the prices you can securely obtain through our system. If you are asked the price of one or more products, you must use the provided tool (the `retrieve_product_prices` function). If you cannot obtain the price of a product, simply say that you cannot provide that information at the moment due to a technical issue. If there are multiple products whose price cannot be obtained, you should not give the explanation for each product, but only once for all of them.
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
        assert tool_calls
        display_neutral_msg("Realizando consulta de precios...")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            assert isinstance(function_params, dict)
            function_params = cast(dict[str, object], function_params)
            match function_name:
                case "retrieve_product_prices":
                    assert len(function_params) == 1, function_params
                    assert "product_refs" in function_params
                    product_refs = function_params.get("product_refs")
                    assert isinstance(product_refs, list)
                    cast(list[ProductRef], product_refs)
                    function_result = retrieve_product_prices(
                        product_refs  # pyright: ignore [reportUnknownArgumentType]
                    )
                    tool_response_message = create_tool_response(
                        function_name, function_result
                    )
                    self._messages.append(CompleteMessage(tool_response_message))
                case _:
                    raise WrongFunctionName(function_name)
        return self._client.get_simple_response(
            self._model,
            self._messages,
            tools=tools,
            tool_choice="none",
        )


def create_tool_response(function_name: str, function_result: str) -> ChatMessage:
    return ChatMessage(role="tool", name=function_name, content=function_result)


if __name__ == "__main__":
    main = Main()
    try:
        main.execute()
    except LLMChatException as err:
        show_error_msg(str(err))
        print()
