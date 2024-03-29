import json
import os
from typing import Any, Mapping

from rich import print
from dotenv import load_dotenv

from examples.shop_data import ProductsData, data
from src.infrastructure.client_wrapper import ClientWrapper
from src.io_helpers import display_neutral_msg, get_input
from src.logging import configure_logger
from src.models.shared import ChatMessage, CompleteMessage, Model, ModelName, Platform

logger = configure_logger(__name__, __file__)


models: Mapping[str, ModelName] = dict(
    medium=ModelName("mistral-medium"), large=ModelName("mistral-large-2402")
)


def _retrieve_prices_by_name(names_in_english: list[str]) -> dict[str, float | None]:
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


def retrieve_prices_by_name(names_in_english: list[str]) -> str:
    return json.dumps(_retrieve_prices_by_name(names_in_english))


tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_prices_by_name",
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
    return f"""Eres un asistente virtual en una tienda de ropa. Tu misión es proporcionar información precisa y actualizada sobre los productos disponibles, sus precios y cualquier otra cosa que los clientes puedan preguntar. Tu tono debe ser amigable y profesional. Tu objetivo es proporcionar una experiencia positiva al cliente y ayudarlo a encontrar lo que está buscando. Los productos disponibles son estos:
{format_products_for_assistant(data)}

Solo debes proporcionar los precios que puedas obtener con seguridad por medio de nuestro sistema. Si no conoces el precio de un producto, simplemente di que ahora mismo no puedes proporcionar ese precio debido a una incidencia técnica. Si son varios los productos cuyo precio desconoces, no debes dar la explicación para cada producto, sino una única vez para todos ellos.

Responde en el idioma que use el cliente.

Recuerda que tienes disponible una función para obtener los precios de varios productos.
"""


def main() -> None:
    load_dotenv()
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    client = ClientWrapper(mistral_api_key=mistral_api_key)
    messages = client.define_system_prompt(create_system_prompt())
    user_query = get_input("Pregunta lo que quieras sobre nuestra tienda")
    response = client.get_simple_response(
        Model(Platform.Mistral, models["large"]),
        user_query,
        messages,
        tools=tools,
        tool_choice="auto",
    )
    messages = response.messages
    last_message = messages[-1]
    if calls := last_message.chat_msg.tool_calls:

        display_neutral_msg("Realizando consulta de precios...")

        assert isinstance(calls, list)
        tool_call: Any = calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments)
        assert function_name == "retrieve_prices_by_name"
        assert len(function_params) == 1
        assert "names_in_english" in function_params
        names_in_english = function_params.get("names_in_english")
        function_result = retrieve_prices_by_name(names_in_english)
        chat_message = ChatMessage(
            role="tool", name=function_name, content=function_result
        )
        messages.append(CompleteMessage(chat_message))
        response = client.get_simple_response(
            Model(Platform.Mistral, models["large"]),
            "",
            messages,
            tools=tools,
            tool_choice="none",
            append_query=False,  # because the query was send before
        )
    print(response.content)

    logger.info(response.messages)


if __name__ == "__main__":
    main()
