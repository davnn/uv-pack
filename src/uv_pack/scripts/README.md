# uv-pack

This package contains platform-specific unpack scripts that create (or reuse) a Python virtual
environment and install all dependencies fully offline.

The scripts are:

- `unpack.sh`   (POSIX shells)
- `unpack.ps1`  (PowerShell)

Both scripts implement the same behavior and differ only in platform syntax.

---

## Inputs / Environment Variables

- `VENV_DIR` (optional)
  Target virtual environment directory.
  Default: `<PACK_DIR>/.venv`
  Set to an empty string to install directly into `BASE_PY`.

- `PYTHON_DIR` (optional)
  Target python directory (only used if Python archive exists).
  Default: `<PACK_DIR>/.python`

- `BASE_PY` (optional)
  Explicit path to a Python interpreter to use as the venv base.
  If not set and no bundled Python is found, the scripts will search for
  a system python and ask for confirmation.

---

## Features

- **Automatic uv Setup**: Installs `uv` from a bundled wheel if not found in the environment.
- **Fast Installation**: Uses `uv` for environment creation and package installation if available.
- **Environment Reuse**: Skips virtual environment creation if `VENV_DIR` already exists.
- **Interactive Python Discovery**: Searches for system Python if no base interpreter is specified.

---

## Directory Layout

Expected layout relative to `PACK_DIR`:

- `requirements.txt` — Python requirements file
- `wheels/`          — Prebuilt wheel files
- `vendor/`          — Additional wheel or source distributions
- `python/`          — *(optional)* Directory containing a single `*.tar.gz` Python distribution
- `.python/`         — Extraction target for the bundled Python (created automatically)
- `.venv/`           — Virtual environment directory (created automatically unless `VENV_DIR` is empty)

---

## Notes

- All platforms share the same discovery and extraction semantics
- Archive extraction is guarded by interpreter discovery, not file presence
- `ensurepip` failures are ignored consistently across platforms
- No network access is required at any stage
- Uses `uv` if available for significantly faster unpacking
