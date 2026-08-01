from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(
    os.environ.get(
        "PROJECT_STEWARD_ENTRY",
        str(SKILL_ROOT / "scripts" / "project_templates.py"),
    )
)
CATALOG = SKILL_ROOT / "assets" / "project-templates" / "catalog.json"


def run(
    command: list[str],
    cwd: Path,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_tool(
    command: str,
    project: Path | None = None,
    *,
    catalog: Path | None = None,
    extra: list[str] | None = None,
    check: bool = True,
) -> tuple[subprocess.CompletedProcess, dict | None]:
    arguments = [sys.executable, str(SCRIPT)]
    if catalog:
        arguments.extend(["--catalog", str(catalog)])
    arguments.append(command)
    if project is not None:
        arguments.append(str(project))
    arguments.extend(extra or [])
    arguments.append("--compact")
    completed = run(arguments, project or SKILL_ROOT, check=check)
    payload = json.loads(completed.stdout) if completed.stdout.strip() else None
    return completed, payload


def write_tauri_vue_fixture(
    root: Path,
    *,
    decorations: bool,
    close_method: str = "close",
    close_permission: str = "core:window:allow-close",
) -> None:
    (root / "src").mkdir(parents=True)
    (root / "src-tauri" / "capabilities").mkdir(parents=True)
    (root / "package.json").write_text(
        json.dumps(
            {
                "name": "tauri-vue-fixture",
                "dependencies": {
                    "@tauri-apps/api": "^2.0.0",
                    "vue": "^3.0.0",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "src-tauri" / "tauri.conf.json").write_text(
        json.dumps(
            {
                "app": {
                    "windows": [
                        {
                            "label": "main",
                            "title": "Fixture",
                            "decorations": decorations,
                        }
                    ]
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "src-tauri" / "capabilities" / "main.json").write_text(
        json.dumps(
            {
                "identifier": "main",
                "windows": ["main"],
                "permissions": [
                    "core:window:allow-minimize",
                    "core:window:allow-toggle-maximize",
                    close_permission,
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "src" / "App.vue").write_text(
        (
            "<template>\n"
            "  <header data-tauri-drag-region>\n"
            "    <button @click=\"minimize\">Minimize</button>\n"
            "    <button @click=\"maximize\">Maximize</button>\n"
            "    <button @click=\"closeWindow\">Close</button>\n"
            "  </header>\n"
            "</template>\n"
            "<script setup lang=\"ts\">\n"
            "import { getCurrentWindow } from '@tauri-apps/api/window'\n"
            "const appWindow = getCurrentWindow()\n"
            "const minimize = () => appWindow.minimize()\n"
            "const maximize = () => appWindow.toggleMaximize()\n"
            f"const closeWindow = () => appWindow.{close_method}()\n"
            "</script>\n"
        ),
        encoding="utf-8",
    )


class ProjectTemplateTests(unittest.TestCase):
    def test_unknown_template_field_is_rejected_and_not_listed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-provenance-"
        ) as temporary:
            root = Path(temporary)
            source_root = CATALOG.parent
            fixture_root = root / "project-templates"
            shutil.copytree(source_root, fixture_root)
            fixture_catalog_path = fixture_root / "catalog.json"
            fixture_catalog = json.loads(
                fixture_catalog_path.read_text(encoding="utf-8")
            )
            base_path = fixture_root / "templates" / "base.json"
            base = json.loads(base_path.read_text(encoding="utf-8"))
            base["obsolete_field"] = []
            base_path.write_text(
                json.dumps(base, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            fixture_catalog["templates"]["base"]["sha256"] = hashlib.sha256(
                base_path.read_bytes()
            ).hexdigest()
            fixture_catalog_path.write_text(
                json.dumps(
                    fixture_catalog,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            completed, payload = run_tool(
                "list",
                catalog=fixture_catalog_path,
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIsNone(payload)
            self.assertIn("unsupported fields: obsolete_field", completed.stderr)

            _, active_payload = run_tool("list")
            assert active_payload is not None
            for entry in active_payload["templates"]:
                self.assertNotIn("obsolete_field", entry)

    def test_plain_project_inside_parent_repository_stays_plain_and_is_consumed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-plain-"
        ) as temporary:
            parent = Path(temporary)
            run(["git", "init", "-b", "parent-root"], parent)
            project = parent / "ordinary-folder"
            project.mkdir()
            (project / "README.md").write_text(
                "# Ordinary project\n", encoding="utf-8"
            )

            _, inspected = run_tool("inspect", project)
            assert inspected is not None
            self.assertIsNone(inspected["git"])
            self.assertEqual(["base"], inspected["suggested_templates"])
            workspace_detection = inspected["detection"][
                "local-file-workspace"
            ]
            self.assertFalse(workspace_detection["matched"])
            self.assertEqual(
                "explicit_only",
                workspace_detection["details"][0]["signal"],
            )

            _, adopted = run_tool("adopt", project)
            assert adopted is not None
            self.assertEqual("adopted", adopted["status"])
            self.assertEqual(["base"], adopted["templates"])
            self.assertEqual(
                "passed", adopted["verification"]["status"]
            )
            profile_path = project / ".project-steward" / "project.json"
            self.assertTrue(profile_path.is_file())

            _, verified = run_tool("verify", project)
            assert verified is not None
            verification = verified["verification"]
            self.assertEqual("passed", verification["status"])
            self.assertTrue(verification["manual_verification_required"])
            self.assertIn(
                "base-primary-user-result",
                {
                    item["id"]
                    for item in verification["manual_verification"]
                },
            )
            before = profile_path.read_bytes()
            _, current = run_tool("upgrade", project)
            assert current is not None
            self.assertEqual("current", current["status"])
            self.assertEqual(before, profile_path.read_bytes())

    def test_exact_root_git_is_reported_only_when_marker_is_at_project_root(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-git-"
        ) as temporary:
            project = Path(temporary)
            run(["git", "init", "-b", "project-root"], project)

            _, inspected = run_tool("inspect", project)
            assert inspected is not None
            self.assertTrue(inspected["git"]["exact_root"])
            self.assertEqual("project-root", inspected["git"]["branch"])

    def test_design_context_selects_product_ui_and_real_consumer_reads_it(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-product-ui-"
        ) as temporary:
            project = Path(temporary)
            (project / "docs").mkdir()
            (project / "docs" / "DESIGN.md").write_text(
                "# Product interface\n", encoding="utf-8"
            )

            _, inspected = run_tool("inspect", project)
            assert inspected is not None
            self.assertEqual(
                ["base", "product-ui"],
                inspected["suggested_templates"],
            )

            _, adopted = run_tool("adopt", project)
            assert adopted is not None
            self.assertEqual(
                ["base", "product-ui"],
                adopted["templates"],
            )
            checks = {
                item["id"]: item
                for item in adopted["verification"]["checks"]
            }
            self.assertEqual(
                "pass",
                checks["ui-product-surface-contract"]["status"],
            )
            manual_ids = {
                item["id"]
                for item in adopted["verification"]["manual_verification"]
            }
            self.assertIn("ui-primary-task-visible-chain", manual_ids)
            self.assertIn("ui-interface-use-quality-chain", manual_ids)

            _, verified = run_tool("verify", project)
            assert verified is not None
            self.assertEqual("passed", verified["verification"]["status"])
            self.assertIn(
                "ui-visible-verification",
                {
                    item["id"]
                    for item in verified["verification"]["checks"]
                },
            )
            self.assertIn(
                "ui-optional-capability-disclosure",
                {
                    item["id"]
                    for item in verified["verification"]["checks"]
                },
            )
            self.assertIn(
                "ui-interface-use-quality",
                {
                    item["id"]
                    for item in verified["verification"]["checks"]
                },
            )

    def test_local_file_workspace_is_explicit_and_consumed_as_a_capability(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-workspace-"
        ) as temporary:
            project = Path(temporary)
            (project / "notes").mkdir()
            (project / "notes" / "README.md").write_text(
                "# Plain workspace\n", encoding="utf-8"
            )

            _, inspected = run_tool("inspect", project)
            assert inspected is not None
            self.assertEqual(["base"], inspected["suggested_templates"])
            self.assertFalse(
                inspected["detection"]["local-file-workspace"]["matched"]
            )

            _, listed = run_tool("list")
            assert listed is not None
            listed_workspace = next(
                item
                for item in listed["templates"]
                if item["id"] == "local-file-workspace"
            )
            self.assertEqual("explicit-only", listed_workspace["selection"])

            selection = ["--template", "local-file-workspace"]
            _, plan = run_tool("plan", project, extra=selection)
            assert plan is not None
            self.assertEqual("explicit", plan["selection_source"])
            self.assertEqual(
                ["base", "product-ui", "local-file-workspace"],
                plan["selected_templates"],
            )
            self.assertEqual(
                "selected-folder-files",
                plan["target_profile"]["decisions"][
                    "workspace_content_truth"
                ],
            )

            _, adopted = run_tool("adopt", project, extra=selection)
            assert adopted is not None
            self.assertEqual(
                ["base", "product-ui", "local-file-workspace"],
                adopted["templates"],
            )
            checks = {
                item["id"]: item
                for item in adopted["verification"]["checks"]
            }
            self.assertEqual(
                "pass", checks["workspace-content-truth-decision"]["status"]
            )
            self.assertEqual(
                "pass",
                checks["workspace-version-control-decision"]["status"],
            )
            manual_ids = {
                item["id"]
                for item in adopted["verification"]["manual_verification"]
            }
            self.assertIn("workspace-plain-folder-chain", manual_ids)
            self.assertIn("workspace-tree-visible-chain", manual_ids)
            self.assertIn("workspace-source-fidelity-chain", manual_ids)

            _, verified = run_tool("verify", project)
            assert verified is not None
            self.assertEqual("passed", verified["verification"]["status"])
            self.assertTrue(
                verified["verification"]["manual_verification_required"]
            )

    def test_tauri_vue_producer_adopt_consumer_verify_and_regression(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-tauri-"
        ) as temporary:
            project = Path(temporary)
            write_tauri_vue_fixture(project, decorations=False)

            _, inspected = run_tool("inspect", project)
            assert inspected is not None
            self.assertEqual(
                ["base", "product-ui", "desktop-app", "tauri-vue"],
                inspected["suggested_templates"],
            )

            _, adopted = run_tool("adopt", project)
            assert adopted is not None
            self.assertEqual("adopted", adopted["status"])
            self.assertEqual(
                ["base", "product-ui", "desktop-app", "tauri-vue"],
                adopted["templates"],
            )
            checks = {
                item["id"]: item
                for item in adopted["verification"]["checks"]
            }
            self.assertEqual(
                "pass", checks["tauri-window-shell-chain"]["status"]
            )
            self.assertFalse(
                checks["tauri-window-shell-chain"]["evidence"][
                    "destroy_call"
                ]
            )
            manual_ids = {
                item["id"]
                for item in adopted["verification"]["manual_verification"]
            }
            self.assertIn("desktop-window-visual-chain", manual_ids)
            self.assertIn("ui-primary-task-visible-chain", manual_ids)
            self.assertIn("tauri-windows-shell-runtime", manual_ids)

            config_path = project / "src-tauri" / "tauri.conf.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["app"]["windows"][0]["decorations"] = True
            config_path.write_text(
                json.dumps(config, indent=2) + "\n", encoding="utf-8"
            )

            completed, verified = run_tool(
                "verify", project, check=False
            )
            self.assertEqual(1, completed.returncode)
            assert verified is not None
            self.assertEqual(
                "failed", verified["verification"]["status"]
            )
            self.assertIn(
                "tauri-window-shell-chain",
                verified["verification"]["failed_check_ids"],
            )

    def test_destroy_without_allow_destroy_blocks_adoption_without_writing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-destroy-"
        ) as temporary:
            project = Path(temporary)
            write_tauri_vue_fixture(
                project,
                decorations=False,
                close_method="destroy",
                close_permission="core:window:allow-close",
            )

            completed, result = run_tool(
                "adopt", project, check=False
            )
            self.assertEqual(1, completed.returncode)
            assert result is not None
            self.assertEqual("blocked", result["status"])
            preflight = result["plan"]["preflight"]
            self.assertIn(
                "tauri-window-shell-chain",
                preflight["failed_check_ids"],
            )
            shell_check = next(
                item
                for item in preflight["checks"]
                if item["id"] == "tauri-window-shell-chain"
            )
            self.assertIn(
                "core:window:allow-destroy",
                shell_check["evidence"]["missing_permissions"],
            )
            self.assertFalse(
                (project / ".project-steward" / "project.json").exists()
            )

    def test_permissions_on_another_window_do_not_satisfy_the_main_window(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-window-scope-"
        ) as temporary:
            project = Path(temporary)
            write_tauri_vue_fixture(project, decorations=False)
            capability_path = (
                project / "src-tauri" / "capabilities" / "main.json"
            )
            capability = json.loads(
                capability_path.read_text(encoding="utf-8")
            )
            capability["windows"] = ["settings"]
            capability_path.write_text(
                json.dumps(capability, indent=2) + "\n",
                encoding="utf-8",
            )

            completed, result = run_tool(
                "adopt", project, check=False
            )
            self.assertEqual(1, completed.returncode)
            assert result is not None
            shell_check = next(
                item
                for item in result["plan"]["preflight"]["checks"]
                if item["id"] == "tauri-window-shell-chain"
            )
            self.assertIn(
                "core:window:allow-close",
                shell_check["evidence"]["missing_permissions"],
            )
            self.assertEqual(
                [],
                shell_check["evidence"]["target_permissions"],
            )

    def test_test_fixture_window_calls_cannot_replace_production_shell_calls(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-production-chain-"
        ) as temporary:
            project = Path(temporary)
            write_tauri_vue_fixture(project, decorations=False)
            original = (project / "src" / "App.vue").read_text(
                encoding="utf-8"
            )
            (project / "tests").mkdir()
            (project / "tests" / "fake-window-chain.ts").write_text(
                original,
                encoding="utf-8",
            )
            (project / "src" / "App.vue").write_text(
                "<template><main>Missing production titlebar</main></template>\n",
                encoding="utf-8",
            )

            completed, result = run_tool(
                "adopt", project, check=False
            )
            self.assertEqual(1, completed.returncode)
            assert result is not None
            shell_check = next(
                item
                for item in result["plan"]["preflight"]["checks"]
                if item["id"] == "tauri-window-shell-chain"
            )
            self.assertEqual("fail", shell_check["status"])
            self.assertNotIn(
                "tests/fake-window-chain.ts",
                shell_check["evidence"]["frontend_files_scanned"],
            )
            self.assertIn(
                "Tauri current-window API boundary",
                shell_check["evidence"]["missing_features"],
            )

    def test_native_explicit_requires_native_decorations_without_duplicate_shell(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-native-shell-"
        ) as temporary:
            root = Path(temporary)
            duplicate = root / "duplicate"
            duplicate.mkdir()
            write_tauri_vue_fixture(duplicate, decorations=True)
            completed, result = run_tool(
                "adopt",
                duplicate,
                extra=["--decision", "window_shell=native-explicit"],
                check=False,
            )
            self.assertEqual(1, completed.returncode)
            assert result is not None
            shell_check = next(
                item
                for item in result["plan"]["preflight"]["checks"]
                if item["id"] == "tauri-window-shell-chain"
            )
            self.assertIn(
                "custom drag region",
                shell_check["evidence"]["duplicate_signals"],
            )

            native = root / "native"
            native.mkdir()
            write_tauri_vue_fixture(native, decorations=True)
            (native / "src" / "App.vue").write_text(
                "<template><main>Native window shell</main></template>\n",
                encoding="utf-8",
            )
            _, adopted = run_tool(
                "adopt",
                native,
                extra=["--decision", "window_shell=native-explicit"],
            )
            assert adopted is not None
            self.assertEqual("adopted", adopted["status"])
            shell_check = next(
                item
                for item in adopted["verification"]["checks"]
                if item["id"] == "tauri-window-shell-chain"
            )
            self.assertEqual("pass", shell_check["status"])

    def test_catalog_hash_is_enforced_through_public_list_command(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-catalog-"
        ) as temporary:
            copied_root = Path(temporary) / "project-templates"
            shutil.copytree(CATALOG.parent, copied_root)
            copied_catalog = copied_root / "catalog.json"
            base_path = copied_root / "templates" / "base.json"
            base_path.write_text(
                base_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )

            completed, payload = run_tool(
                "list",
                catalog=copied_catalog,
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIsNone(payload)
            self.assertIn("integrity mismatch", completed.stderr)

    def test_real_profile_drift_is_planned_upgraded_and_reconsumed(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-upgrade-"
        ) as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            (project / "README.md").write_text("# Upgrade\n", encoding="utf-8")
            run_tool("adopt", project)

            copied_root = root / "catalog"
            shutil.copytree(CATALOG.parent, copied_root)
            copied_catalog = copied_root / "catalog.json"
            catalog = json.loads(copied_catalog.read_text(encoding="utf-8"))
            base_path = copied_root / "templates" / "base.json"
            base = json.loads(base_path.read_text(encoding="utf-8"))
            base["version"] = "1.2.0"
            base["defaults"]["decisions"][
                "diagnostic_handling"
            ] = "evidence-classified"
            base_path.write_text(
                json.dumps(base, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            digest = hashlib.sha256(base_path.read_bytes()).hexdigest()
            catalog["catalog_version"] = "2.3.0"
            catalog["templates"]["base"]["version"] = "1.2.0"
            catalog["templates"]["base"]["sha256"] = digest
            copied_catalog.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            before, verification = run_tool(
                "verify",
                project,
                catalog=copied_catalog,
                check=False,
            )
            self.assertEqual(1, before.returncode)
            assert verification is not None
            drift_kinds = {
                item["kind"]
                for item in verification["verification"]["drift"]
            }
            self.assertIn("version", drift_kinds)
            self.assertIn("catalog", drift_kinds)

            _, plan = run_tool(
                "plan", project, catalog=copied_catalog
            )
            assert plan is not None
            self.assertEqual("upgrade", plan["action"])
            self.assertEqual(
                "1.2.0", plan["target_profile"]["templates"][0]["version"]
            )
            self.assertEqual(
                "evidence-classified",
                plan["target_profile"]["decisions"]["diagnostic_handling"],
            )
            self.assertEqual("passed", plan["preflight"]["status"])

            _, upgraded = run_tool(
                "upgrade", project, catalog=copied_catalog
            )
            assert upgraded is not None
            self.assertEqual("upgraded", upgraded["status"])
            self.assertEqual("passed", upgraded["verification"]["status"])

            profile = json.loads(
                (project / ".project-steward" / "project.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("2.3.0", profile["catalog_version"])
            self.assertEqual("1.2.0", profile["templates"][0]["version"])
            self.assertEqual(
                "evidence-classified",
                profile["decisions"]["diagnostic_handling"],
            )

    def test_untracked_project_decision_cannot_be_silently_overwritten(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-decision-drift-"
        ) as temporary:
            project = Path(temporary)
            (project / "README.md").write_text(
                "# Decision drift\n", encoding="utf-8"
            )
            run_tool("adopt", project)
            profile_path = project / ".project-steward" / "project.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["decisions"]["source_of_truth"] = "database-mirror"
            profile_path.write_text(
                json.dumps(profile, indent=2) + "\n",
                encoding="utf-8",
            )

            completed, payload = run_tool(
                "upgrade", project, check=False
            )
            self.assertEqual(2, completed.returncode)
            self.assertIsNone(payload)
            self.assertIn(
                "--decision before upgrade",
                completed.stderr,
            )

            _, upgraded = run_tool(
                "upgrade",
                project,
                extra=["--decision", "source_of_truth=project-files"],
            )
            assert upgraded is not None
            self.assertEqual("upgraded", upgraded["status"])
            self.assertEqual("passed", upgraded["verification"]["status"])


if __name__ == "__main__":
    unittest.main()
