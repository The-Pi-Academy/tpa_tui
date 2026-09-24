#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${TPA_TUI_REPO_URL:-https://github.com/The-Pi-Academy/tpa_tui.git}"
WORKSPACE="${TPA_WORKSPACE:-$HOME/thepiacademy}"
TUI_DIR="$WORKSPACE/tpa_tui"

log() {
  printf '\033[1;33m[The Pi Academy]\033[0m %s\n' "$*"
}

need_command() {
  command -v "$1" >/dev/null 2>&1
}

if ! need_command git || ! need_command python3; then
  if need_command apt-get && need_command sudo; then
    log "Installing bootstrap tools..."
    sudo apt-get update
    sudo apt-get install -y git python3 python3-venv python3-pip ca-certificates curl
  else
    log "Please install git, python3, python3-venv, and python3-pip, then rerun this script."
    exit 1
  fi
fi

mkdir -p "$WORKSPACE"
if [ -d "$TUI_DIR/.git" ]; then
  log "Updating TUI repository..."
  git -C "$TUI_DIR" pull --ff-only
else
  log "Cloning TUI repository..."
  git clone "$REPO_URL" "$TUI_DIR"
fi

log "Preparing Python environment..."
python3 -m venv "$TUI_DIR/.venv"
"$TUI_DIR/.venv/bin/python" -m pip install --upgrade pip wheel
"$TUI_DIR/.venv/bin/python" -m pip install -e "$TUI_DIR"

log "Launching setup TUI..."
exec "$TUI_DIR/.venv/bin/tpa-tui"
