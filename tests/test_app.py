from contextlib import suppress
import subprocess
import unittest
from unittest.mock import patch

from textual.worker import WorkerFailed, WorkerState

from tpa_tui.app import TpaSetupApp


class InstallWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_command_keeps_menu_alive_and_allows_retry(self):
        app = TpaSetupApp()
        lines = []
        original = app.log_line

        def capture(line):
            lines.append(line)
            original(line)

        app.log_line = capture
        failure = subprocess.CalledProcessError(1, ["mvn", "-q", "dependency:go-offline"])
        with patch("tpa_tui.app.install_everything", side_effect=failure) as install:
            async with app.run_test() as pilot:
                await pilot.press("a")
                with suppress(WorkerFailed):
                    await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertTrue(any("Install failed" in line and "mvn" in line for line in lines))
                self.assertFalse(any(line.startswith("Completed:") for line in lines))
                await pilot.press("p")
                await pilot.pause()
                self.assertIn("Repositories:", lines)
                install.side_effect = None
                await pilot.press("a")
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(install.call_count, 2)
                self.assertIn("Completed: install_all_projects", lines)

    async def test_all_install_workers_handle_missing_executable(self):
        cases = (
            ("install_repos", "clone_or_update_repositories"),
            ("install_standard_dependencies", "install_dependencies"),
            ("install_optional_projects", "clone_or_update_repositories"),
            ("install_editor_packages", "install_apt_packages"),
            ("install_all_projects", "install_everything"),
        )
        for method, dependency in cases:
            with self.subTest(method=method):
                app = TpaSetupApp()
                with patch(f"tpa_tui.app.{dependency}", side_effect=FileNotFoundError("missing executable")):
                    async with app.run_test() as pilot:
                        worker = getattr(app, method)()
                        with self.assertRaises(WorkerFailed):
                            await worker.wait()
                        await pilot.pause()
                        self.assertEqual(worker.state, WorkerState.ERROR)
                        self.assertIsInstance(worker.error, FileNotFoundError)
                        self.assertFalse(worker.exit_on_error)


if __name__ == "__main__":
    unittest.main()
