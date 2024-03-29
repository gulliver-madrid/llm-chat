import os

from dotenv import load_dotenv

from src.infrastructure.client_wrapper import ClientWrapper
from src.io_helpers import get_input
from src.logging import configure_logger
from src.models.shared import Model, ModelName, Platform

logger = configure_logger(__name__, __file__)


def create_system_prompt() -> str:
    return "Eres un asistente virtual en una tienda de ropa. Tu función es proporcionar información precisa y actualizada sobre los productos disponibles, sus precios y cualquier otra cosa que los clientes puedan preguntar. Tu tono debe ser amigable y profesional. Tu objetivo es proporcionar una experiencia positiva al cliente y ayudarlo a encontrar lo que está buscando."


def main() -> None:
    load_dotenv()
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    client = ClientWrapper(mistral_api_key=mistral_api_key)
    messages = client.define_system_prompt(create_system_prompt())
    user_query = get_input("Pregunta lo que quieras sobre nuestra tienda")
    response = client.get_simple_response(
        Model(Platform.Mistral, ModelName("mistral-large-2402")), user_query, messages
    )
    print(response.content)

    logger.info(response.messages)


if __name__ == "__main__":
    main()
