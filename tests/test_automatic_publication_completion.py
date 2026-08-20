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
PUBLICATION_EXECUTION_TEXT = (
    ROOT / "references" / "repository-publication-execution.md"
).read_text(encoding="utf-8")


class AutomaticPublicationCompletionTests(unittest.TestCase):
    def test_project_steward_self_evolution_publishes_the_entire_worktree(self) -> None:
        for fragment in (
            "references/repository-publication.md",
            "整个工作区按实际影响验证",
            "使用 `git add -A`",
            "已跟踪修改、未跟踪文件和现有删除",
            "推送成功后停止",
            "不等待远端检查",
            "任何一项不能共同发布时保留完整工作区",
            "不退回选择性提交",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        self.assertIn("只改本地", SKILL_TEXT)

    def test_star_history_dispatches_and_stops_without_waiting(self) -> None:
        for fragment in (
            "references/github-star-history.md",
            "references/repository-publication.md",
            "精确提交并推送调用仓库改动",
            "手动派发工作流后立即停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "## 默认完成事务",
            "gh workflow run star-history.yml",
            "不运行 `gh run watch`",
            "派发成功后立即停止",
            "用户后来明确要求远端验收",
            "异步未验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAR_TEXT)

    def test_default_publication_keeps_existing_scope_guards(self) -> None:
        for fragment in (
            "普通项目只有在用户明确要求提交或推送",
            "只处理获准依赖闭包",
            "在推送成功后停止",
            "不等待 GitHub Actions、部署或其它远端验证",
            "获准依赖闭包",
            "创建远端",
            "改变可见性",
            "强制推送",
            "无关工作树变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_explicit_default_branch_result_owns_its_required_merge_gate(
        self,
    ) -> None:
        for fragment in (
            "用户明确要求准确改动进入默认分支",
            "候选分支、PR、准确候选 required checks",
            "但不授权修复失败或改变远端设置",
            "只有准确候选的必需检查通过、合并成功",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

        for fragment in (
            "停止位置明确是默认分支包含候选时",
            "required checks 是该结果的前置门",
            "与当前结果无关的可选检查单独报告",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_EXECUTION_TEXT)

    def test_project_steward_invocation_does_not_publish_the_target_project(
        self,
    ) -> None:
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "点名 Project Steward 只选择治理方法",
            "不授予目标项目提交、推送或发布权限",
            "普通目标项目修改在本机相关验证后停止",
            "只有用户明确要求提交或推送",
            "Project Steward 自我进化与 Star History 分别按各自主路径处理",
            "不能互相补造权限",
            "提交或推送不自动授权等待 GitHub Actions",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, shared)

        for fragment in (
            "调用 Project Steward、允许修改目标项目或确认治理方案，都不自动授权提交和推送该目标项目",
            "普通项目只有在用户明确要求提交或推送",
            "Star History 使用其叶子方法的独立展示优化合同",
            "都不能为普通目标项目补造发布权限",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

        self.assertNotIn(
            "### 明确点名 Project Steward 的实施默认推送即停止",
            PUBLICATION_TEXT,
        )

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
            "推送前核对工作区没有遗漏",
            "推送命令成功后立即停止",
            "不再执行状态回读",
            "不等待 GitHub Actions",
            "工作区没有遗漏",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_public_install_entry_stops_after_push(self) -> None:
        for fragment in (
            "自动同步公开安装入口",
            "公开入口不存在、尚未发布或检查失败时不写占位命令",
            "安装段落、项目清单与发布配置进入同一次获准发布闭包",
            "推送成功后停止",
            "正式安装消费者",
            "远端消费仍是异步状态",
            "用户另行明确要求远端验收",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


if __name__ == "__main__":
    unittest.main()
