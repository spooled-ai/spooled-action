from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "scripts" / "install-spooled.sh"


class ActionContractTests(unittest.TestCase):
    def _run_installer(
        self,
        *,
        source: str = "",
        version: str = "",
        extra_deps: str = "",
    ) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            fake_bin = work / "bin"
            fake_bin.mkdir()
            pip_log = work / "pip-argv.txt"
            fake_pip = fake_bin / "pip"
            fake_pip.write_text(
                '#!/usr/bin/env bash\nprintf "%s\\n" "$@" >> "$SPOOLED_TEST_PIP_LOG"\n'
            )
            fake_pip.chmod(0o755)

            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{fake_bin}:{environment['PATH']}",
                    "SPOOLED_TEST_PIP_LOG": str(pip_log),
                    "SPOOLED_SOURCE_INPUT": source,
                    "SPOOLED_VERSION_INPUT": version,
                    "SPOOLED_EXTRA_DEPS_INPUT": extra_deps,
                    "SPOOLED_ACTION_PATH": str(work / "external-action"),
                }
            )
            completed = subprocess.run(
                ["bash", str(INSTALLER)],
                cwd=REPO_ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            argv = pip_log.read_text().splitlines() if pip_log.exists() else []
            return completed, argv

    def test_action_wires_source_without_shell_interpolation(self) -> None:
        action = yaml.safe_load((REPO_ROOT / "action.yml").read_text())
        install = next(
            step for step in action["runs"]["steps"] if step["name"] == "Install Spooled"
        )

        self.assertFalse(action["inputs"]["spooled-source"]["required"])
        self.assertEqual(
            install["env"]["SPOOLED_SOURCE_INPUT"],
            "${{ inputs.spooled-source }}",
        )
        self.assertNotIn("${{ inputs.spooled-source }}", install["run"])

    def test_exact_unreleased_source_is_one_requirement(self) -> None:
        source = "https://github.com/spooled-ai/spooled/archive/" + ("a" * 40) + ".tar.gz"

        completed, argv = self._run_installer(source=source)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(argv, ["install", f"spooled-ai @ {source}"])

    def test_exact_pypi_version_is_supported(self) -> None:
        completed, argv = self._run_installer(version="0.9.0")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(argv, ["install", "spooled-ai==0.9.0"])

    def test_latest_pypi_is_the_default(self) -> None:
        completed, argv = self._run_installer()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(argv, ["install", "spooled-ai"])

    def test_ambiguous_candidate_is_rejected(self) -> None:
        completed, argv = self._run_installer(
            source="https://example.invalid/spooled.tar.gz",
            version="0.9.0",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(argv, [])
        self.assertIn(
            "Set only one of spooled-source or spooled-version",
            completed.stderr,
        )

    def test_missing_extra_dependencies_fail_loudly(self) -> None:
        completed, argv = self._run_installer(
            extra_deps="/does/not/exist/requirements.txt"
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(argv, ["install", "spooled-ai"])
        self.assertIn("extra-deps file not found", completed.stderr)


if __name__ == "__main__":
    unittest.main()
