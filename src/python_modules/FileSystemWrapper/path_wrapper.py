from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathWrapper:
    """Wrapper to prevent call directly Path methods that trigger file R/W operations"""

    path_value: Path

    @property
    def name(self) -> str:
        return self.path_value.name

    @property
    def stem(self) -> str:
        return self.path_value.stem

    def __truediv__(self, value: str) -> "PathWrapper":
        return PathWrapper(self.path_value / value)
