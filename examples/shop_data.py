from typing import Mapping, Sequence


ProductsData = Mapping[str, Sequence[Mapping[str, str | float]]]

data: ProductsData = {
    "products": [
        {"name": "Short-sleeve T-shirt", "price": 15.99},
        {"name": "Jeans", "price": 29.99},
        {"name": "Casual dress", "price": 39.99},
        {"name": "Winter jacket", "price": 79.99},
        {"name": "Hoodie", "price": 24.99},
        {"name": "Button-up shirt", "price": 34.99},
        {"name": "Midi skirt", "price": 27.99},
        {"name": "Swimsuit", "price": 49.99},
        {"name": "Knit jacket", "price": 54.99},
        {"name": "Trousers", "price": 32.99},
        {"name": "Seasonal coat", "price": 89.99},
        {"name": "Sports leggings", "price": 19.99},
        {"name": "Wool sweater", "price": 45.99},
        {"name": "Shorts", "price": 22.99},
        {"name": "Formal blazer", "price": 64.99},
        {"name": "Basic socks", "price": 6.99},
        {"name": "Pajama set", "price": 29.99},
        {"name": "Sport pants", "price": 26.99},
        {"name": "Lightweight jacket", "price": 39.99},
        {"name": "Evening dress", "price": 69.99},
    ]
}
