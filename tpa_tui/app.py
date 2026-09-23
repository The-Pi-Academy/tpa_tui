from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Log, Static

from .catalog import EDITOR_APT_PACKAGES, OPTIONAL_REPOSITORIES, REPOSITORIES
from .installer import (
    Runner,
    clone_or_update_repositories,
    default_workspace,
    install_apt_packages,
    install_dependencies,
    install_everything,
    print_plan,
)


class TpaSetupApp(App[None]):
    CSS = """
    Screen {
        background: #1f1408;
        color: #fff8ed;
    }

    Header, Footer {
        background: #d17914;
        color: #1f1408;
    }

    #title {
        padding: 1 2;
        background: #2b1b0d;
        color: #fff8ed;
        border: tall #d17914;
        height: 5;
    }

    #actions {
        width: 34;
        padding: 1;
        background: #2b1b0d;
        border-right: solid #d17914;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    Button.-primary {
        background: #d17914;
        color: #1f1408;
    }

    #repos {
        height: 12;
        border: tall #d17914;
    }

    #log {
        border: tall #d17914;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "plan", "Plan"),
        ("r", "repos", "Repos"),
        ("d", "dependencies", "Deps"),
        ("a", "all", "All"),
    ]

    def __init__(self, workspace: Path | None = None) -> None:
        super().__init__()
        self.workspace = workspace or default_workspace()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "The Pi Academy Setup\n"
            f"Workspace: {self.workspace}\n"
            "Prepare Raspberry Pi OS 64-bit camp machines with repos, editors, and project dependencies.",
            id="title",
        )
        with Horizontal():
            with Vertical(id="actions"):
                yield Button("Install / Update Everything", id="all", variant="primary")
                yield Button("Download or Update Repositories", id="repos")
                yield Button("Install Editors", id="editors")
                yield Button("Install Dependencies", id="deps")
                yield Button("Install Optional + Heavy Projects", id="optional")
                yield Button("Show Dry-Run Plan", id="plan")
                yield Button("Quit", id="quit")
            with Vertical():
                table = DataTable(id="repos")
                table.add_columns("Repository", "Kind", "Notes")
                for repo in REPOSITORIES:
                    table.add_row(repo.name, repo.kind, "heavy deps opt-in" if repo.heavy else "standard")
                for repo in OPTIONAL_REPOSITORIES:
                    table.add_row(repo.name, repo.kind, "optional")
                yield table
                yield Log(id="log", highlight=True)
        yield Footer()

    def on_mount(self) -> None:
        self.title = "The Pi Academy Setup"
        self.log_line("Ready. Press 'a' to install everything or 'p' to preview the plan.")

    def log_line(self, line: str) -> None:
        self.query_one("#log", Log).write_line(line)

    def runner(self) -> Runner:
        return Runner(log=lambda line: self.call_from_thread(self.log_line, line))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "all":
                self.action_all()
            case "repos":
                self.action_repos()
            case "editors":
                self.install_editors()
            case "deps":
                self.action_dependencies()
            case "optional":
                self.action_optional()
            case "plan":
                self.action_plan()
            case "quit":
                self.exit()

    def action_plan(self) -> None:
        print_plan(log=self.log_line)

    @work(thread=True)
    def action_repos(self) -> None:
        clone_or_update_repositories(self.runner(), self.workspace)

    @work(thread=True)
    def action_dependencies(self) -> None:
        install_dependencies(self.runner(), self.workspace, include_heavy=False, editors=False)

    @work(thread=True)
    def action_optional(self) -> None:
        clone_or_update_repositories(self.runner(), self.workspace, include_optional=True)
        install_dependencies(
            self.runner(),
            self.workspace,
            include_heavy=True,
            editors=False,
            include_optional=True,
        )

    @work(thread=True)
    def install_editors(self) -> None:
        install_apt_packages(self.runner(), EDITOR_APT_PACKAGES)

    @work(thread=True)
    def action_all(self) -> None:
        install_everything(
            workspace=self.workspace,
            log=lambda line: self.call_from_thread(self.log_line, line),
        )


def main() -> None:
    TpaSetupApp().run()
