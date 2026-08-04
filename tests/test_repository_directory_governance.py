import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCE = SKILL_ROOT / "references" / "repository-directory-governance.md"
REFERENCE_TEXT = REFERENCE.read_text(encoding="utf-8")
OPENAI_TEXT = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
SCRIPT = SKILL_ROOT / "scripts" / "inspect_project_tree.py"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@unittest.skipUnless(
    shutil.which("git"), "Git is required for directory inventory tests"
)
class ProjectTreeInventoryTests(unittest.TestCase):
    def test_cli_reports_tracked_untracked_and_ignored_without_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-tree-") as temporary:
            repository = Path(temporary)
            run(["git", "init"], repository)
            run(["git", "config", "user.name", "Project Steward Test"], repository)
            run(["git", "config", "user.email", "test@example.invalid"], repository)

            (repository / "src").mkdir()
            (repository / "src" / "main.py").write_text(
                "print('ok')\n", encoding="utf-8"
            )
            (repository / "build").mkdir()
            (repository / "build" / "output.bin").write_bytes(b"generated")
            (repository / "notes.txt").write_text("local notes\n", encoding="utf-8")
            (repository / ".gitignore").write_text("/build/\n", encoding="utf-8")
            run(["git", "add", ".gitignore", "src/main.py"], repository)
            run(["git", "commit", "-m", "test: create tree fixture"], repository)
            (repository / "src" / "main.py").write_text(
                "print('changed')\n", encoding="utf-8"
            )

            status_before = run(
                ["git", "status", "--porcelain=v1", "--ignored"], repository
            ).stdout
            completed = run(
                [sys.executable, str(SCRIPT), str(repository), "--no-sizes"],
                repository,
            )
            status_after = run(
                ["git", "status", "--porcelain=v1", "--ignored"], repository
            ).stdout

            report = json.loads(completed.stdout)
            entries = {entry["name"]: entry for entry in report["entries"]}
            self.assertEqual(1, report["schema_version"])
            self.assertTrue(report["root"]["requested_is_git_root"])
            self.assertEqual("tracked", entries["src"]["git"]["disposition"])
            self.assertEqual(1, entries["src"]["git"]["tracked_path_count"])
            self.assertEqual(1, entries["src"]["git"]["changed_tracked_path_count"])
            self.assertEqual("untracked", entries["notes.txt"]["git"]["disposition"])
            self.assertEqual("ignored", entries["build"]["git"]["disposition"])
            self.assertIn("/build/", entries["build"]["git"]["ignore_rule_match"])
            self.assertEqual(status_before, status_after)

    def test_cli_reports_recursive_sizes_for_a_non_git_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-size-") as temporary:
            project = Path(temporary)
            (project / "assets" / "nested").mkdir(parents=True)
            (project / "assets" / "one.bin").write_bytes(b"1234")
            (project / "assets" / "nested" / "two.bin").write_bytes(b"567")

            completed = run([sys.executable, str(SCRIPT), str(project)], project)
            report = json.loads(completed.stdout)
            entries = {entry["name"]: entry for entry in report["entries"]}

            self.assertFalse(report["git"]["is_repository"])
            self.assertEqual(2, entries["assets"]["file_count"])
            self.assertEqual(7, entries["assets"]["size_bytes"])
            self.assertTrue(entries["assets"]["size_complete"])


class RepositoryDirectoryGovernanceContractTests(unittest.TestCase):
    def test_route_and_public_consumers_reach_the_unique_method(self) -> None:
        self.assertIn("项目目录治理", SKILL_TEXT)
        self.assertIn("references/repository-directory-governance.md", SKILL_TEXT)
        self.assertIn("scripts/inspect_project_tree.py", SKILL_TEXT)
        self.assertIn("项目目录", OPENAI_TEXT)

    def test_method_preserves_evidence_and_permission_boundaries(self) -> None:
        required_contracts = (
            "被 Git 跟踪，所以当前一定使用",
            "未跟踪或被忽略，所以可以删除",
            "目录被清理后又出现时，先定位再次创建它的正式生产者",
            "Windows 和默认大小写不敏感的文件系统",
            "将已跟踪目录移出仓库会在 Git 中表现为删除",
            "删除文件或目录需要当前用户与项目规则允许",
            "正式生产者或人工入口",
        )
        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, REFERENCE_TEXT)

    def test_main_skill_stays_within_its_budget(self) -> None:
        self.assertLessEqual(len(SKILL_TEXT.splitlines()), 220)
        self.assertLessEqual(len(SKILL_TEXT), 14_000)


if __name__ == "__main__":
    unittest.main()
