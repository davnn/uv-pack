uv-pack
=======

[![Check Status](https://github.com/davnn/uv-pack/actions/workflows/check.yml/badge.svg)](https://github.com/davnn/uv-pack/actions?query=workflow%3Acheck)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/davnn/uv-pack/releases)

Bundle a locked `uv` environment into a self-contained, offline-installable directory.
The output includes pinned requirements, third-party wheels, locally built wheels,
and a portable Python interpreter.

What it does
------------
- Exports a `requirements.txt` from your `uv` lock file.
- Downloads third-party wheels into `pack/wheels/`.
- Builds local workspace packages into `pack/vendor/`.
- Downloads a python-build-standalone archive into `pack/python/` (unless `--system`).
- Writes `unpack.sh`, `unpack.ps1`, and `unpack.cmd` to unpack the resulting venv offline.

Install
-------

Install `uv-pack` as a dev-dependency or as a uv tool.

```bash
uv add --dev uv-pack
# or install as a tool
uv tool install uv-pack
```

Once installed, run using:

```bash
uv run uv-pack --help
# or as a tool
uv tool run uv-pack --help
# or using uvx (equivalent)
uvx uv-pack --help
```

CLI
---

```bash
uv-pack [OUTPUT_DIRECTORY (default = ./pack)]
```

Options:
- `--uv-export`: extra args passed to `uv export`
- `--pip-download`: extra args passed to `pip download`
- `--uv-build-sdist`: extra args passed to `uv build` for downloaded sdists
- `--uv-build-pkg`: extra args passed to `uv build` for local packages
- `--no-clean`: keep the output directory instead of wiping
- `--include-dev`: include dev dependencies
- `--system`: skip bundling Python; require `BASE_PY` at unpack time

Example
-------
```bash
uv-pack --include-dev
```

Output layout
-------------
```
pack/
  requirements.txt
  wheels/
  vendor/
  python/   # (omitted with --system)
  unpack.sh
  unpack.ps1
  unpack.cmd
  README.md
```

Unpack and install offline
--------------------------

POSIX (sh/bash/zsh):

```bash
./pack/unpack.sh
```

PowerShell:

```powershell
.\pack\unpack.ps1 -VenvDir <path>
```

Windows cmd:

```cmd
pack\unpack.cmd
```

All scripts also accept `VENV_DIR`, `PY_DEST` and `BASE_PY` environment variables.
Use `BASE_PY` when `--system` was used during packing to provide a system
python interpreter. `VENV_DIR` (default = `.venv`) and `PY_DEST` (default = `.python`)
can be used to customize the target python and venv diretory.

Configuration
-------------

`UV_PYTHON_INSTALL_MIRROR` can override the GitHub API endpoint to retrieve the
Python releases, default is:
<https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest>.

`GITHUB_TOKEN` can be used to authenticate the request to the GitHub API to
prevent possible rate-limiting.
