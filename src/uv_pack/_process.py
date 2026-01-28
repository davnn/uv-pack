from contextlib import contextmanager
import subprocess
import sys
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass(frozen=True)
class CommandOutput:

    """Captured subprocess execution result."""

    name: str
    stdout: str
    stderr: str
    returncode: int


@contextmanager
def progress_spinner(cmd_name: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
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


def exit_on_error(result: CommandOutput, console: Console) -> None:
    """Exit the CLI if a subprocess failed."""
    if result.returncode == 0:
        return

    if result.stderr:
        if sys.stderr.isatty():
            console.print(
                Panel.fit(
                    result.stderr.rstrip(),
                    title=f"[bold red]{result.name} failed[/bold red]",
                    border_style="red",
                ),
            )
        else:
            typer.echo(result.stderr, err=True)

    raise typer.Exit(code=result.returncode)
