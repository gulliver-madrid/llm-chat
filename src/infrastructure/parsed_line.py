from enum import Enum
import re
from typing import Final, Mapping


class TagType(Enum):
    """Type of a tag"""

    META = "META"
    ROLE = "ROLE"


tag_types: Final[Mapping[str, TagType]] = dict(META=TagType.META, ROLE=TagType.ROLE)


class ParsedLine:
    def __init__(self, line: str):
        self.line = line
        assert "\n" not in line
        pattern = re.compile(r"^\[(META|ROLE) .*\]$")
        self.match = pattern.match(line)

    def is_tag(self) -> bool:
        return bool(self.match)

    def get_tag_type(self) -> TagType | None:
        if not self.is_tag():
            return None
        assert self.match
        return tag_types[self.match.groups()[0]]

    def get_role(self) -> str | None:
        if self.get_tag_type() is not TagType.ROLE:
            return None
        assert self.match
        pattern = re.compile(r"^\[ROLE (.*)\]$")
        match = pattern.match(self.line)
        assert match
        found = match.groups()[0]
        first = found.split()[0]
        assert isinstance(first, str)  # malformed tag
        assert first == first.upper()
        assert (role := first.lower()) in ("system", "user", "assistant"), first
        return role
