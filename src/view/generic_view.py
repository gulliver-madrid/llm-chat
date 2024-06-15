from dataclasses import dataclass
from typing import NewType


# EscapedStr: text correctly escaped to prevent the disappearance of brackets, and without style
# Should only be generated using escape_for_rich()
EscapedStr = NewType("EscapedStr", str)

# StyledStr: text that has had style added (therefore will have style brackets and may have escaped brackets)
StyledStr = NewType("StyledStr", EscapedStr)


@dataclass(frozen=True)
class Raw:
    """
    Text without style and not escaped (it can have brackets, but not for styling).
    """

    value: str
