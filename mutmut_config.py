import re
from typing import Any

STYLE_TAGS_REGEX = r"""^[A-Z_]+ = StyleTag\("\[[a-z_]+\]"\)$"""


def pre_mutation(context: Any):

    print(context.filename)
    if "python_modules" in context.filename:
        print("skipped:", context.filename)
        context.skip = True
        return
    if re.match(STYLE_TAGS_REGEX, context.current_source_line.strip()):
        print(f"skipped line: {context.line}")
        context.skip = True
    else:
        print("not skipped")
