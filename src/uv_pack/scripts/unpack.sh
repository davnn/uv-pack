#!/bin/sh
set -eu

PACK_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REQ_FILE=$PACK_DIR/requirements.txt
WHEELS_DIR=$PACK_DIR/wheels
VENDOR_DIR=$PACK_DIR/vendor
ARCHIVE_DIR=$PACK_DIR/python
PYTHON_DIR="${PYTHON_DIR:-$PACK_DIR/.python}"
VENV_DIR="${VENV_DIR-$PACK_DIR/.venv}"

say() { printf "%s\n" "$*" >&2; }
die() { say "ERROR: $*"; exit 1; }
first() { LC_ALL=C sort | head -n 1; }
find_python() { find -L "$1" -type f -perm -u+x \( -name python -o -name python3 \) 2>/dev/null | first || true; }

ARCHIVE="$([ -d "$ARCHIVE_DIR" ] && find "$ARCHIVE_DIR" -maxdepth 1 -type f -name '*.tar.gz' | first || true)"

if [ -z "${BASE_PY:-}" ] && { [ -d "$PYTHON_DIR" ] || [ -n "$ARCHIVE" ]; }; then
  mkdir -p "$PYTHON_DIR"
  BASE_PY="$(find_python "$PYTHON_DIR")"
  if [ -z "$BASE_PY" ] && [ -n "$ARCHIVE" ]; then
    tar -C "$PYTHON_DIR" -xzf "$ARCHIVE"
    say "Extracted python to $PYTHON_DIR"
    BASE_PY="$(find_python "$PYTHON_DIR")"
  fi
fi

[ -n "${BASE_PY:-}" ] || \
die "$(
  [ -n "$ARCHIVE" ] && \
  printf %s 'Bundled python not found after extracting archive' || \
  printf %s 'BASE_PY must be set when no python archive is provided'
)"

if [ -z "${BASE_PY:-}" ]; then
  if [ -n "$ARCHIVE" ]; then
    die "Bundled python not found after extracting archive"
  else
    die "BASE_PY must be set when no python archive is provided"
  fi
fi
[ -x "$BASE_PY" ] || die "BASE_PY not executable: $BASE_PY"

say "Using base interpreter: $BASE_PY"
VENV_PY=$BASE_PY
if [ -n "$VENV_DIR" ]; then
  "$BASE_PY" -m venv "$VENV_DIR"
  VENV_PY="$VENV_DIR/bin/python"
  [ -x "$VENV_PY" ] || VENV_PY="$VENV_DIR/bin/python3"
  [ -x "$VENV_PY" ] || die "Venv python missing"
fi

export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

"$VENV_PY" -m ensurepip --upgrade --default-pip >/dev/null 2>&1 || true
"$VENV_PY" -m pip install --find-links "$WHEELS_DIR" --find-links "$VENDOR_DIR" -r "$REQ_FILE"

say "Done."
[ -z "$VENV_DIR" ] || { say "Activate with:"; say "  . \"$VENV_DIR/bin/activate\""; }
