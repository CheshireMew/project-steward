from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
CLI_TEXT = (ROOT / "references" / "agent-facing-cli-governance.md").read_text(
    encoding="utf-8"
)


class AgentFacingCLIGovernanceTests(unittest.TestCase):
    def test_external_agent_cli_has_one_prevention_route(self) -> None:
        prevention = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        external_tools = SKILL_TEXT.split("## 外部工具兼容性", 1)[1].split(
            "## 项目研究与讲解", 1
        )[0]

        self.assertEqual(
            SKILL_TEXT.count("references/agent-facing-cli-governance.md"), 1
        )
        self.assertIn("面向外部 Agent 新建项目 CLI", prevention)
        self.assertIn("references/structured-data-boundary.md", prevention)
        self.assertNotIn("agent-facing-cli-governance", external_tools)

    def test_method_keeps_external_agent_and_embedded_agent_separate(self) -> None:
        for fragment in (
            "Codex、Claude Code 等外部 Agent",
            "不把 Agent、模型调用、聊天界面或 Agent 编排层内置进产品",
            "项目调用第三方 CLI、SDK 或外部服务的兼容关系",
            "CLI 是应用边界外侧的薄适配器",
            "不直接实例化 repository",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CLI_TEXT)

    def test_command_registry_owns_a_concrete_machine_contract(self) -> None:
        for fragment in (
            "稳定身份",
            "结构化输入模型",
            "正常结果的具体 JSON Schema",
            "数据库状态、worker、外部服务、凭据",
            "调用者提供的幂等身份",
            "稳定退出码与错误类型",
            "注册表和能力发现是可执行真源",
            "不能作为尚未完成输出建模的占位",
            "用其公开 Schema 校验",
            "不能用通用 `str(value)`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CLI_TEXT)

    def test_read_only_process_and_durable_boundaries_are_preserved(self) -> None:
        for fragment in (
            "stdout 一次调用只包含一个版本化结果文档",
            "业务日志、进度、调试堆栈和第三方库的 `print` 进入 stderr",
            "原样转发参数、标准流和退出码",
            "观察入口在创建目录、打开会隐式创建文件的数据库连接",
            "只有项目点名的初始化命令拥有这项状态改变",
            "等待业务任务或实际生产进入项目定义的终态",
            "超时只结束本次等待并返回准确状态",
            "人工处理终态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CLI_TEXT)

    def test_completion_claim_consumes_the_original_plan_and_cli_evidence(self) -> None:
        for fragment in (
            "实施计划或用户确认的命令面必须转换成完成账本",
            "计划承诺与稳定发现 ID",
            "CLI 边界测试的实际唯一身份",
            "让实际输出通过对应公开 Schema",
            "service 单元测试只证明下层",
            "替身通过不能写成真实服务已经可用",
            "总测试数、完整套件名称或相邻 service 测试通过",
            "只有每项计划承诺都有合法终态，才能回答“都做完了”",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CLI_TEXT)


if __name__ == "__main__":
    unittest.main()
