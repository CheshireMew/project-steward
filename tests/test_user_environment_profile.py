from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "user_environment_profile.py"
SCHEMA = (
    SKILL_ROOT
    / "assets"
    / "user-environment"
    / "profile.schema.json"
)


def run_profile(
    *arguments: str,
    environment: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        timeout=120,
    )


def existing_non_system_root() -> Path | None:
    if os.name != "nt":
        return None
    system_drive = os.environ.get("SystemDrive", "C:").rstrip("\\/").lower()
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{letter}:\\")
        if root.is_dir() and f"{letter}:".lower() != system_drive:
            return root
    return None


class UserEnvironmentProfileTests(unittest.TestCase):
    def test_plan_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            completed = run_profile(
                "plan",
                "--profile",
                str(profile),
                "--default-tool",
                f"python={sys.executable}",
            )
            result = json.loads(completed.stdout)
            self.assertEqual("create", result["action"])
            self.assertFalse(profile.exists())

    def test_real_producer_profile_consumer_and_python_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            environment = os.environ.copy()
            environment["PROJECT_STEWARD_TEST_TOKEN"] = (
                "must-not-enter-environment-profile"
            )

            applied = run_profile(
                "apply",
                "--profile",
                str(profile),
                "--default-tool",
                f"python={sys.executable}",
                "--write",
                environment=environment,
            )
            self.assertTrue(json.loads(applied.stdout)["written"])
            self.assertTrue(profile.is_file())

            inspected = json.loads(
                run_profile(
                    "inspect",
                    "--profile",
                    str(profile),
                    environment=environment,
                ).stdout
            )
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            self.assertEqual(
                schema["properties"]["schema_version"]["const"],
                inspected["schema_version"],
            )
            serialized = profile.read_text(encoding="utf-8")
            self.assertNotIn("PROJECT_STEWARD_TEST_TOKEN", serialized)
            self.assertNotIn("must-not-enter-environment-profile", serialized)

            verified = json.loads(
                run_profile(
                    "verify",
                    "--profile",
                    str(profile),
                    environment=environment,
                ).stdout
            )
            self.assertTrue(verified["valid"], verified["issues"])

            resolved = json.loads(
                run_profile(
                    "resolve",
                    "--profile",
                    str(profile),
                    "--capability",
                    "python",
                    environment=environment,
                ).stdout
            )
            executable = resolved["tool"]["executable"]
            consumed = subprocess.run(
                [
                    executable,
                    "-c",
                    "import json,sys;print(json.dumps("
                    "{'executable':sys.executable,'version':sys.version.split()[0]}"
                    "))",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**environment, **resolved["environment"]},
                timeout=30,
            )
            actual = json.loads(consumed.stdout)
            self.assertEqual(
                os.path.normcase(str(Path(executable).resolve())),
                os.path.normcase(str(Path(actual["executable"]).resolve())),
            )
            self.assertEqual(
                resolved["tool"]["version"],
                actual["version"],
            )

    def test_verify_reports_a_drifted_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            run_profile(
                "apply",
                "--profile",
                str(profile),
                "--default-tool",
                f"python={sys.executable}",
                "--write",
            )
            value = json.loads(profile.read_text(encoding="utf-8"))
            value["tools"]["python"][0]["executable"] = str(
                Path(temporary) / "missing-python.exe"
            )
            profile.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            completed = run_profile(
                "verify",
                "--profile",
                str(profile),
                check=False,
            )
            self.assertEqual(1, completed.returncode)
            result = json.loads(completed.stdout)
            self.assertFalse(result["valid"])
            self.assertTrue(
                any(
                    issue["issue"] == "recorded executable is missing"
                    for issue in result["issues"]
                )
            )

    def test_schema_rejects_unknown_profile_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            run_profile(
                "apply",
                "--profile",
                str(profile),
                "--default-tool",
                f"python={sys.executable}",
                "--write",
            )
            value = json.loads(profile.read_text(encoding="utf-8"))
            value["unexpected"] = True
            profile.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            completed = run_profile(
                "inspect",
                "--profile",
                str(profile),
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("profile.unexpected is not allowed", completed.stderr)

    def test_large_content_policy_uses_real_profile_and_storage_consumer(
        self,
    ) -> None:
        storage_root = existing_non_system_root()
        if storage_root is None:
            self.skipTest("no existing non-system Windows drive is available")

        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            applied = run_profile(
                "apply",
                "--profile",
                str(profile),
                "--avoid-system-drive-for-large-content",
                "--large-content-root",
                f"media={storage_root}",
                "--write",
            )
            self.assertTrue(json.loads(applied.stdout)["written"])

            inspected = json.loads(
                run_profile("inspect", "--profile", str(profile)).stdout
            )
            policy = inspected["preferences"]["large_content_storage"]
            self.assertTrue(policy["avoid_system_drive"])

            verified = json.loads(
                run_profile("verify", "--profile", str(profile)).stdout
            )
            self.assertTrue(verified["valid"], verified["issues"])

            resolved = json.loads(
                run_profile(
                    "resolve-storage",
                    "--profile",
                    str(profile),
                    "--category",
                    "media",
                ).stdout
            )
            self.assertEqual(
                os.path.normcase(str(storage_root.resolve())),
                os.path.normcase(str(Path(resolved["root"]).resolve())),
            )
            self.assertTrue(resolved["policy"]["avoid_system_drive"])

    def test_large_content_policy_rejects_a_system_drive_root(self) -> None:
        if os.name != "nt":
            self.skipTest("system-drive policy is a Windows volume boundary")
        system_root = Path(os.environ.get("SystemDrive", "C:")) / "\\"
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "environment-profile.json"
            completed = run_profile(
                "plan",
                "--profile",
                str(profile),
                "--avoid-system-drive-for-large-content",
                "--large-content-root",
                f"generated-output={system_root}",
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn(
                "large content roots conflict with the system-drive avoidance policy",
                completed.stderr,
            )
            self.assertFalse(profile.exists())


if __name__ == "__main__":
    unittest.main()
