from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REVIEW = SKILL_ROOT / "scripts" / "repository_branch_containment.py"
REFERENCE = SKILL_ROOT / "references" / "repository-publication-execution.md"


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def commit(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-m", f"add {name}")


def initialize(repo: Path) -> None:
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Project Steward Test")
    git(repo, "config", "user.email", "project-steward@example.invalid")
    commit(repo, "base.txt", "base\n")


def review(repo: Path, source: str = "topic", destination: str = "main") -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            str(REVIEW),
            str(repo),
            "--source",
            source,
            "--destination",
            destination,
            "--compact",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout)


class RepositoryBranchContainmentTests(unittest.TestCase):
    def test_method_separates_graph_containment_history_remote_and_authorization(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for phrase in (
            "scripts/repository_branch_containment.py",
            "来源独有提交为零",
            "两个分支同一 SHA 只是充分但非必要条件",
            "不能证明历史上一定执行过 merge 命令",
            "本地分支、远端分支和其它 worktree 分别成立",
            "不是当前分支",
            "非强制删除",
            "远端分支删除是另一项授权",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_same_tip_is_contained_without_mutating_refs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-branch-") as temporary:
            repo = Path(temporary) / "repo"
            initialize(repo)
            git(repo, "branch", "topic")
            before = git(repo, "show-ref")

            payload = review(repo)

            self.assertTrue(payload["same_tip"])
            self.assertTrue(payload["contained_in_current_graph"])
            self.assertEqual(0, payload["source_unique_commits"])
            self.assertTrue(payload["technically_eligible_for_local_delete"])
            self.assertEqual("not-queried", payload["remote_state"])
            self.assertEqual(before, git(repo, "show-ref"))

    def test_merged_branch_need_not_share_the_destination_tip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-branch-") as temporary:
            repo = Path(temporary) / "repo"
            initialize(repo)
            git(repo, "switch", "-c", "topic")
            commit(repo, "topic.txt", "topic\n")
            git(repo, "switch", "main")
            git(repo, "merge", "--no-ff", "--no-edit", "topic")

            payload = review(repo)

            self.assertFalse(payload["same_tip"])
            self.assertTrue(payload["contained_in_current_graph"])
            self.assertEqual(0, payload["source_unique_commits"])
            self.assertGreater(payload["destination_unique_commits"], 0)
            self.assertTrue(payload["technically_eligible_for_local_delete"])

    def test_divergence_and_other_worktree_block_local_deletion(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-branch-") as temporary:
            root = Path(temporary)
            repo = root / "repo"
            initialize(repo)
            git(repo, "switch", "-c", "topic")
            commit(repo, "topic.txt", "topic\n")
            git(repo, "switch", "main")
            commit(repo, "main.txt", "main\n")

            divergent = review(repo)
            self.assertFalse(divergent["contained_in_current_graph"])
            self.assertIn(
                "source-has-commits-not-contained-in-destination",
                divergent["deletion_blockers"],
            )

            git(repo, "merge", "--no-ff", "--no-edit", "topic")
            linked = root / "linked"
            git(repo, "worktree", "add", str(linked), "topic")
            occupied = review(repo)
            self.assertTrue(occupied["contained_in_current_graph"])
            self.assertFalse(occupied["technically_eligible_for_local_delete"])
            self.assertIn("source-is-checked-out-in-worktree", occupied["deletion_blockers"])
            self.assertIn(str(linked.resolve()), occupied["source_checked_out_worktrees"])


if __name__ == "__main__":
    unittest.main()
