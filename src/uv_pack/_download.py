import os
import platform
import re
from pathlib import Path
import sys
from typing import Literal
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from urllib3.util.retry import Retry

from uv_pack._logging import ConsoleError, Verbosity, console_print

__all__ = [
    "download_latest_python_build",
]

LATEST_RELEASE_API = (
    "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
)

def download_latest_python_build(
    *,
    dest_dir: Path,
    target_format: Literal["install_only", "install_only_stripped"] = "install_only_stripped",
) -> Path:
    """Resolve and download the latest python-build-standalone artifact.

    Returns the downloaded file path.
    """
    session = session_with_retries()
    url = find_latest_python_build(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        target_arch=resolve_platform(),
        target_format=target_format,
        session=session,
    )
    console_print(f"[dim]Resolved asset:[/dim] {url}", level=Verbosity.verbose)
    return download_with_progress(
        url=url,
        dest_dir=dest_dir,
        session=session,
    )


def find_latest_python_build(
    python_version: str,
    target_arch: str,
    *,
    target_format: Literal["install_only", "install_only_stripped"] = "install_only_stripped",
    session: requests.Session | None = None,
) -> str:
    session = session or requests.Session()
    release_api = os.getenv("UV_PYTHON_INSTALL_MIRROR", LATEST_RELEASE_API)

    resp = session.get(release_api, timeout=10)
    resp.raise_for_status()
    release = resp.json()

    py_pattern = re.compile(
        rf"^cpython-{re.escape(python_version)}(\.\d+)?",
        re.IGNORECASE,
    )

    for asset in release.get("assets", []):
        name = asset["name"]
        if (
            py_pattern.search(name)
            and target_arch in name
            and name.endswith(f"{target_format}.tar.gz")
        ):
            return asset["browser_download_url"]

    msg = f"No asset found for Python {python_version} on {target_arch}"
    raise RuntimeError(msg)

def download_with_progress(
    url: str,
    dest_dir: Path,
    *,
    filename: str | None = None,
    console: Console | None = None,
    session: requests.Session | None = None,
) -> Path:
    """Download a file with retries and a Rich progress bar.

    Returns the final file path.
    """
    session = session or requests.Session()
    console = console or Console()
    dest_dir.mkdir(parents=True, exist_ok=True)

    with session.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))
        # try to get the filename from headers, otherwise fall back to the file name in the URL
        filename = resp.headers.get("Content-Disposition", unquote(url.rsplit("/", 1)[-1])).split("filename=")[1]
        final_path = dest_dir / filename
        temp_path = final_path.with_suffix(final_path.suffix + ".part")

        progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        )

        with progress:
            task = progress.add_task(
                "Running 'python'...",
                total=total if total > 0 else None,
            )

            with temp_path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

    temp_path.replace(final_path)
    return final_path


def session_with_retries() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "venv-pack-download",
        "Accept": "application/vnd.github+json",
    })

    # authenticate to GitHub API to prevent rate-limiting
    if token := os.getenv("GITHUB_TOKEN"):
        session.headers["Authorization"] = f"Bearer {token}"

    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.5,
        status_forcelist=(502, 503, 504),
        allowed_methods=("GET",),
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session


def resolve_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture
    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }
    arch = arch_map.get(machine, machine)

    if system == "windows":
        return f"{arch}-pc-windows-msvc"

    if system == "linux":
        return f"{arch}-unknown-linux-gnu"

    if system == "darwin":
        return f"{arch}-apple-darwin"

    msg = f"[bold red]✘ Found unsupported platform:[/bold red] {system}"
    raise ConsoleError(msg)
