import json
from collections.abc import Sequence
from typing import Final

from examples.shop.repository import ShopRepository


class ToolsManager:
    def __init__(self, repository: ShopRepository):
        self.repository = repository

    def retrieve_product_prices(self, product_refs: Sequence[str]) -> str:
        return json.dumps(self._retrieve_product_prices(product_refs))

    def _retrieve_product_prices(
        self,
        product_refs: Sequence[str],
    ) -> dict[str, float | None]:
        prices: dict[str, float | None] = {}
        for ref in product_refs:
            for product in self.repository.products:
                if product["ref"] == ref:
                    prices[ref] = product["price"]
                    break
            else:
                prices[ref] = None
        assert len(prices) == len(product_refs)
        return prices


tools: Final = [
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
