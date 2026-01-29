from enum import Enum
from typing import Any

from rich.console import Console
from typer import Exit

__all__ = [
    "ConsoleError",
    "Verbosity",
    "console_print",
    "set_verbosity",
]

console = Console(legacy_windows=False)


class Verbosity(Enum):
    quiet = 0
    normal = 1
    verbose = 2


_internal_verbosity = Verbosity.normal


def set_verbosity(mode: Verbosity) -> None:
    """Globally set the verbosity level for console printing."""
    global _internal_verbosity  # noqa: PLW0603
    _internal_verbosity = mode


def console_print(
    *objects: Any,
    level: Verbosity = Verbosity.normal,
    **kwargs: Any,
) -> None:
    """Print to console if the current verbosity level is sufficient."""
    if _internal_verbosity.value >= level.value:
        console.print(*objects, **kwargs)


class ConsoleError(Exit):
    def __init__(self, *objects: Any, **kwargs: Any) -> None:
        """Raise a user-friendly console error and print the message to the console."""
        console.print(*objects, **kwargs)
        super().__init__(code=1)
