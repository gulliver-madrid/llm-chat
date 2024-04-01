from typing import Sequence, TypedDict
import csv
from pathlib import Path


class Product(TypedDict):
    name: dict[str, str]
    price: float
    ref: str


ProductsData = Sequence[Product]


def get_products_data() -> ProductsData:
    path = Path(__file__).parent / "items.csv"
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        items: list[Product] = []
        for row in reader:
            # Convertir cada fila del CSV en un diccionario
            item: Product = {
                "ref": row["ref"],
                "name": {
                    "english": row["english_name"],
                    "spanish": row["spanish_name"],
                },
                "price": float(row["price"]),
            }
            items.append(item)
    return items
