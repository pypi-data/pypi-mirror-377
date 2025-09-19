from .._exceptions import A4FError

INSTRUCTIONS = """

A4F error:

    missing `{library}`

This feature requires additional dependencies:

    $ pip install a4f[{extra}]

"""


def format_instructions(*, library: str, extra: str) -> str:
    return INSTRUCTIONS.format(library=library, extra=extra)


class MissingDependencyError(A4FError):
    pass
