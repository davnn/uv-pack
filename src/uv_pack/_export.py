from pathlib import Path

from ._process import exit_on_error, run_cmd

def export_requirements(
    *,
    requirements_file: Path,
    include_dev: bool,
    other_args: str,
) -> None:
    cmd = [
        "uv",
        "export",
        "--quiet",
        "--no-hashes",
        "--no-emit-local",
        "--format=requirements.txt",
        f"--output-file={requirements_file}",
    ]

    if not include_dev:
        cmd.append("--no-dev")

    cmd.extend(other_args.split())
    exit_on_error(run_cmd(cmd, "uv export"))


def export_local_requirements(
    *,
    requirements_file: Path,
    other_args: str,
) -> None:
    cmd = [
        "uv",
        "export",
        "--quiet",
        "--no-header",
        "--no-hashes",
        "--no-annotate",
        "--no-editable",
        "--only-emit-local",
        "--format=requirements.txt",
        f"--output-file={requirements_file}",
    ]

    cmd.extend(other_args.split())
    exit_on_error(run_cmd(cmd, "uv export"))
