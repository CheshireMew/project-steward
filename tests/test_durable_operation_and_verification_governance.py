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
            "仍可能取消、失败、崩溃恢复或跨重启继续交付结果",
            "失败后无需追踪且不会留下外部结果的瞬时操作不使用本方法",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

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

    def test_conflicted_rebinding_uses_a_strict_plan_and_commit_boundary(
        self,
    ) -> None:
        ordered = (
            "`plan` 只读地重新取得源、目标和受影响记录的准确身份与当前版本",
            "覆盖整份计划的不可变摘要",
            "`commit` 必须同时收到原计划摘要和每一项冲突的明确决定",
            "任何写入前再次读取源、目标和受影响记录",
            "任一对象漂移就拒绝整份计划并重新生成",
            "才越过操作接受点",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "无冲突的瞬时内存修改不使用这套流程",
            "不得提供 `allow_conflicts`、尽力而为或隐式偏好",
            "不能只重算发生变化的局部后继续使用旧摘要",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

    def test_execution_plan_and_progress_have_stable_semantics(self) -> None:
        for fragment in (
            "固化为不可变执行计划",
            "只包含会改变结果的内容相关修订或指纹",
            "不得在真正执行时重新读取已经可能变化的全局设置",
            "不参与结果的派生状态不能让计划失效",
            "整体进度属于一个执行批次",
            "在该批次内只能单调前进",
            "阶段进度属于带稳定身份的当前步骤",
            "不能把已有整体进度覆盖回零",
            "显式重试创建新的执行批次和自己的进度序列",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

        ordered = (
            "固化为不可变执行计划",
            "执行前仍要重新取得当前输入",
            "进度是执行批次对这份计划的投影",
            "成功、失败、取消、冲突和中断仍只由唯一终态决定",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

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

        self.assertIn("两个独立调度观察者", DURABLE_TEXT)
        self.assertIn("不重放结果不确定的业务生产者", DURABLE_TEXT)

    def test_result_sets_and_run_evidence_have_one_retention_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "完整结果集合一起发布或撤回",
            "全部成员共享同一操作身份",
            "整个集合保持未决或失败",
            "验证运行证据的保留生命周期",
            "运行开始前，在受控证据根内先写入由工具拥有的清单",
            "保留全部失败与中断运行",
            "每个明确类别只保留最近一次完整成功",
            "更新的成功终态和完整证据已经持久提交",
            "不得触碰仍在运行、状态未知、缺少工具所有权标记",
            "清理失败要作为独立保留错误",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

        ordered = (
            "先写入由工具拥有的清单",
            "`running` 状态",
            "正式生产者结束",
            "成功、失败或中断",
            "执行保留选择",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("测试、性能、审计和真实用户链", DURABLE_TEXT)

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

    def test_semantic_mutations_and_sequential_batches_use_committed_state(
        self,
    ) -> None:
        for fragment in (
            "语义记录修改与连续决策批次使用已提交状态",
            "来源、证据、权威性、资格和关系",
            "同一次原子提交更新",
            "固定计划批次 / 连续决策批次",
            "后一步必须消费提交边界返回的新版本与正式结果",
            "不能在整个循环中反复使用同一份初始快照",
            "不能由消费端手写更新后的来源、证据或关系",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "记录仍存在但派生消费者将其排除",
            "第一处错误就在修改生产者与原子提交边界",
            "错误在批处理器的状态推进边界",
            "不能手写一份语义已经对齐的对象绕过错误边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_runtime_authority_precedes_recovery_and_scheduling(self) -> None:
        ordered = (
            "创建不触发持久状态变化的进程外壳",
            "竞争并取得权威端点或服务租约",
            "确认本进程是唯一活动实例",
            "初始化状态服务、恢复任务和启动调度",
            "接受客户端并产生新的状态变化",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "唯一运行权必须先于任何会改变持久状态的初始化",
            "竞争失败的进程只能关闭自己为竞争创建的端点、句柄和内存对象",
            "服务 `start` 必须幂等",
            "任务状态、重试次数和调度游标不变",
            "两个独立进程同时竞争同一权威端点",
            "只有胜者执行一次恢复和调度",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)


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
