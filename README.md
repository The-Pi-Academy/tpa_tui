# The Pi Academy Setup TUI

A terminal setup app for The Pi Academy coding camp machines running
Raspberry Pi OS 64-bit on Raspberry Pi 4s, with room for Raspberry Pi 5s later.

The installer downloads every public repository in the `The-Pi-Academy`
organization into `~/thepiacademy`, excluding this repository, which is stored
at `~/thepiacademy/tpa_tui`. It can also install VS Code, beginner-friendly
editors, and the standard system/Python/Java dependencies used by the projects.
The object detection demo is available as an optional install instead of a
default student-machine download.

## Quick Start

Install `curl` first if the image does not already include it:

```bash
sudo apt-get update
sudo apt-get install -y curl
```

Then launch the setup tool:

```bash
curl -fsSL https://the-pi-academy.github.io/tpa_tui/install.sh | bash
```

For local development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
tpa-tui
```

Preview the install plan without changing the machine:

```bash
tpa-setup plan
tpa-setup all --dry-run
```

If a remote terminal renders the TUI but does not pass key presses through,
use the plain line-mode menu:

```bash
tpa-setup menu
```

The bootstrap script also launches the line-mode menu automatically when it
detects Kubernetes. To force it anywhere:

```bash
curl -fsSLo /tmp/tpa-install.sh https://raw.githubusercontent.com/The-Pi-Academy/tpa_tui/main/scripts/install.sh
TPA_SETUP_MODE=menu bash /tmp/tpa-install.sh
```

## GitHub Pages

The static Pages entry point lives in `docs/`. Configure GitHub Pages for this
repository to publish from the `main` branch and the `/docs` folder.

## Notes

- The default workspace is `~/thepiacademy`.
- Default installs target Raspberry Pi OS 64-bit.
- Python dependencies are installed into a `.venv` inside each project repo.
- Heavier dependency sets are opt-in from the CLI with `--include-heavy`.
- Optional projects such as `object_detection_demo` are opt-in with
  `--include-optional`; combine both flags for the full object-detection setup.
- Hardware-specific projects still require the matching Raspberry Pi hardware
  such as GPIO wiring or Sense HAT.

## Troubleshooting an installation failure

The TUI keeps the menu open when an install worker fails, shows the failed
command/error, and does not report completion for that operation. Read the
command output immediately above the error before retrying. Earlier successful
steps are not rolled back.

To capture a plain-text log on a Raspberry Pi, run this in Bash (this retries
the installation, including package installation and repository updates):

```bash
set -o pipefail
~/thepiacademy/tpa_tui/.venv/bin/tpa-setup all 2>&1 | tee ~/thepiacademy-install.log
```

Include the failing command and preceding error output when reporting a problem,
along with `cat /etc/os-release`, `uname -m`, and `python3 --version`. Review the
log for personal information before sharing it.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use Textual's headless test runner and mocked installer operations; they
do not install system packages or require Raspberry Pi hardware.
