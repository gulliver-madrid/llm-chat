import re
from typing import Any

STYLE_TAGS_REGEX = r"""^[A-Z_]+ = StyleTag\("\[[a-z_]+\]"\)$"""


def is_enum_or_similar(line: str) -> bool:
    # Regex that checks if the line starts with 4 spaces and the constant name is identical
    # to the assigned value
    regex = r'^ {4}([A-Z_]+) = "\1"$'
    # Check if there is a match
    return bool(re.match(regex, line))


def pre_mutation(context: Any) -> None:
    lines: list[str] = []
    lines.append("\n" * 2 + context.filename)
    lines.append(context.current_source_line)
    lines.append(f"index: {context.index}")
    # lines.append(f"mutation_id: {context.mutation_id}")
    print("\n".join(lines))
    if "python_modules" in context.filename:
        print("skipped:", context.filename)
        context.skip = True
        return
    if re.match(STYLE_TAGS_REGEX, context.current_source_line.strip()):
        context.skip = True
    elif is_enum_or_similar(context.current_source_line):
        context.skip = True
    elif context.current_source_line.strip().startswith("assert "):
        context.skip = True
    else:
        print("not skipped")
    if context.skip:
        print("skipped line")
