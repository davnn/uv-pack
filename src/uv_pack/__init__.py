"""uv-pack: Bundle a locked uv environment into an offline-installable bundle.

Pipeline:
1. Clean the output directory
2. Export locked requirements via uv
3. Download third-party wheels into ./wheels
4. Build local workspace packages into ./vendor
5. Download a python interpreter to ./python

Result:
pack/
├── requirements.txt
├── wheels/              # third-party wheels
│   └── requirements.txt # index packages
├── vendor/              # locally built wheels
│   └── requirements.txt # local packages
├── python/              # python interpreter
├── unpack.sh
├── unpack.ps1
├── unpack.bat
├── .gitignore
└── README.md
"""

import shutil
from collections.abc import Iterable
from enum import Enum
from pathlib import Path

import typer

from uv_pack._build import build_requirements, build_src_wheel
from uv_pack._download import download_third_party_wheels
from uv_pack._export import export_local_requirements, export_requirements
from uv_pack._files import PackLayout
from uv_pack._logging import ConsoleError, Verbosity, console_print, set_verbosity
from uv_pack._process import run_step
from uv_pack._python import download_latest_python_build
from uv_pack._scripts import copy_unpack_scripts

# -----------------------------------------------------------------------------
# CLI setup
# -----------------------------------------------------------------------------

app: typer.Typer = typer.Typer(add_completion=True)


def main() -> None:
    """Main entry point for uv-pack CLI."""
    try:
        app()
    except ConsoleError:
        raise  # already formatted for user
    except KeyboardInterrupt as err:
        console_print("[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(130) from err
    except Exception as err:
        msg = (
            "[bold red]✘ An unexpected internal error occurred, please try again or"
            " open an issue https://github.com/davnn/uv-pack/issues.[/bold red]"
        )
        raise ConsoleError(msg) from err


# -----------------------------------------------------------------------------
# Step model
# -----------------------------------------------------------------------------


class Step(str, Enum):
    """Steps to be performed in the pack pipeline."""

    clean = "clean"
    export = "export"
    download = "download"
    build = "build"
    python = "python"


PIPELINE_ORDER: tuple[Step, ...] = (
    Step.clean,
    Step.export,
    Step.download,
    Step.build,
    Step.python,
)


# -----------------------------------------------------------------------------
# Helper operations
# -----------------------------------------------------------------------------


def _additional_cli_args(cmd_name: str) -> str:
    return f"Additional command line arguments to be provided to '{cmd_name}'"


def _normalize_steps(
    steps: Iterable[Step] | None,
    skip: Iterable[Step] | None,
) -> list[Step]:
    selected = set(PIPELINE_ORDER) if steps is None else set(steps)
    selected = selected.difference([] if skip is None else set(skip))
    return [step for step in PIPELINE_ORDER if step in selected]


def _raise_requirement_txt_missing(path: Path) -> None:
    if not path.exists():
        msg = f"[bold red]✘ No requirements file found:[/bold red] '{path}', did you skip the 'export' step?"
        raise ConsoleError(msg)


# -----------------------------------------------------------------------------
# Orchestration command
# -----------------------------------------------------------------------------


@app.command()
def pack(
    *,
    steps: list[Step] | None = typer.Argument(
        PIPELINE_ORDER,
        help="Pipeline steps to run (multiple can be whitespace-separated)",
    ),
    skip: list[Step] | None = typer.Option(
        None,
        "--skip",
        "-s",
        help="Pipeline steps to skip (can be supplied multiple times)",
    ),
    output_directory: Path = typer.Option(
        Path("./pack"),
        "--output-directory",
        "-o",
        help="Path to output directory",
    ),
    uv_export: str = typer.Option(
        default="",
        help=_additional_cli_args("uv export"),
    ),
    pip_download: str = typer.Option(
        default="",
        help=_additional_cli_args("pip download"),
    ),
    uv_build: str = typer.Option(
        default="",
        help=_additional_cli_args("uv build"),
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """Pack a locked uv environment into an offline-installable bundle."""
    set_verbosity(Verbosity.verbose if verbose else Verbosity.normal)
    selected_steps = _normalize_steps(steps, skip)
    console_print(
        f"[dim]Running steps:[/dim] {[step.value for step in selected_steps]}",
    )

    if Step.clean in selected_steps:
        with run_step("clean"):
            shutil.rmtree(output_directory, ignore_errors=True)

        console_print(
            f"[green]✔ Cleaned[/green] output directory '{output_directory}'",
            level=Verbosity.verbose,
        )

    # initialize pack directory structure and copy unpack scripts
    pack = PackLayout.create(output_directory=output_directory)
    copy_unpack_scripts(output_directory=output_directory)

    if Step.export in selected_steps:
        with run_step("export"):
            export_requirements(
                requirements_file=pack.requirements_export_txt,
                other_args=uv_export,
            )
            export_local_requirements(
                requirements_file=pack.requirements_local_txt,
                other_args=uv_export,
            )
        console_print(
            f"[green]✔ Exported[/green] requirements '{pack.requirements_export_txt}'",
            level=Verbosity.verbose,
        )
        console_print(
            f"[green]✔ Exported[/green] requirements '{pack.requirements_local_txt}'",
            level=Verbosity.verbose,
        )

    if Step.download in selected_steps:
        _raise_requirement_txt_missing(pack.requirements_export_txt)

        with run_step("download"):
            download_third_party_wheels(
                requirements_file=pack.requirements_export_txt,
                wheels_directory=pack.wheels_dir,
                other_args=pip_download,
            )

    if Step.build in selected_steps:
        _raise_requirement_txt_missing(pack.requirements_local_txt)
        _raise_requirement_txt_missing(pack.requirements_export_txt)

        # show the progress for each package in verbose mode, otherwise a single progress report is shown
        with run_step("build", should_run=not verbose):
            for line in pack.requirements_local_txt.read_text(
                encoding="utf-8",
            ).splitlines():
                with run_step("build", should_run=verbose):
                    build_src_wheel(
                        source_path=Path(line),
                        out_path=pack.vendor_dir,
                        other_args=uv_build,
                    )
                console_print(
                    f"[green]✔ Built[/green] wheel: '{line}'",
                    level=Verbosity.verbose,
                )

            for sdist in pack.wheels_dir.glob("*.tar.gz"):
                with run_step("build", should_run=verbose):
                    build_src_wheel(
                        source_path=sdist,
                        out_path=pack.wheels_dir,
                        other_args=uv_build,
                    )
                    sdist.unlink(missing_ok=True)
                console_print(
                    f"[green]✔ Built[/green] wheel: '{sdist}'",
                    level=Verbosity.verbose,
                )

            build_requirements(
                requirements_txt=pack.requirements_txt,
                requirements_export_txt=pack.requirements_export_txt,
                vendor_directory=pack.vendor_dir,
            )
            console_print(
                f"[green]✔ Built[/green] requirements: '{pack.requirements_txt}'",
                level=Verbosity.verbose,
            )

    if Step.python in selected_steps:
        pack.python_dir.mkdir(exist_ok=True)
        python_path = download_latest_python_build(
            dest_dir=pack.python_dir,
        )
        console_print(
            f"[green]✔ Downloaded[/green] '{python_path}'",
            level=Verbosity.verbose,
        )

    console_print("[green]✔ Done[/green]")
