# Specification

1. **Determine paths**
   - `REQ_FILE = <PACK_DIR>/requirements.txt`
   - `WHEELS_DIR = <PACK_DIR>/wheels`
   - `VENDOR_DIR = <PACK_DIR>/vendor`
   - `ARCHIVE_DIR = <PACK_DIR>/python`
   - `PYTHON_DIR = <PACK_DIR>/.python`
   - `VENV_DIR = <PACK_DIR>/.venv`

If `VENV_DIR=""`, the depenencies are installed directly into `BASE_PY`.
If `BASE_PY` is set, it should be preferred over an existing `PYTHON_DIR`, which should be preferred over unpacking
a python interpreter from `ARCHIVE_DIR` to `PYTHON_DIR`.

2. **Discover bundled Python archive**
   - If `<PACK_DIR>/python` exists, search for `*.tar.gz`
   - Choose the first found archive inside the directory
   - If no archive is present, bundled Python is considered unavailable

3. **Extract bundled Python (if needed)**
   - Ensure `<PACK_DIR>/.python` exists
   - Recursively search for an existing interpreter in `.python`
   - If none is found, extract the archive into `.python`

4. **Interpreter discovery**
   - Search recursively under `.python`
   - POSIX: `python` or `python3` with executable bit set (alphabetically first)
   - Windows: `python.exe` (match with the shortest path is selected)

5. **Interpreter validation**
   - POSIX: interpreter must exist and be executable
   - Windows: interpreter must exist
   - If no interpreter is available after extraction:
     - Fail with a clear error

6. **Create virtual environment**
   - If `VENV_DIR` is non-empty, run: `<BASE_PY> -m venv <VENV_DIR>`
   - If `VENV_DIR` is empty, use `BASE_PY` directly for installation

7. **Determine venv interpreter**
   - If `VENV_DIR` is non-empty:
     - POSIX: `<VENV_DIR>/bin/python` or `python3`
     - Windows: `<VENV_DIR>\Scripts\python.exe`
     - Fail if not found
   - If `VENV_DIR` is empty:
     - Use `BASE_PY`

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
   - Print activation instructions appropriate for the platform when a venv was created
