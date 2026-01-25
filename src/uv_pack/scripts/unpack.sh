#!/bin/sh
set -eu

PACK_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

REQ_FILE="$PACK_DIR/requirements.txt"
WHEELS_DIR="$PACK_DIR/wheels"
VENDOR_DIR="$PACK_DIR/vendor"
VENV_DIR="${VENV_DIR:-"$PACK_DIR/.venv"}"
PY_DEST="${PY_DEST:-"$PACK_DIR/.python"}"
PY_SRC="$PACK_DIR/python"

say() { printf "%s\n" "$*" >&2; }
die() { say "ERROR: $*"; exit 1; }

find_python() {
  find -L "$1" \( -name python -o -name python3 \) -type f -perm -u+x 2>/dev/null |
    LC_ALL=C sort | head -n 1 || true
}

find_archive() {
  [ -d "$PY_SRC" ] || return 1
  find "$PY_SRC" -maxdepth 1 -type f -name "*.tar.gz" |
    LC_ALL=C sort | head -n 1 || true
}

ARCHIVE="$(find_archive || true)"
HAS_ARCHIVE=0
[ -n "$ARCHIVE" ] && HAS_ARCHIVE=1

if [ "$HAS_ARCHIVE" -eq 1 ]; then
  mkdir -p "$PY_DEST"
  BASE_PY="$(find_python "$PY_DEST")"

  if [ -z "$BASE_PY" ]; then
    tar -C "$PY_DEST" -xzf "$ARCHIVE"
    say "✔ Extracted python"
    BASE_PY="$(find_python "$PY_DEST")"
  fi
fi

if [ -z "${BASE_PY:-}" ]; then
  if [ "$HAS_ARCHIVE" -eq 0 ]; then
    die "BASE_PY must be set when no python archive is provided"
  fi
  die "Bundled python not found after extracting archive"
fi

[ -x "$BASE_PY" ] || die "BASE_PY not executable: $BASE_PY"

say "Using base interpreter: $BASE_PY"
"$BASE_PY" -m venv "$VENV_DIR"

VENV_PY="$VENV_DIR/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="$VENV_DIR/bin/python3"
[ -x "$VENV_PY" ] || die "Venv python missing"

export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

"$VENV_PY" -m ensurepip --upgrade --default-pip >/dev/null 2>&1 || true

"$VENV_PY" -m pip install \
  --find-links "$WHEELS_DIR" \
  --find-links "$VENDOR_DIR" \
  -r "$REQ_FILE"

say "Done."
say "Activate with:"
say "  . \"$VENV_DIR/bin/activate\""
