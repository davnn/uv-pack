"""Copy unpack scripts to create (or reuse) a virtual environment and install dependencies from the pack directory."""

import shutil
import stat
from importlib.resources import files
from pathlib import Path


def copy_unpack_scripts(
    *,
    output_directory: Path,
) -> None:
    """Write unpack scripts into the pack directory."""
    scripts_dir = files("uv_pack") / "scripts"
    copy_file = lambda src: shutil.copyfile(str(src), str(output_directory / src.name)) # noqa: E731 # type: ignore

    output_directory.mkdir(parents=True, exist_ok=True)
    copy_file(scripts_dir / "unpack.sh")
    copy_file(scripts_dir / "unpack.ps1")
    copy_file(scripts_dir / "unpack.cmd")
    copy_file(scripts_dir / "README.md")
    _make_executable(output_directory / "unpack.sh")


def _make_executable(path: Path) -> None:
    """Best-effort make a script executable (POSIX)."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass
