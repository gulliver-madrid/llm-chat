from dataclasses import dataclass
from typing import NewType

import rich

# EscapedStr: text correctly escaped to prevent the disappearance of brackets, and without style
# Should only be generated using escape_for_rich()
EscapedStr = NewType("EscapedStr", str)

# StyledStr: text that has had style added (therefore will have style brackets and may have escaped brackets)
StyledStr = NewType("StyledStr", EscapedStr)


class GenericView:
    def print(self, texto: EscapedStr) -> None:
        rich.print(texto)


@dataclass(frozen=True)
class Raw:
    """
    Text without style and not escaped (it can have brackets, but not for styling).
    """

    value: str
