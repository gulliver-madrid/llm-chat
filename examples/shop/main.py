from collections.abc import Mapping
import json
import os
from pprint import pformat
import re
from typing import Any, Final, cast

from rich import print
from dotenv import load_dotenv

from examples.shop.function_calling import (
    FunctionCall,
    ToolCall,
    is_function_call_mapping,
)
from examples.shop.prompts import system_prompt_template
from examples.shop.read_config import read_use_system_config
from examples.shop.repository import ShopRepository
from examples.shop.tools import ToolsManager, tools
from examples.shop.types import is_object_mapping, is_object_sequence, is_str_sequence
from src.infrastructure.client_wrapper import (
    ClientWrapper,
    QueryResult,
)
from src.infrastructure.exceptions import LLMChatException
from src.io_helpers import display_neutral_msg, get_input
from src.logging import configure_logger
from src.models.shared import ChatMessage, CompleteMessage, Model, ModelName, Platform

logger = configure_logger(__name__)


class WrongFunctionName(LLMChatException):
    def __init__(self, function_name: str):
        super().__init__(function_name)


models: Final[Mapping[str, ModelName]] = dict(
    medium=ModelName("mistral-medium"), large=ModelName("mistral-large-2402")
)


class Main:
    _client: ClientWrapper

    def __init__(self) -> None:
        self._messages: Final[list[CompleteMessage]] = []
        self._model = Model(Platform.Mistral, models["large"])
        self._shop_repository = ShopRepository()
        self._tools_manager = ToolsManager(self._shop_repository)
        self.use_system = read_use_system_config()

    def execute(self) -> None:
        load_dotenv()
        mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        self._client = ClientWrapper(mistral_api_key=mistral_api_key)
        self._messages.clear()
        self._messages.extend(
            self._client.define_system_prompt(
                self._create_system_prompt(), use_system=self.use_system
            )
        )
        user_query = get_input("Pregunta lo que quieras sobre nuestra tienda")

        if user_query == "/exit":
            print("Conversación finalizada")
            quit()

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
        logger.info(pformat(self._messages, width=120))

    def _parse_tool_calls_from_content(
        self, last_message: CompleteMessage
    ) -> list[ToolCall]:
        tool_calls: list[ToolCall] = []
        last_message_content = last_message.chat_msg.content
        logger.info("last_message_content:")
        logger.info(last_message_content)

        # Greedily match text enclosed by [{ and }], delimiters included
        pattern = r"(\[\{.+\}\])"

        # Use re.DOTALL so that '.' also matches newline characters
        result = re.search(pattern, last_message_content, re.DOTALL)
        if result:
            found = result.group(1)
            index = result.start(1)
            msg_for_the_user = last_message_content[:index]
            print(msg_for_the_user)
            parsed = json.loads(found)
            assert is_object_sequence(parsed)
            for item in parsed:
                assert is_function_call_mapping(item), item
                name = item["name"]
                args_parsed = item["arguments"]
                args = json.dumps(args_parsed)
                tool_calls.append(ToolCall(FunctionCall(name, args)))
        return tool_calls

    def _use_price_query_to_answer(self, tool_calls: list[ToolCall]) -> QueryResult:
        assert tool_calls
        display_neutral_msg("Realizando consulta de precios...")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            assert is_object_mapping(function_params)
            match function_name:
                case "retrieve_product_prices":
                    assert len(function_params) == 1, function_params
                    assert "product_refs" in function_params
                    product_refs = function_params.get("product_refs")
                    assert is_str_sequence(product_refs)
                    function_result = self._tools_manager.retrieve_product_prices(
                        product_refs
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

    def _create_system_prompt(self) -> str:
        return system_prompt_template.substitute(
            {"product_list": self._format_products_for_assistant()}
        )

    def _format_products_for_assistant(self) -> str:
        lines: list[str] = []
        for product in self._shop_repository.products:
            product_name = product["name"]
            ref = product["ref"]
            english = product_name["english"]
            spanish = product_name["spanish"]
            lines.append(f"- {ref} {english} (spanish: {spanish})")
        return "\n".join(lines)


def create_tool_response(function_name: str, function_result: str) -> ChatMessage:
    return ChatMessage(role="tool", name=function_name, content=function_result)
