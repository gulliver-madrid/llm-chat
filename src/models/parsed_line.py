from dataclasses import dataclass
from enum import Enum
import re
from typing import Final, Mapping

from src.models.shared import ModelName


class TagType(Enum):
    """Type of a tag"""

    META = "META"
    ROLE = "ROLE"


@dataclass(frozen=True)
class RoleInfo:
    role: str
    model_name: ModelName | None = None


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

    def get_role_info(self) -> RoleInfo | None:
        if self.get_tag_type() is not TagType.ROLE:
            return None
        assert self.match
        pattern = re.compile(r"^\[ROLE ([A-Z]+)(.*)\]$")
        match = pattern.match(self.line)
        assert match
        first = match.groups()[0]
        assert isinstance(first, str)  # malformed tag
        assert first == first.upper()
        assert (role := first.lower()) in ("system", "user", "assistant"), first
        second = match.groups()[1].strip()
        if not second:
            return RoleInfo(role)
        model_match = re.match(r"model=([.-_a-z0-9]+)", second)
        assert model_match, second
        model_name = ModelName(model_match.groups()[0])
        return RoleInfo(role, model_name)
