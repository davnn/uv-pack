"""Copy unpack scripts to create (or reuse) a virtual environment and install dependencies from the pack directory."""

import shutil
import stat
from importlib.resources import files
from pathlib import Path

__all__ = [
    "copy_unpack_scripts",
]


def copy_unpack_scripts(
    *,
    output_directory: Path,
) -> None:
    """Write unpack scripts into the pack directory."""
    scripts_dir = files("uv_pack") / "scripts"
    copy_file = lambda src, force_lf=False: _copy_file(src, output_directory, force_lf=force_lf)  # type: ignore

    output_directory.mkdir(parents=True, exist_ok=True)
    copy_file(scripts_dir / "unpack.sh", force_lf=True)
    copy_file(scripts_dir / "unpack.ps1")
    copy_file(scripts_dir / "unpack.cmd")
    copy_file(scripts_dir / "README.md")
    _make_executable(output_directory / "unpack.sh")


def _copy_file(src: Path, dst_dir: Path, *, force_lf: bool = False) -> None:
    """Copy a file from src to dst_dir, optionally normalizing line endings to LF."""
    dst = dst_dir / src.name

    if force_lf:
        # Normalize line endings to LF regardless of how Git stored it
        data = src.read_bytes()
        data = data.replace(b"\r\n", b"\n")
        dst.write_bytes(data)
    else:
        shutil.copyfile(str(src), str(dst))


def _make_executable(path: Path) -> None:
    """Best-effort make a script executable (POSIX)."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass
