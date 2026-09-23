#!/usr/bin/env bash
set -euo pipefail

export TPA_TUI_REPO_URL="${TPA_TUI_REPO_URL:-https://github.com/The-Pi-Academy/tpa_tui.git}"
curl -fsSL https://raw.githubusercontent.com/The-Pi-Academy/tpa_tui/main/scripts/install.sh | bash
