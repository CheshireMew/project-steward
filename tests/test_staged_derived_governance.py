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

    def test_continuous_high_cost_work_forecasts_wall_clock_before_start(
        self,
    ) -> None:
        forecast = STAGED_TEXT.index("连续高成本工作先说明预计时间")
        execution = STAGED_TEXT.index("自动执行仍逐阶段生成成果")
        self.assertLess(forecast, execution)

        for fragment in (
            "用户已经授权连续自动执行，且完整生产与验证明显昂贵时",
            "在开始第一个昂贵动作前给出预计墙钟时间范围、关键路径、估算依据和主要不确定性",
            "不能把各阶段简单相加而忽略并行关系",
            "总耗时仍未知",
            "验证阶段的选择、耗时证据和重跑范围由 `ci-execution-governance.md` 负责",
            "立即更新预计范围并说明原估算中的哪项事实失效",
            "普通波动没有改变这些事实时不反复改口",
            "不能等到用户追问后才解释工作为何扩张",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)

        self.assertIn(
            "普通低成本、确定性、一步完成且没有实质用户选择的工作不增加阶段确认",
            STAGED_TEXT,
        )

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
    def test_multiple_artifacts_choose_one_explicit_evolution_contract(
        self,
    ) -> None:
        ordered = (
            "多份产物先选择演化合同",
            "权威产物及其稳定身份",
            "允许回流",
            "向前留档",
            "维护活真源",
            "三种关系没有全局默认",
        )
        positions = [DERIVED_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "独立事实、派生结果还是不可变历史",
            "重要理由由哪个真源保留",
            "不能按目录序号、修改时间或最近出现文件猜测",
            "不能在整体重写时丢失",
            "不增加模式字段、状态文件、目录层级、工作流引擎或人工门槛",
            "同一结果由多份规格、计划、任务或研究产物表达",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DERIVED_TEXT + MAIN_TEXT)

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

    def test_equivalent_state_representations_share_one_canonical_projection(
        self,
    ) -> None:
        ordered = (
            "先判断集合顺序是否属于业务语义",
            "顺序本身必须进入权威状态、版本和持久表示",
            "按稳定语义身份生成确定顺序",
            "缓存键、工作单元切分和最终装配共同消费这份投影",
        )
        positions = [DERIVED_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "实时内存、持久化重开、网络副本或迁移结果",
            "同一语义状态必须在进入缓存前得到相同规范投影和内容身份",
            "不能让缓存键、工作单元切分或最终装配各自排序、补默认值或猜顺序",
            "分别从实时状态生产者和持久化重开生产者",
            "真正有语义的换序才改变缓存身份",
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

    def test_selection_constraints_precede_scoring_and_refill(self) -> None:
        owner = DERIVED_TEXT.split(
            "### 选择器先冻结约束层级",
            1,
        )[1].split("## 8. 为重复 Agent 工作提供紧凑自动化边界", 1)[0]
        ordered = (
            "候选资格与拒绝原因",
            "硬约束、作用范围与显式例外",
            "软评分、排序、多样性与轮换",
            "请求数量语义：最大值 / 目标值 / 最小值",
            "补位或 fallback 允许放宽的软偏好",
            "最终 selected / deferred / rejected 及原因",
        )
        positions = [owner.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "资格和硬约束先过滤",
            "软评分只给仍合格的候选排序",
            "最大值是上界",
            "不能用补位绕过资格、排除项、类别硬上限或其它硬约束",
            "只能放宽已经列出的软偏好",
            "候选高度集中在同一类别、候选稀疏",
            "正式选择入口取得 selected、deferred 和 rejected 身份及原因",
        ):
            with self.subTest(owner_fragment=fragment):
                self.assertIn(fragment, owner)

        prevention_route = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理",
            1,
        )[0]
        remediation_route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        for fragment, route in (
            ("候选资格、配额、补位", prevention_route),
            ("候选硬约束被补位绕过", remediation_route),
        ):
            with self.subTest(route_fragment=fragment):
                self.assertIn(fragment, route)

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
