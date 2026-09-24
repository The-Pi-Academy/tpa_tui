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
