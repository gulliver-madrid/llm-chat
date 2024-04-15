import json
import os
import re
from typing import Any, Final, cast

from dotenv import load_dotenv

from examples.shop.function_calling import (
    FunctionCall,
    ToolCall,
    WrongFunctionName,
    is_function_call_mapping,
)
from examples.shop.prompt_generator import SystemPromptGenerator
from examples.shop.read_config import ConfigReader
from examples.shop.repository import ShopRepository
from examples.shop.tools import ToolsManager, tools
from examples.shop.types import is_object_mapping, is_object_sequence, is_str_sequence

from src.domain import ChatMessage
from src.generic_view import GenericView, Raw
from src.infrastructure.llm_connection import ClientWrapper, QueryResult
from src.infrastructure.repository import ChatRepository
from src.io_helpers import display_neutral_msg, escape_for_rich, get_input
from src.logging import configure_logger, format_var
from src.models.shared import CompleteMessage, Model, define_system_prompt
from src.models_data import get_models


logger = configure_logger(__name__)


class Main:
    _client: ClientWrapper

    def __init__(self) -> None:
        self._config_reader = ConfigReader()
        self._messages: Final[list[CompleteMessage]] = []
        self._model = self._get_model()
        self._repository = ChatRepository()
        self._shop_repository = ShopRepository()
        self._tools_manager = ToolsManager(self._shop_repository)
        self._use_system = self._config_reader.read_use_system_config()
        self._tool_calls_regex = create_tool_calls_regex()
        self._view = GenericView()
        self._display_model_name()
        self._prompt_generator = SystemPromptGenerator()

    def execute(self) -> None:
        load_dotenv()
        mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self._client = ClientWrapper(
            mistral_api_key=mistral_api_key, openai_api_key=openai_api_key
        )
        self._messages.clear()
        system_prompt = define_system_prompt(
            self._prompt_generator.create_system_prompt(self._shop_repository.products),
            use_system=self._use_system,
        )
        self._messages.append(system_prompt)
        user_query = get_input(Raw("Pregunta lo que quieras sobre nuestra tienda"))
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
        self._repository.save_messages(response.messages)
        self._messages.clear()
        self._messages.extend(response.messages)
        last_message = self._messages[-1]

        tool_calls: list[ToolCall] | None = cast(Any, last_message.chat_msg.tool_calls)

        if not tool_calls:
            tool_calls = self._parse_tool_calls_from_content(last_message)

        if tool_calls:
            response = self._use_price_query_to_answer(tool_calls)

        self._view.print(escape_for_rich(Raw(response.content)))

        logger.info(format_var("self._messages", self._messages))

    def _get_model(self) -> Model:
        model_name = self._config_reader.read_model_config()
        models = get_models()
        default_model = models[0]
        model = None
        if model_name:
            for model in models:
                if model.model_name == model_name:
                    break
            else:
                print(f"Modelo desconocido: {model_name}")
        return model or default_model

    def _display_model_name(self) -> None:
        self._view.print(escape_for_rich(Raw("Using model " + self._model.model_name)))

    def _parse_tool_calls_from_content(
        self, last_message: CompleteMessage
    ) -> list[ToolCall]:
        tool_calls: list[ToolCall] = []
        last_message_content = last_message.chat_msg.content
        logger.info(format_var("last_message_content", last_message_content))

        # Use re.DOTALL so that '.' also matches newline characters
        result = self._tool_calls_regex.search(last_message_content, re.DOTALL)
        if result:
            found = result.group(1)
            index = result.start(1)
            msg_for_the_user = last_message_content[:index]
            self._view.print(escape_for_rich(Raw(msg_for_the_user)))
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
        display_neutral_msg(Raw("Realizando consulta de precios..."))
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
                    assert isinstance(tool_call.id, str)
                    tool_response_message = create_tool_response(
                        function_name, function_result, tool_call.id
                    )
                    self._messages.append(CompleteMessage(tool_response_message))
                case _:
                    raise WrongFunctionName(function_name)
        response = self._client.get_simple_response(
            self._model,
            self._messages,
            tools=tools,
            tool_choice="none",
        )
        self._repository.save_messages(response.messages)
        return response


def create_tool_response(
    function_name: str, function_result: str, tool_call_id: str
) -> ChatMessage:
    return ChatMessage(
        role="tool",
        name=function_name,
        content=function_result,
        tool_call_id=tool_call_id,
    )


def create_tool_calls_regex() -> re.Pattern[str]:
    # Greedily match text enclosed by [{ and }], delimiters included
    return re.compile(r"(\[\{.+\}\])")
