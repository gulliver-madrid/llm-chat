import re


def find_placeholders(s: str) -> list[str]:
    return re.findall(r"(?<![a-zA-Z0-9])\$0[a-zA-Z_][a-zA-Z]*[0-9]*", s)
