from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
STAGED_TEXT = (
    SKILL_ROOT / "references" / "staged-result-governance.md"
).read_text(encoding="utf-8")
DERIVED_TEXT = (
    SKILL_ROOT / "references" / "derived-artifact-governance.md"
).read_text(encoding="utf-8")


class StagedResultGovernanceTests(unittest.TestCase):
    def test_routes_are_directly_reachable_from_prevention_and_remediation(
        self,
    ) -> None:
        prevention = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理",
            1,
        )[0]
        remediation = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]

        for reference in (
            "references/staged-result-governance.md",
            "references/derived-artifact-governance.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, prevention)
                self.assertIn(reference, remediation)

    def test_stage_approval_binds_the_real_artifact_identity(self) -> None:
        for fragment in (
            "用户确认的是当时实际看见的成果身份",
            "确认提交时重新读取成果内容身份",
            "未确认阶段阻止下游昂贵生产者",
            "聊天回复、任务卡和界面标记只是这份账本的投影",
            "不能靠对话记忆猜测用户确认过什么",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)

    def test_stage_plan_is_driven_by_decision_propagation(self) -> None:
        decision = STAGED_TEXT.index("先从决定传播关系派生阶段")
        artifact = STAGED_TEXT.index("阶段成果必须是真实可观察结果")
        approval = STAGED_TEXT.index("确认绑定准确成果")
        invalidation = STAGED_TEXT.index("用依赖图精确传播失效")
        self.assertLess(decision, artifact)
        self.assertLess(artifact, approval)
        self.assertLess(approval, invalidation)

        for fragment in (
            "大型研究报告可以是",
            "界面重建可以是",
            "阶段数量由独立决定决定",
            "用户只改局部事实时，不把无关阶段重新打开",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)

    def test_full_automation_is_explicit_and_does_not_expand_authority(
        self,
    ) -> None:
        for fragment in (
            "明确要求连续自动完成",
            "不在每个阶段等待新的用户回复",
            "需要新增下载、安装、删除、发布、外部写入",
            "不能把用户曾经说过“继续”",
            "不能在用户明确授权全自动后又机械要求重复确认同一方案",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)

    def test_stage_validation_uses_real_producers_and_distinct_surfaces(
        self,
    ) -> None:
        for fragment in (
            "大型研究报告任务",
            "另一个代码生成任务",
            "正式生产者生成成果",
            "测试不能直接把阶段状态设为已确认",
            "不能手写一份成果摘要冒充正式生产者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)


class DerivedArtifactGovernanceTests(unittest.TestCase):
    def test_cache_key_uses_the_consumed_projection(self) -> None:
        for fragment in (
            "生产者实际消费的规范输入投影",
            "生产者语义版本",
            "正式输出规格",
            "只有能够证明进入生产者并改变输出的事实才加入键",
            "审核备注、诊断标签、展示顺序、输出目录、文件名",
            "先由唯一生产边界生成实际消费的规范投影",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_target_size_is_separate_from_the_safety_limit(self) -> None:
        for fragment in (
            "目标单元与安全上限是两种约束",
            "目标单元大小及其性能依据",
            "最大连续单元及其硬限制来源",
            "允许切分的中性边界",
            "不能把目标大小当成必须命中的硬切点",
            "不产生孤立单元",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_local_change_preserves_unaffected_units_and_shared_resources(
        self,
    ) -> None:
        for fragment in (
            "局部单元变化只使该单元、读取它的相邻接缝和必要装配失效",
            "共享连续资源只生产一次",
            "共享不等于全局失效",
            "同计划重跑",
            "局部语义变化",
            "非语义变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_resource_inventory_expands_only_after_utilization_is_proved(
        self,
    ) -> None:
        utilization = DERIVED_TEXT.index("先检查调度利用，再增加资源")
        conclusion = DERIVED_TEXT.index("才判定资源确实不足")
        self.assertLess(utilization, conclusion)

        for fragment in (
            "实际可达",
            "选择次数与连续重复",
            "根因是利用策略而不是资源库存",
            "先修复资格、轮换、多样性或连续重复约束",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_agent_round_trips_are_reduced_at_the_public_boundary(self) -> None:
        for fragment in (
            "结构化快照",
            "原子批处理",
            "可观察长任务",
            "机器可读能力",
            "不复制领域状态、缓存算法、阶段判断、任务恢复或错误解释",
            "把 Agent 读状态与作决定的时间、工具调用往返",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_validation_does_not_fake_cache_or_producer_results(self) -> None:
        for fragment in (
            "代码生成任务只改变一个模块的规范输入",
            "资源池利用",
            "Agent 编排",
            "不能直接填充缓存、伪造命中报告、手写下游单元",
            "缓存报告由真实生产者和缓存边界生成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT)

    def test_learned_method_does_not_retain_project_specific_corrections(
        self,
    ) -> None:
        for forbidden in (
            "巴菲特",
            "谷歌",
            "夜希",
            "MediaFlow",
            "224px",
            "384×384",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, STAGED_TEXT + DERIVED_TEXT)

    def test_main_skill_budget_and_reference_identity_remain_valid(self) -> None:
        direct_references = set(
            re.findall(r"references/[A-Za-z0-9._/-]+\.md", MAIN_TEXT)
        )
        self.assertLessEqual(len(MAIN_TEXT.splitlines()), 220)
        self.assertLessEqual(len(MAIN_TEXT), 14_000)
        self.assertIn("references/staged-result-governance.md", direct_references)
        self.assertIn("references/derived-artifact-governance.md", direct_references)

        for reference in direct_references:
            with self.subTest(reference=reference):
                self.assertTrue((SKILL_ROOT / reference).is_file())


if __name__ == "__main__":
    unittest.main()
