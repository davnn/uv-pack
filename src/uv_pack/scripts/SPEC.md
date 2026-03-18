# Specification

1. **Determine paths**
   - `REQ_FILE = <PACK_DIR>/requirements.txt`
   - `WHEELS_DIR = <PACK_DIR>/wheels`
   - `VENDOR_DIR = <PACK_DIR>/vendor`
   - `ARCHIVE_DIR = <PACK_DIR>/python`
   - `PYTHON_DIR = <PACK_DIR>/.python`
   - `VENV_DIR = <PACK_DIR>/.venv`
   - `UV_WHEEL = <PACK_DIR>/wheels/uv-*.whl`

If `VENV_DIR=""`, the dependencies are installed directly into `BASE_PY`.
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

5. **Interactive System Python Discovery**
   - If `BASE_PY` is still not set after checking bundled options:
     - Search for system commands: `python3`, `python`, `python2` (POSIX) or `python`, `python3` (Windows)
     - For each found command, prompt the user: "Do you want to use this python for installation? [y/N]"
     - If confirmed, set `BASE_PY` to that command's path

6. **Interpreter validation**
   - POSIX: interpreter must exist and be executable
   - Windows: interpreter must exist
   - Fail with a clear error if no interpreter is available after all discovery steps

7. **Automatic uv Setup**
   - Check if `uv` command is available in the environment
   - If `uv` is missing, look for a `uv-*.whl` in `<PACK_DIR>`
   - If found, install it into the base interpreter: `<BASE_PY> -m pip install <UV_WHEEL>`
   - Re-check `uv` availability for subsequent steps

8. **Create virtual environment**
   - If `VENV_DIR` is non-empty:
     - **Check Existence**: If `<VENV_DIR>` already exists, skip creation
     - **Uv Mode**: If `uv` is available, run: `uv venv <VENV_DIR> --python <BASE_PY>`
     - **Legacy Mode**: Otherwise, run: `<BASE_PY> -m venv <VENV_DIR>`
   - If `VENV_DIR` is empty, use `BASE_PY` directly for installation

9. **Determine venv interpreter**
   - If `VENV_DIR` is non-empty:
     - POSIX: `<VENV_DIR>/bin/python` or `python3`
     - Windows: `<VENV_DIR>\Scripts\python.exe`
     - Fail if not found
   - If `VENV_DIR` is empty:
     - Use `BASE_PY`

10. **Offline installation**
    - **Uv Mode** (if `uv` available):
      - Run: `uv pip install --python <VENV_PY> --no-index --find-links <WHEELS_DIR> --find-links <VENDOR_DIR> -r <REQ_FILE>`
    - **Legacy Mode**:
      - Set: `PIP_NO_INDEX=1`, `PIP_DISABLE_PIP_VERSION_CHECK=1`
      - Run `ensurepip` (best-effort, never fatal)
      - Run: `<VENV_PY> -m pip install --find-links <WHEELS_DIR> --find-links <VENDOR_DIR> -r <REQ_FILE>`

11. **Completion**
    - Print activation instructions appropriate for the platform when a venv was created
