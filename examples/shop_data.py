from typing import Mapping, Sequence, TypedDict


class Product(TypedDict):
    name: dict[str, str]
    price: float


ProductsData = Mapping[str, Sequence[Product]]

data: ProductsData = {
    "products": [
        {
            "name": {
                "english": "Short-sleeve T-shirt",
                "spanish": "Camiseta de manga corta",
            },
            "price": 15.99,
        },
        {
            "name": {"english": "Jeans", "spanish": "Pantalones vaqueros"},
            "price": 29.99,
        },
        {
            "name": {"english": "Casual dress", "spanish": "Vestido casual"},
            "price": 39.99,
        },
        {
            "name": {"english": "Winter jacket", "spanish": "Chaqueta de invierno"},
            "price": 79.99,
        },
        {
            "name": {"english": "Hoodie", "spanish": "Sudadera con capucha"},
            "price": 24.99,
        },
        {
            "name": {"english": "Button-up shirt", "spanish": "Camisa de botones"},
            "price": 34.99,
        },
        {"name": {"english": "Midi skirt", "spanish": "Falda midi"}, "price": 27.99},
        {"name": {"english": "Swimsuit", "spanish": "Traje de baño"}, "price": 49.99},
        {
            "name": {"english": "Knit jacket", "spanish": "Chaqueta de punto"},
            "price": 54.99,
        },
        {
            "name": {"english": "Trousers", "spanish": "Pantalón de tela"},
            "price": 32.99,
        },
        {
            "name": {"english": "Seasonal coat", "spanish": "Abrigo de temporada"},
            "price": 89.99,
        },
        {
            "name": {"english": "Sports leggings", "spanish": "Leggings deportivos"},
            "price": 19.99,
        },
        {
            "name": {"english": "Wool sweater", "spanish": "Jersey de lana"},
            "price": 45.99,
        },
        {"name": {"english": "Shorts", "spanish": "Pantalón corto"}, "price": 22.99},
        {
            "name": {"english": "Formal blazer", "spanish": "Blazer formal"},
            "price": 64.99,
        },
        {
            "name": {"english": "Basic socks", "spanish": "Calcetines básicos"},
            "price": 6.99,
        },
        {
            "name": {"english": "Pajama set", "spanish": "Conjunto de pijama"},
            "price": 29.99,
        },
        {
            "name": {"english": "Sport pants", "spanish": "Pantalón deportivo"},
            "price": 26.99,
        },
        {
            "name": {"english": "Lightweight jacket", "spanish": "Chaqueta ligera"},
            "price": 39.99,
        },
        {
            "name": {"english": "Evening dress", "spanish": "Vestido de noche"},
            "price": 69.99,
        },
    ]
}
