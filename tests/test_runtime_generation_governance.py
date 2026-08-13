from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
RUNTIME_TEXT = (
    SKILL_ROOT / "references" / "runtime-generation-governance.md"
).read_text(encoding="utf-8")


class RuntimeGenerationGovernanceTests(unittest.TestCase):
    def test_runtime_generation_has_direct_prevention_and_remediation_routes(
        self,
    ) -> None:
        route = "references/runtime-generation-governance.md"
        prevention = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        remediation = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]

        self.assertIn(route, prevention)
        self.assertIn(route, remediation)
        self.assertNotIn("references/", RUNTIME_TEXT)

    def test_actual_graph_diff_owns_the_affected_service_set(self) -> None:
        for fragment in (
            "不能根据 patch 的字段名猜测影响范围",
            "旧图描述与候选图描述",
            "真正会改变身份、生命周期、存储根或并发所有权",
            "最终服务图构造规则",
            "不再维护另一份“哪些配置字段重要”的名单",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)

    def test_each_operation_uses_one_immutable_generation(self) -> None:
        ordered = (
            "从唯一运行时所有者取得代次与完整服务上下文",
            "在该上下文内完成读取、执行、写入和结果发布",
            "释放该代次租约",
        )
        positions = [RUNTIME_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "一次操作中反复查询“当前服务”",
            "前半段旧代与后半段新代拼在一起",
            "一次记忆操作不能在旧根读取、切换后写入新根",
            "等待超时只说明旧代尚未排空",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)

    def test_hot_switch_has_one_commit_and_truthful_rollback(self) -> None:
        ordered = (
            "构造候选配置、候选图与不对外服务的候选对象",
            "原子持久化候选配置；失败则旧服务完全不动",
            "请求受影响旧任务停止并等待租约排空",
            "在一个内存提交点同时发布候选配置、服务图和代次",
            "正式消费者读取新代，界面报告成功",
        )
        positions = [RUNTIME_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "仍先让运行时权威状态明确保持旧代",
            "磁盘候选内容与活动旧代不一致",
            "不能静默保留半套新服务",
            "旧对象只能服务提交前已经持有的明确租约",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)

    def test_physical_roots_and_desktop_mutations_have_explicit_boundaries(
        self,
    ) -> None:
        for fragment in (
            "物理根变化默认是启动边界",
            "任务历史、索引、缓存、恢复记录和后台调度器",
            "重启后生效",
            "一个后台串行队列",
            "成功只在新代已经提交且正式消费者能够读取后发布",
            "失败保留用户仍未提交的脏字段和可重试意图",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)

    def test_coalescing_preserves_every_accepted_completion_obligation(
        self,
    ) -> None:
        for fragment in (
            "只能合并物理执行和最终补丁",
            "不能合并已经对调用者成立的完成责任",
            "每个已受理意图保留稳定身份和自己的完成接收者",
            "分别取得且只取得一次完成、失败、被替代或取消终态",
            "不能靠移除队列项、丢弃回调或永久保留忙碌状态表达",
            "先停止接收新修改，再排空全部已受理意图及其完成投递",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)

        acceptance = RUNTIME_TEXT.split("## 6. 真实验收", 1)[1]
        for fragment in (
            "共享一次物理提交但保留各自身份和完成接收者",
            "每个已受理意图都恰好取得一个可消费终态",
            "忙碌计数也能归零",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, acceptance)

    def test_acceptance_uses_real_graphs_leases_and_consumers(self) -> None:
        for fragment in (
            "用受控屏障让真实操作在旧代完成读取后暂停",
            "旧任务、旧 provider 和旧服务图从未中断",
            "再注入一次磁盘回滚失败",
            "事件循环仍能处理一次无关交互",
            "候选图必须由正式配置和服务图生产者生成",
            "最终由当前消费者读取本次提交的代次和结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, RUNTIME_TEXT)



if __name__ == "__main__":
    unittest.main()
