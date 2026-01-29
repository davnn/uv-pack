from pathlib import Path

from uv_pack._process import exit_on_error, run_cmd


def export_requirements(
    *,
    requirements_file: Path,
    other_args: str,
) -> None:
    cmd = [
        "uv",
        "export",
        "--quiet",
        "--no-dev",
        "--no-header",
        "--no-hashes",
        "--no-emit-local",
        "--format=requirements.txt",
        f"--output-file={requirements_file}",
    ]

    cmd.extend(other_args.split())
    exit_on_error(run_cmd(cmd, "uv export"))


def export_local_requirements(
    *,
    requirements_file: Path,
    other_args: str,
) -> None:
    """Export only local packages to a plain requirements.txt file (each line is a local requirement path)."""
    cmd = [
        "uv",
        "export",
        "--quiet",
        "--no-dev",
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
