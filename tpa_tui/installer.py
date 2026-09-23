from __future__ import annotations

import argparse
import shutil
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path

from .catalog import (
    ALL_REPOSITORIES,
    BASE_APT_PACKAGES,
    EDITOR_APT_PACKAGES,
    OPTIONAL_REPOSITORIES,
    REPOSITORIES,
    WORKSPACE_NAME,
    Repository,
)

Logger = Callable[[str], None]


def default_workspace() -> Path:
    return Path.home() / WORKSPACE_NAME


class Runner:
    def __init__(self, dry_run: bool = False, log: Logger = print) -> None:
        self.dry_run = dry_run
        self.log = log

    def run(self, command: Iterable[str], cwd: Path | None = None, check: bool = True) -> int:
        command = tuple(command)
        rendered = " ".join(command)
        if cwd:
            self.log(f"$ cd {cwd} && {rendered}")
        else:
            self.log(f"$ {rendered}")
        if self.dry_run:
            return 0

        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.log(line.rstrip())
        code = process.wait()
        if check and code != 0:
            raise subprocess.CalledProcessError(code, command)
        return code


def has_command(name: str) -> bool:
    return shutil.which(name) is not None


def apt_available() -> bool:
    return has_command("apt-get") and has_command("sudo")


def install_apt_packages(runner: Runner, packages: Iterable[str]) -> None:
    packages = tuple(dict.fromkeys(packages))
    if not packages:
        return
    if not apt_available():
        runner.log("Skipping apt packages: this machine does not have sudo + apt-get.")
        runner.log(f"Needed packages: {', '.join(packages)}")
        return

    runner.run(("sudo", "apt-get", "update"))
    available: list[str] = []
    for package in packages:
        code = runner.run(("apt-cache", "show", package), check=False)
        if code == 0:
            available.append(package)
        else:
            runner.log(f"Package not found in apt repositories: {package}")
    if available:
        runner.run(("sudo", "apt-get", "install", "-y", *available))


def maybe_install_vscode_repo(runner: Runner) -> None:
    if not apt_available():
        return
    if runner.run(("apt-cache", "show", "code"), check=False) == 0:
        return
    arch = subprocess.check_output(("dpkg", "--print-architecture"), text=True).strip()
    if arch not in {"amd64", "arm64", "armhf"}:
        runner.log(f"Skipping VS Code repository setup for unsupported architecture: {arch}")
        return
    runner.run(("sudo", "install", "-d", "-m", "0755", "/etc/apt/keyrings"))
    runner.run(
        (
            "bash",
            "-lc",
            "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | "
            "gpg --dearmor | sudo tee /etc/apt/keyrings/packages.microsoft.gpg >/dev/null",
        )
    )
    runner.run(("sudo", "chmod", "0644", "/etc/apt/keyrings/packages.microsoft.gpg"))
    repo = f"deb [arch={arch} signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main"
    runner.run(("bash", "-lc", f"echo {repo!r} | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null"))


def selected_repositories(include_optional: bool = False) -> tuple[Repository, ...]:
    return ALL_REPOSITORIES if include_optional else REPOSITORIES


def clone_or_update_repositories(
    runner: Runner,
    workspace: Path = default_workspace(),
    include_optional: bool = False,
) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    for repo in selected_repositories(include_optional):
        destination = workspace / repo.name
        if (destination / ".git").exists():
            runner.run(("git", "pull", "--ff-only"), cwd=destination)
        elif destination.exists():
            runner.log(f"Skipping {repo.name}: {destination} exists but is not a git repository.")
        else:
            runner.run(("git", "clone", repo.url, str(destination)))


def install_python_requirements(runner: Runner, repo: Repository, repo_dir: Path) -> None:
    if not repo.requirements:
        return
    venv = repo_dir / ".venv"
    if not (venv / "bin" / "python").exists():
        runner.run(("python3", "-m", "venv", str(venv)))
    python = venv / "bin" / "python"
    runner.run((str(python), "-m", "pip", "install", "--upgrade", "pip", "wheel"))
    for requirement in repo.requirements:
        req_path = repo_dir / requirement
        if req_path.exists():
            runner.run((str(python), "-m", "pip", "install", "-r", str(req_path)))
        else:
            runner.log(f"Missing requirements file for {repo.name}: {requirement}")


