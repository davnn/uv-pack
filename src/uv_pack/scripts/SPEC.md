# Specification

1. **Determine paths**
   - `REQ_FILE = <PACK_DIR>/requirements.txt`
   - `WHEELS_DIR = <PACK_DIR>/wheels`
   - `VENDOR_DIR = <PACK_DIR>/vendor`
   - `PY_SRC = <PACK_DIR>/python`
   - `PY_DEST = <PACK_DIR>/.python`
   - `VENV_DIR` defaults to `<PACK_DIR>/.venv` if not set

2. **Discover bundled Python archive**
   - If `<PACK_DIR>/python` exists, search for `*.tar.gz`
   - Exactly one archive is expected
   - If no archive is present, bundled Python is considered unavailable

3. **Extract bundled Python (if needed)**
   - Ensure `<PACK_DIR>/.python` exists
   - Recursively search for an existing interpreter in `.python`
   - If none is found, extract the archive into `.python`

4. **Interpreter discovery**
   - Search recursively under `.python`
   - POSIX: `python` or `python3` with executable bit set
   - Windows: `python.exe`
   - The lexicographically first match is selected
   - If found, this interpreter overrides `BASE_PY`

5. **Interpreter validation**
   - If no interpreter is available after extraction:
     - Fail with a clear error
   - POSIX: interpreter must exist and be executable
   - Windows: interpreter must exist

6. **Create virtual environment**
   - Run: `<BASE_PY> -m venv <VENV_DIR>`

7. **Determine venv interpreter**
   - POSIX: `<VENV_DIR>/bin/python` or `python3`
   - Windows: `<VENV_DIR>\Scripts\python.exe`
   - Fail if not found

8. **Offline installation**
   - Set:
     - `PIP_NO_INDEX=1`
     - `PIP_DISABLE_PIP_VERSION_CHECK=1`
   - Run `ensurepip` (best-effort, never fatal)
   - Install dependencies using:
     - `wheels/`
     - `vendor/`
     - `requirements.txt`

9. **Completion**
   - Print activation instructions appropriate for the platform
