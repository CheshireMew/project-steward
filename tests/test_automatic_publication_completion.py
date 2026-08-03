from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (ROOT / "README.md").read_text(encoding="utf-8")
STAR_TEXT = (ROOT / "references" / "github-star-history.md").read_text(
    encoding="utf-8"
)
PUBLICATION_TEXT = (ROOT / "references" / "repository-publication.md").read_text(
    encoding="utf-8"
)


class AutomaticPublicationCompletionTests(unittest.TestCase):
    def test_project_steward_self_evolution_publishes_the_approved_closure(self) -> None:
        for fragment in (
            "references/repository-publication.md",
            "精确提交并推送本轮获准依赖闭包",
            "核对远端 HEAD 后才完成",
            "远端、认证、分支保护、分叉或未获准依赖阻塞",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        self.assertIn("只改本地", SKILL_TEXT)
        self.assertIn("现有工作树中的其它修改不会被顺手纳入", README_TEXT)

    def test_star_history_stops_only_after_the_remote_consumer_works(self) -> None:
        for fragment in (
            "references/github-star-history.md",
            "references/repository-publication.md",
            "精确提交并推送调用仓库改动",
            "手动运行工作流",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "## 默认完成事务",
            "gh workflow run star-history.yml",
            "等待该次运行结束",
            "star-history` 分支、两个 SVG",
            "两个 raw 地址和 GitHub README",
            "只有上述远端链路全部成立才报告接入完成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAR_TEXT)

    def test_default_publication_keeps_existing_scope_guards(self) -> None:
        for fragment in (
            "不在本地验证后再次请求同一发布授权",
            "获准依赖闭包",
            "创建远端",
            "改变可见性",
            "强制推送",
            "无关工作树变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


if __name__ == "__main__":
    unittest.main()