def run_repo_setup_commands(runner: Runner, repo: Repository, repo_dir: Path) -> None:
    for command in repo.setup_commands:
        if not has_command(command[0]):
            runner.log(f"Skipping {repo.name} setup command: {command[0]} is not installed.")
            continue
        cwd = repo_dir / "rust" if repo.name == "sort-algo-visualizer" and command[0] == "cargo" else repo_dir
        runner.run(command, cwd=cwd)


def install_dependencies(
    runner: Runner,
    workspace: Path = default_workspace(),
    include_heavy: bool = False,
    editors: bool = True,
    include_optional: bool = False,
) -> None:
    install_apt_packages(runner, BASE_APT_PACKAGES)

    packages: list[str] = []
    if editors:
        maybe_install_vscode_repo(runner)
        packages.extend(EDITOR_APT_PACKAGES)
    for repo in selected_repositories(include_optional):
        if include_heavy or not repo.heavy:
            packages.extend(repo.apt_packages)
    install_apt_packages(runner, packages)

    for repo in selected_repositories(include_optional):
        if repo.heavy and not include_heavy:
            runner.log(f"Skipping heavier dependency setup for {repo.name}.")
            continue
        repo_dir = workspace / repo.name
        if repo_dir.exists():
            install_python_requirements(runner, repo, repo_dir)
            run_repo_setup_commands(runner, repo, repo_dir)
        else:
            runner.log(f"Skipping dependency setup for {repo.name}: repository is not downloaded yet.")


def install_everything(
    dry_run: bool = False,
    workspace: Path = default_workspace(),
    include_heavy: bool = False,
    editors: bool = True,
    include_optional: bool = False,
    log: Logger = print,
) -> None:
    runner = Runner(dry_run=dry_run, log=log)
    install_apt_packages(runner, BASE_APT_PACKAGES)
    clone_or_update_repositories(runner, workspace, include_optional=include_optional)
    install_dependencies(
        runner,
        workspace,
        include_heavy=include_heavy,
        editors=editors,
        include_optional=include_optional,
    )


def print_plan(
    include_heavy: bool = False,
    editors: bool = True,
    include_optional: bool = False,
    log: Logger = print,
) -> None:
    log(f"Workspace: {default_workspace()}")
    log("Target platform: Raspberry Pi OS 64-bit on Raspberry Pi 4 or newer.")
    log("Repositories:")
    for repo in selected_repositories(include_optional):
        marker = "heavy deps opt-in" if repo.heavy and not include_heavy else "heavy" if repo.heavy else "standard"
        log(f"  - {repo.name} ({repo.kind}, {marker})")
    if not include_optional:
        log("Optional repositories:")
        for repo in OPTIONAL_REPOSITORIES:
            log(f"  - {repo.name} ({repo.kind}, opt in with --include-optional)")
    packages = set(BASE_APT_PACKAGES)
    if editors:
        packages.update(EDITOR_APT_PACKAGES)
    for repo in selected_repositories(include_optional):
        if include_heavy or not repo.heavy:
            packages.update(repo.apt_packages)
    log("Apt packages:")
    log("  " + ", ".join(sorted(packages)))
    log("Python requirements:")
    for repo in selected_repositories(include_optional):
        if repo.requirements and (include_heavy or not repo.heavy):
            log(f"  - {repo.name}: {', '.join(repo.requirements)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install The Pi Academy coding projects.")
    parser.add_argument("action", choices=("all", "repos", "deps", "plan"), nargs="?", default="all")
    parser.add_argument("--workspace", type=Path, default=default_workspace())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-heavy", action="store_true", help="Install large ML/Rust dependency sets.")
    parser.add_argument("--skip-heavy", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--include-optional", action="store_true", help="Download optional projects such as object detection.")
    parser.add_argument("--skip-editors", action="store_true", help="Skip VS Code and kid-friendly editors.")
    args = parser.parse_args(argv)

    runner = Runner(dry_run=args.dry_run)
    include_heavy = args.include_heavy and not args.skip_heavy
    editors = not args.skip_editors
    if args.action == "plan":
        print_plan(include_heavy=include_heavy, editors=editors, include_optional=args.include_optional)
    elif args.action == "repos":
        clone_or_update_repositories(runner, args.workspace, include_optional=args.include_optional)
    elif args.action == "deps":
        install_dependencies(
            runner,
            args.workspace,
            include_heavy=include_heavy,
            editors=editors,
            include_optional=args.include_optional,
        )
    else:
        install_everything(
            dry_run=args.dry_run,
            workspace=args.workspace,
            include_heavy=include_heavy,
            editors=editors,
            include_optional=args.include_optional,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
