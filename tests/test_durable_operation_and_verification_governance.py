from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


SKILL_TEXT = read("SKILL.md")
DURABLE_TEXT = read("references/durable-operation-governance.md")
PREVENTION_TEXT = read("references/change-prevention.md")
REMEDIATION_TEXT = read("references/root-cause-remediation.md")
DESKTOP_TEXT = read("references/desktop-app-governance.md")
IMPLEMENTATION_TEXT = read("references/implementation-review.md")
README_TEXT = read("README.md")
AGENT_TEXT = read("agents/openai.yaml")


class DurableOperationAndVerificationGovernanceTests(unittest.TestCase):
    def test_durable_operation_has_a_direct_conditional_route(self) -> None:
        reference = (
            SKILL_ROOT / "references" / "durable-operation-governance.md"
        )
        self.assertTrue(reference.is_file())
        self.assertIn(
            "references/durable-operation-governance.md",
            SKILL_TEXT,
        )
        for fragment in (
            "导出、复制、保存、下载、同步、最终化",
            "随后仍可能取消、失败、留下外部产物或需要跨重启交付",
            "失败后无需追踪、不会留下外部结果的瞬时操作不建立事务",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

    def test_acceptance_physical_truth_and_visible_ack_are_ordered(self) -> None:
        for fragment in (
            "持久化 pending",
            "重新读取并校验当前输入",
            "物理结果完成或证据保全",
            "持久化唯一终态",
            "用户实际看见结果",
            "明确确认已交付",
            "物理命名空间或存储根",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

        self.assertLess(
            DURABLE_TEXT.index("持久化 pending"),
            DURABLE_TEXT.index("重新读取并校验当前输入"),
        )
        self.assertLess(
            DURABLE_TEXT.index("物理结果完成或证据保全"),
            DURABLE_TEXT.index("持久化唯一终态"),
        )

    def test_all_physical_effects_and_one_terminal_outcome_have_one_owner(
        self,
    ) -> None:
        for fragment in (
            "`pending` 还必须早于本次操作产生的任何外部可观察副作用",
            "创建父目录或临时目录",
            "都属于事务的物理执行",
            "一个唯一所有者接收显式结果并写入一次终态",
            "不能先记录失败再由兜底路径追加成功",
            "账本终态、结构化完成事件和操作日志必须消费同一结果身份",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

        self.assertLess(
            DURABLE_TEXT.index("持久化 pending"),
            DURABLE_TEXT.index("创建父目录或临时目录"),
        )
        self.assertIn("同一操作先失败后成功", DURABLE_TEXT)
        self.assertIn("只产生一个账本、结构化事件和日志", README_TEXT)

    def test_tests_consume_producer_owned_truth(self) -> None:
        for fragment in (
            "动作前的事务身份集合",
            "从新事务读取实际路径",
            "不要建立第二个时钟",
            "不得根据成功次数预测名称",
            "从当前活动树重新取得元素",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    DURABLE_TEXT + PREVENTION_TEXT + REMEDIATION_TEXT,
                )

    def test_automatic_occurrence_and_execution_attempt_are_distinct(self) -> None:
        for fragment in (
            "队列、调度器、重试器或多个观察者",
            "稳定发生身份",
            "同一事务中写入发生记录、创建任务并推进调度游标",
            "发生身份回答“这是不是同一次触发”",
            "不得自动重放同一批次",
            "显式重试产生可区分的新批次",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT + DURABLE_TEXT + README_TEXT)

        self.assertIn("两个独立调度观察者", DURABLE_TEXT)
        self.assertIn("一个原子边界内写入发生记录、任务和调度进度", README_TEXT)
        self.assertIn("不重放结果不确定的业务生产者", DURABLE_TEXT)

    def test_async_ownership_preserves_authoritative_state(self) -> None:
        for fragment in (
            "每个线程、任务、事件读取器和订阅分发器",
            "可等待的完成信号",
            "权威状态和致命错误使用无损路径",
            "高频遥测可以使用有界、合并或丢旧值的路径",
            "释放生产者、文件句柄、设备或远程会话失败时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    DURABLE_TEXT + REMEDIATION_TEXT,
                )

    def test_archive_preservation_is_byte_exact_and_inactive(self) -> None:
        for fragment in (
            "源文件 → 归档文件",
            "字节数与哈希或直接逐字节比较",
            "先重命名再继续修改同一文件不等于保存了原内容",
            "活动入口不再读取归档",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_real_acceptance_uses_low_disruption_inputs(self) -> None:
        for fragment in (
            "最低扰动输入",
            "静音或不可听输入",
            "不得用持续刺耳的测试音",
            "立即停止本次启动的准确生产者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    PREVENTION_TEXT + DESKTOP_TEXT + IMPLEMENTATION_TEXT,
                )

    def test_visible_actions_and_fresh_evidence_are_required(self) -> None:
        for fragment in (
            "行动区必须保持可达",
            "重新查询当前元素",
            "不能拼接修改前的完整报告与修改后的局部截图",
            "测试驱动冻结后运行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_public_identity_exposes_the_new_capability(self) -> None:
        for fragment in (
            "## 持久操作与恢复",
            "不播放持续刺耳的测试音",
            "生产者真正新增的事务和实际路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

        self.assertIn(
            "治理架构、持久操作、用户环境、仓库研究与发布链路",
            AGENT_TEXT,
        )
        self.assertIn(
            "一次用户意图、一次物理执行和一个最终可见结果",
            DURABLE_TEXT,
        )
        self.assertNotIn("持久意图、物理事实、唯一终态和可见确认", AGENT_TEXT)


if __name__ == "__main__":
    unittest.main()
