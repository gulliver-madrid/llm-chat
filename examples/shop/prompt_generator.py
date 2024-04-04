from examples.shop.prompts import (
    add_margin,
    system_prompt_template,
    interaction_examples,
)
from examples.shop.repository import ProductsData


class SystemPromptGenerator:
    def create_system_prompt(self, products: ProductsData) -> str:
        formatted_list = add_margin(self._format_products_for_assistant(products), 4)
        prompt = system_prompt_template.substitute(
            {"product_list": formatted_list, "examples": interaction_examples}
        )
        return prompt

    def _format_products_for_assistant(self, products: ProductsData) -> str:
        lines: list[str] = []
        for product in products:
            product_name = product["name"]
            ref = product["ref"]
            english = product_name["english"]
            spanish = product_name["spanish"]
            lines.append(f"- {ref} {english} (spanish: {spanish})")
        return "\n".join(lines)
