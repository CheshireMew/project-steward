from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
STAR_TEXT = (ROOT / "references" / "github-star-history.md").read_text(
    encoding="utf-8"
)
PUBLICATION_TEXT = (ROOT / "references" / "repository-publication.md").read_text(
    encoding="utf-8"
)


class AutomaticPublicationCompletionTests(unittest.TestCase):
    def test_project_steward_self_evolution_publishes_the_entire_worktree(self) -> None:
        for fragment in (
            "references/repository-publication.md",
            "整个工作区按实际影响验证",
            "使用 `git add -A`",
            "已跟踪修改、未跟踪文件和现有删除",
            "核对远端 HEAD 和工作区无遗漏后才完成",
            "任何一项不能共同发布时保留完整工作区",
            "不退回选择性提交",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        self.assertIn("只改本地", SKILL_TEXT)

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

    def test_self_evolution_full_worktree_is_an_explicit_publication_exception(self) -> None:
        section = PUBLICATION_TEXT.split(
            "### Project Steward 自我进化使用整仓发布合同",
            1,
        )[1].split("### 本地提交与远端状态分层交付", 1)[0]
        for fragment in (
            "整个当前工作区是一个不可拆分的发布范围",
            "工作区不干净不是跳过文件、缩小历史调查或拒绝修改的理由",
            "全部已跟踪修改、未跟踪文件和现有删除",
            "不按任务、来源、文件或内容片段选择性排除",
            "本地尚未推送提交",
            "保留完整工作区并停止",
            "使用 `git add -A`",
            "创建为一个新提交",
            "远端 HEAD 与本地 HEAD 相同",
            "工作区没有遗漏",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_public_install_entry_finishes_at_the_remote_consumer(self) -> None:
        for fragment in (
            "自动同步公开安装入口",
            "公开入口不存在、尚未发布或检查失败时不写占位命令",
            "安装段落、项目清单与发布配置进入同一次获准发布闭包",
            "推送后回读远端提交中的全部活动语言 README",
            "正式安装消费者",
            "安装入口仍未完成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


if __name__ == "__main__":
    unittest.main()
