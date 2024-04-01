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


class ShopRepository:
    _products: ProductsData | None = None

    @property
    def products(self) -> ProductsData:
        if self._products is None:
            self._products = self._get_products_data()
        return self._products

    def _get_products_data(self) -> ProductsData:
        path = Path(__file__).parent / "items.csv"
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            products = [parse_product(row) for row in reader]
        return products


def parse_product(row: dict[str, Any]) -> Product:
    return {
        "ref": ProductRef(row["ref"]),
        "name": {
            "english": row["english_name"],
            "spanish": row["spanish_name"],
        },
        "price": float(row["price"]),
    }
