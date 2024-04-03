from typing import NewType


EscapedStr = NewType("EscapedStr", str)


class GenericView:
    def print(self, texto: EscapedStr) -> None:
        print(texto)
