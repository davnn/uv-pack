from pathlib import Path

from packaging.utils import parse_wheel_filename

from uv_pack._process import exit_on_error, run_cmd


def download_third_party_wheels(
    *,
    requirements_file: Path,
    wheels_directory: Path,
    other_args: str,
    platform: str | None = None,
) -> None:
    wheels_directory.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uv",
        "run",
        "--with",
        "pip",
        "python",
        "-m",
        "pip",
        "download",
        "--prefer-binary",
        "--no-deps",
        "--disable-pip-version-check",
        "-r",
        str(requirements_file),
        "-d",
        str(wheels_directory),
    ]
    
    if platform:
        cmd.extend(["--platform", platform])

    cmd.extend(other_args.split())
    exit_on_error(run_cmd(cmd, "pip download"))


def determine_download_requirements(
    *,
    requirements_file: Path,
    wheels_directory: Path,
) -> None:
    available_wheels: list[str] = []

    for wheel in wheels_directory.glob("*.whl"):
        name, version, *_ = parse_wheel_filename(wheel.name)
        available_wheels.append(f"{name}=={version}")

    requirements_file.write_text(
        "\n".join(sorted(set(available_wheels))),
        encoding="utf-8",
    )
