from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_TEXT = (
    SKILL_ROOT / "references" / "repository-publication.md"
).read_text(encoding="utf-8")


class RepositoryPublicationGovernanceTests(unittest.TestCase):
    def test_clean_checkout_result_defines_repository_contents(self) -> None:
        for fragment in (
            "用干净克隆确定仓库边界",
            "仓库承诺交付的用户结果",
            "必须跟踪的输入",
            "仓库明确承诺提供的 Skill",
            "已被 Git 跟踪、尚未跟踪、命中忽略规则",
            "当前工作区的成功拼成干净克隆成功",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_concurrent_writers_cannot_be_restored_or_published_by_accident(
        self,
    ) -> None:
        for fragment in (
            "同步客户端、生成器、编辑器监视器、其它 Agent 或进程",
            "不能解释的变化不得用 `git restore` 消掉",
            "不得顺手暂存",
            "是否证明提交遗漏了正式交付物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_remote_checks_are_verified_without_granting_fix_authority(
        self,
    ) -> None:
        for fragment in (
            "required checks",
            "部署任务或其它远端验证已经结束",
            "读取状态、日志和失败产物属于只读发布验证",
            "用户另行授权时才执行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_commit_or_push_does_not_override_project_deletion_rules(
        self,
    ) -> None:
        for fragment in (
            "读取项目规则对删除、归档、生成物和提交的额外限制",
            "通用的“提交”“推送到 main”或“发布”不能代替删除授权",
            "在暂存、提交或推送前准确列出所有待删除路径及理由",
            "任何受项目规则约束但尚未单独获准的删除都必须在暂存前停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_publication_still_preserves_existing_scope_gates(self) -> None:
        for fragment in (
            "推送授权只覆盖核对后的准确范围",
            "不自动包含同一工作树中的无关改动",
            "不创建提交、不创建远程仓库、不推送",
            "未经授权不通过强制推送、删除远程或改可见性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_final_candidate_evidence_follows_affected_consumers(
        self,
    ) -> None:
        for fragment in (
            "为最终候选内容建立验证账本",
            "候选身份：工作树基线、待暂存路径及内容身份",
            "正式消费者：构建器、运行时、用户界面",
            "最后一次相关变化之后",
            "可见界面、媒体或交互发生变化时",
            "类型检查或构建成功不能代替这条用户链",
            "不机械重跑无关产品回归",
            "重新核对索引中的变化事实、正式消费者和新鲜证据仍然匹配",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_git_checks_cover_untracked_candidate_files(self) -> None:
        for fragment in (
            "检查覆盖：每项检查预期读取什么",
            "已跟踪工作树差异、暂存索引、未跟踪文件和被忽略路径",
            "`git diff --check` 只能检查它实际选中的 Git 差异",
            "候选全是未跟踪文件",
            "未获暂存授权时",
            "对已批准候选路径执行等价只读检查",
            "不由工具默认排除代替",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


if __name__ == "__main__":
    unittest.main()
