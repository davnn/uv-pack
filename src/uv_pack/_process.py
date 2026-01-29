import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass

import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from uv_pack._logging import console_print


@dataclass(frozen=True)
class CommandOutput:
    """Captured subprocess execution result."""

    name: str
    stdout: str
    stderr: str
    returncode: int


@contextmanager
def run_step(cmd_name: str, *, should_run: bool = True) -> Iterator[Progress | None]:
    """Context manager to show a progress display during step execution."""
    ctx = (
        Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        if should_run
        else nullcontext()
    )

    with ctx as progress:
        if progress is not None:
            progress.add_task(f"Running '{cmd_name}'...", total=None)
        yield progress


def run_cmd(cmd: list[str], cmd_name: str) -> CommandOutput:
    """Execute a subprocess command and capture output."""
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandOutput(
        name=cmd_name,
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
    )


def exit_on_error(result: CommandOutput) -> None:
    """Exit the CLI if a subprocess failed."""
    if result.returncode == 0:
        return

    if result.stderr:
        if sys.stderr.isatty():
            console_print(
                Panel.fit(
                    result.stderr.rstrip(),
                    title=f"[bold red]✘ '{result.name}' failed[/bold red]",
                    border_style="red",
                ),
            )
        else:
            typer.echo(result.stderr, err=True)

    raise typer.Exit(code=result.returncode)
