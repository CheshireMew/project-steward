from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


SKILL_TEXT = read("SKILL.md")
FORK_TEXT = read("references/source-fork-and-ecosystem-adoption.md")
PROJECT_RESEARCH_TEXT = read("references/project-research.md")
LICENSE_TEXT = read("references/license-governance.md")
USER_ENVIRONMENT_TEXT = read("references/user-environment-governance.md")


class SourceForkAndShellEvidenceGovernanceTests(unittest.TestCase):
    def test_source_fork_has_a_direct_route_and_unique_owner(self) -> None:
        self.assertIn(
            "references/source-fork-and-ecosystem-adoption.md",
            SKILL_TEXT,
        )
        self.assertIn("实际复制代码时同时读取", SKILL_TEXT)
        self.assertNotIn("references/", FORK_TEXT)

    def test_relationships_are_distinct_before_adoption(self) -> None:
        for fragment in (
            "运行时依赖",
            "一次性源码分叉",
            "兼容适配器",
            "机制借鉴",
            "不能用一个仓库级标签掩盖不同依赖方向",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_direct_reuse_and_method_learning_have_different_attribution(self) -> None:
        for fragment in (
            "### 原始上游、fork 与 README 致谢",
            "实际采用 fork 的独有改动",
            "直接复用或改编后再分发",
            "方法学习后的独立实现",
            "目标根 README 必须增加或更新“第三方资源与致谢”",
            "没有复制来源 IP、代码、资源、示例",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

        self.assertIn("追溯原始上游并区分直接复用与方法学习", SKILL_TEXT)
        self.assertIn("实际拟采用内容来自哪一层", PROJECT_RESEARCH_TEXT)
        self.assertIn("README 必须包含“第三方资源与致谢”", LICENSE_TEXT)
        self.assertIn("不能把来源写成目标正在使用的第三方依赖", LICENSE_TEXT)

    def test_a_fork_never_replaces_the_canonical_upstream(self) -> None:
        for text in (FORK_TEXT, LICENSE_TEXT):
            with self.subTest(source=text[:40]):
                self.assertIn("原始上游", text)
                self.assertIn("fork", text)

    def test_independent_product_owns_identity_state_and_updates(self) -> None:
        for fragment in (
            "目标仓库、发布单元和命令身份",
            "任务、状态、持久化与恢复的唯一真源",
            "目标版本、发布节奏和支持平台",
            "以后如何发现、审计和选择性采用上游变化",
            "上游不能继续通过内部导入",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_adoption_ledger_keeps_provenance_rejections_and_tests(self) -> None:
        for fragment in (
            "固定提交、版本和内容哈希",
            "许可证、版权、NOTICE",
            "采用范围",
            "目标所有者",
            "移植测试",
            "拒绝部分",
            "后续升级",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_core_never_depends_on_the_compatibility_package(self) -> None:
        for fragment in (
            "核心内化与外围兼容只允许单向依赖",
            "目标核心不能导入兼容包",
            "删除兼容包后",
            "不兼容版本在进入核心前明确拒绝",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_all_active_consumers_and_default_tests_are_migrated(self) -> None:
        for fragment in (
            "测试配置、模块别名、mock、fixture",
            "构建脚本、原生宿主、资源清单",
            "活动文档、示例、SDK 片段",
            "不能从残留扫描中整体排除",
            "目标默认测试入口",
            "测试文件存在但默认命令没有选择它",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_upstream_updates_are_new_audited_adoptions(self) -> None:
        for fragment in (
            "上游变化是新的采用事务",
            "没有自动同步、定期合并或无审计升级通道",
            "选择拒绝、机制借鉴、局部移植或兼容适配器升级",
            "不能用长期合并分支",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_delivery_layers_do_not_impersonate_each_other(self) -> None:
        for fragment in (
            "源码独立",
            "默认测试",
            "普通构建",
            "原生或生成产物",
            "当前实例采用",
            "打包与发布",
            "让相应层保持未验证或受阻",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, FORK_TEXT)

    def test_powershell_probe_failure_cannot_become_zero_findings(self) -> None:
        for fragment in (
            "PowerShell 证据不能由最后一条语句代替",
            "$ErrorActionPreference = \"Stop\"",
            "不能依赖整个脚本最后的 `$?`、`$LASTEXITCODE`",
            "只能在产生这些事实的权威查询已经独立成功后",
            "对应事实保持未知",
            "而不是零",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

    def test_tool_exit_codes_are_mapped_to_defined_result_semantics(self) -> None:
        for fragment in (
            "原始退出码与工具定义的结果语义分开记录",
            "非零不是通用失败标签",
            "`rg` 的 1 表示无匹配、2 才表示执行错误",
            "成功有结果、成功无结果、失败或未知",
            "未映射的非零保持未知",
            "不能让本来表示零匹配的结果提前终止后续证据链",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

    def test_shell_evidence_route_reaches_the_unique_platform_method(self) -> None:
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        environment_route = SKILL_TEXT.split(
            "## 用户环境档案与执行环境",
            1,
        )[1].split("## 项目综合审计", 1)[0]

        self.assertIn("隐藏项或转义失真时同样进入", shared)
        self.assertIn("先进入“用户环境档案与执行环境”", shared)
        self.assertIn("references/user-environment-governance.md", environment_route)
        self.assertNotIn("$LASTEXITCODE", shared)

    def test_hidden_control_items_require_a_hidden_aware_probe(self) -> None:
        for fragment in (
            "Windows 隐藏控制项不能由默认读取判定不存在",
            "不能证明准确字面量路径不存在",
            "Test-Path -LiteralPath <root>\\.git",
            "Get-Item -LiteralPath <root>\\.git -Force",
            "准确项目根直接存在 `.git`",
            "验证器假阴性",
            "不能为了让验证器看见对象而清除 `Hidden`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)


    def test_skill_main_file_stays_within_budget(self) -> None:
        self.assertLessEqual(len(SKILL_TEXT.splitlines()), 220)
        self.assertLessEqual(len(SKILL_TEXT), 14_000)


if __name__ == "__main__":
    unittest.main()
