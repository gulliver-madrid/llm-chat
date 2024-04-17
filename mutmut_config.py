import re
from collections.abc import Sequence
from typing import Any

STYLE_TAGS_REGEX = r"""^[A-Z_]+ = StyleTag\("\[[a-z_]+\]"\)$"""

extra_debug = False


def get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def find_log_function_intervals(lines: Sequence[str]) -> list[range]:
    # use 0-based indices
    ranges: list[range] = []
    in_function = False
    start_line = 0
    indent_level = 0

    for current_index, line in enumerate(lines):
        stripped_line = line.strip()

        if in_function:
            if not stripped_line:
                # ignore blank lines
                continue
            if stripped_line.startswith(")") and stripped_line.endswith(":"):
                # the end of the function signature might not be indented
                continue

            # If the current line has an indentation level less than or equal to that of the definition,
            # it means we have exited the function definition
            if get_indent(line) <= indent_level:
                ranges.append(range(start_line, current_index))
                in_function = False

        if not in_function and stripped_line.startswith("def log_"):
            in_function = True
            start_line = current_index
            indent_level = get_indent(line)

    # If we finished reading all lines and were still in a function definition,
    # close the interval
    if in_function:
        ranges.append(range(start_line, len(lines)))

    return ranges


def is_inside_log_function(context: Any) -> bool:
    # Avoid lines that belong to logging functions
    ranges = find_log_function_intervals(context.source.splitlines())

    for range in ranges:
        assert isinstance(context.current_line_index, int)
        if context.current_line_index >= range.stop:
            continue
        # first possible stop, the others are discarded because there is no overlapping
        return context.current_line_index >= range.start

    return False


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

    if extra_debug:
        print("\n".join(lines))
    if "python_modules" in context.filename:
        if extra_debug:
            print("file skipped")
        context.skip = True
        return
    if re.search(r"\blogger\b", context.current_source_line):
        context.skip = True
    elif re.match(STYLE_TAGS_REGEX, context.current_source_line.strip()):
        context.skip = True
    elif is_enum_or_similar(context.current_source_line):
        context.skip = True
    elif context.current_source_line.strip().startswith("assert "):
        context.skip = True
    elif is_inside_log_function(context):
        context.skip = True

    if extra_debug:
        if context.skip:
            print("skipped line")
        else:
            print("not skipped")
