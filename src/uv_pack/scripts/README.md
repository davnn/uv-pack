# uv-pack

This package contains platform-specific unpack scripts that create (or reuse) a Python virtual
environment and install all dependencies fully offline.

The scripts are:

- `unpack.sh`   (POSIX shells)
- `unpack.ps1`  (PowerShell)
- `unpack.cmd`  (Windows CMD)

All scripts implement the same behavior and differ only in platform syntax.

---

## Inputs / Environment Variables

- `VENV_DIR` (optional)
  Target virtual environment directory.
  Default: `<PACK_DIR>/.venv`

- `PY_DEST` (optional)
  Target python directory (only used if Python archive exists).
  Default: `<PACK_DIR>/.python`

- `BASE_PY` (optional)
  Explicit path to a Python interpreter to use as the venv base.
  Required **only if** no bundled Python archive is found,
  otherwise the archive is used.

---

## Directory Layout

Expected layout relative to `PACK_DIR`:

- `requirements.txt` — Python requirements file
- `wheels/`          — Prebuilt wheel files
- `vendor/`          — Additional wheel or source distributions
- `python/`          — *(optional)* Directory containing a single `*.tar.gz` Python distribution
- `.python/`         — Extraction target for the bundled Python (created automatically)
- `.venv/`           — Virtual environment directory (created automatically)

---

## Notes

- All platforms share the same discovery and extraction semantics
- Archive extraction is guarded by interpreter discovery, not file presence
- `ensurepip` failures are ignored consistently across platforms
- No network access is required at any stage
