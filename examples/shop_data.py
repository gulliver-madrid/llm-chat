from collections.abc import Sequence
import csv
from pathlib import Path
from typing import Any, NewType, TypedDict

ProductRef = NewType("ProductRef", str)


class Name(TypedDict):
    english: str
    spanish: str


class Product(TypedDict):
    name: Name
    price: float
    ref: ProductRef


ProductsData = Sequence[Product]


def get_products_data() -> ProductsData:
    path = Path(__file__).parent / "items.csv"
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [parse_product(row) for row in reader]


def parse_product(row: dict[str, Any]) -> Product:
    return {
        "ref": ProductRef(row["ref"]),
        "name": {
            "english": row["english_name"],
            "spanish": row["spanish_name"],
        },
        "price": float(row["price"]),
    }
