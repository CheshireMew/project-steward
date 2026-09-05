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

    def test_composite_artifact_tracks_acceptance_per_decision_unit(self) -> None:
        for fragment in (
            "物理容器，不自动等于一个用户决定",
            "为每个决策单元分别记录成果身份、正式消费者、检查证据和确认状态",
            "同一容器可以同时包含已确认、等待确认、已失效和失败的单元",
            "不能把其中一个单元的确认广播给全部内容",
            "每个必需决策单元都已经有可判断成果且状态得到解决",
            "随后才把局部状态聚合为整体确认",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STAGED_TEXT)

    def test_unreviewed_valid_unit_is_inspected_before_reproduction(self) -> None:
        inspection = STAGED_TEXT.index("先让正式消费者打开准确的现有单元")
        production = STAGED_TEXT.index("才启动对应生产者")
        self.assertLess(inspection, production)

        for fragment in (
            "等待确认或尚未审查是认识状态",
            "不等于成果失败、未制作、未完成或必须重新生成",
            "并运行适用的轻量检查",
            "输入或目标合同变化",
            "依赖图已经传播到该单元的真实失效",
            "正式检查发现具体失败",
            "用户明确要求重做",
            "仅仅缺少确认不能创建新版本",
            "只使该单元及其真实下游失效",
            "其它身份和证据仍成立的单元继续保留",
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

    def test_stage_quality_separates_blockers_repairs_and_preferences(
        self,
    ) -> None:
        section = STAGED_TEXT.split(
            "### 推进前区分阻断、可修复缺陷与理想偏好",
            1,
        )[1].split("## 4. 确认绑定准确成果", 1)[0]
        ordered = (
            "必需不变量或阻断项",
            "可修复缺陷",
            "理想偏好",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不能在验收时悄悄变成硬拒绝条件",
            "稳定问题身份、证据、影响的下游、修复所有者与计划",
            "必须在最终交付前关闭的时点",
            "不能把“留给后期修复”报告成“已经修复”",
            "下一阶段无法可靠消费",
            "污染昂贵或不可逆的下游",
            "不能因为结果未达到示例中的最佳状态就全量重做",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


class DerivedArtifactGovernanceTests(unittest.TestCase):
    def test_unit_completion_has_one_owner_on_existing_routes(self) -> None:
        heading = "### 单元完成必须核对产物来源"
        owners = [
            path.name for path in (SKILL_ROOT / "references").glob("*.md")
            if heading in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(owners, ["derived-artifact-governance.md"])
        graph = DERIVED_TEXT.split("## 3. 先建立语义派生图", 1)[1].split(
            "## 4. 缓存键只表达会改变产物的事实", 1
        )[0]
        self.assertEqual(graph.count(heading), 1)
        self.assertNotIn(heading, MAIN_TEXT)

        for start, end, trigger in (
            ("## 改动前预防", "## 根因治理", "涉及派生产物"),
            ("## 根因治理", "## 外部工具兼容性", "产物关系不明"),
        ):
            route = MAIN_TEXT.split(start, 1)[1].split(end, 1)[0]
            lines = [line for line in route.splitlines() if trigger in line]
            with self.subTest(route=start):
                self.assertEqual(len(lines), 1)
                self.assertIn("references/derived-artifact-governance.md", lines[0])

        entry = DERIVED_TEXT.split("## 1. 进入条件与主要失败", 1)[1].split(
            "## 2. 多份产物先选择演化合同", 1
        )[0]
        self.assertIn("多个步骤或语义单元输出同类型产物", entry)
        self.assertIn("恢复记录缺少可核对的产物归属", entry)
        self.assertIn("普通一次性、小型且没有复用或分段的派生结果不增加完整治理", entry)

    def test_unit_completion_binds_results_to_semantic_producers(self) -> None:
        contract = DERIVED_TEXT.split("### 单元完成必须核对产物来源", 1)[1].split(
            "## 4. 缓存键只表达会改变产物的事实", 1
        )[0]
        for detail in (
            "稳定单元身份、实际消费的规范输入、生产者及其语义版本、输出规格和结果内容身份",
            "正式完成边界逐项核对",
            "同一处理器的不同语义单元不能互相顶替",
            "同后缀、同类型、同路径或别的步骤已有文件",
            "来源由正式生产者在产出时记录",
            "持久化、去重、检查点和重开中保留",
            "共享产物通过显式依赖关系满足消费者输入",
            "不冒充消费者自己应生产的输出",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_unit_completion_preserves_valid_reuse_and_unknown_provenance(self) -> None:
        contract = DERIVED_TEXT.split("### 单元完成必须核对产物来源", 1)[1].split(
            "## 4. 缓存键只表达会改变产物的事实", 1
        )[0]
        for detail in (
            "复用记录引用原产物及本次被接受的依赖关系",
            "不把旧产物重标为本轮新产物",
            "合法缓存可以计入完成，不因未重新调用生产者而拒绝",
            "来源缺失、所属单元不匹配或结果不完整",
            "保留可恢复文件并标明缺失的完成证据",
            "不猜造来源，不把单元置为完成",
            "旧记录只可依据可核对的原始生产证据补齐",
            "`durable-operation-governance.md` 核对权限和副作用",
            "不能从来源未知推导出自动重跑",
            "不另建任务、缓存、恢复或归档系统",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_unit_completion_contract_reaches_publication_validation_and_output(
        self,
    ) -> None:
        publication = DERIVED_TEXT.split("## 9. 失效、装配与发布", 1)[1].split(
            "## 10. 真实验证矩阵", 1
        )[0]
        qualification = publication.index("每个完成入口先消费第 3 节的单元完成资格")
        release = publication.index("单元、接缝、共享资源和最终装配分别在完成校验后原子发布")
        self.assertLess(qualification, release)
        self.assertIn("正常完成、缓存命中与检查点恢复不能各用一套条件", publication)

        matrix = DERIVED_TEXT.split("## 10. 真实验证矩阵", 1)[1].split(
            "## 11. 输出合同", 1
        )[0]
        self.assertIn("只处理产物来源时核对单元完成资格", matrix)
        scenario = matrix.split("**单元完成资格**：", 1)[1].split("\n\n", 1)[0]
        for detail in (
            "第二单元未产生应有结果时仍不得完成",
            "同一处理器的两个语义单元不互相顶替",
            "来源完整的合法缓存", "旧记录缺少来源", "输入或生产版本已变化",
            "正式完成入口和最终消费者读到一致结果",
            "不能手写来源或直接把单元设为完成",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, scenario)
        output = DERIVED_TEXT.split("## 11. 输出合同", 1)[1]
        self.assertIn("逐单元完成证据、产物来源、合法复用关系与未满足原因：", output)

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

    def test_qualitative_review_has_one_editable_authority_and_finalizer(
        self,
    ) -> None:
        section = DERIVED_TEXT.split(
            "### 定性评审只有一份可编辑权威记录",
            1,
        )[1].split("## 3. 先建立语义派生图", 1)[0]
        for fragment in (
            "视觉、语义、质量或其它定性判断",
            "一份带成果身份、证据身份、评审者和决定版本的可编辑评审记录",
            "不能让多个文件分别拥有同一接受、拒绝、修复或完成事实",
            "不能靠人工双写保持一致",
            "一个确定性的收尾边界",
            "阶段问题和完成状态不冲突",
            "一次生成或同步全部机器可读镜像",
            "不得报告完成",
            "不能反向覆盖权威评审",
            "双重所有权会被拒绝",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

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

    def test_active_read_cache_tracks_authoritative_and_derived_freshness(
        self,
    ) -> None:
        section = DERIVED_TEXT.split(
            "### 活动读取缓存必须覆盖它实际返回的全部事实",
            1,
        )[1].split("## 5. 目标单元与安全上限", 1)[0]
        ordered = (
            "独立的版本或内容身份",
            "缓存键必须覆盖它实际返回的全部依赖身份",
            "按实际变化精确失效",
            "推进派生版本或失效受影响缓存",
            "当前界面读取新派生身份",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "权威内容修订不变",
            "持久内容不变量只比较权威字段",
            "派生就绪、路径和质量由自己的变化与重开测试负责",
            "不能用整个对象相等把两类职责混为一谈",
            "关闭重开只能帮助诊断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

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

    def test_optional_segmentation_must_earn_its_first_run_cost(self) -> None:
        ordered = (
            "强制切分",
            "可选切分",
            "每单元固定启动成本",
            "短输入首次冷运行",
            "代表性长输入首次冷运行",
            "同计划暖缓存重跑",
        )
        positions = [DERIVED_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "短输入没有并行或复用收益时可以保持一个单元",
            "暖缓存胜出不能单独证明首次运行的分段策略正确",
            "记录单单元或多单元的原因、阈值来源和本轮实际固定开销",
            "短输入首次单单元与多单元",
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

    def test_repeatable_generation_has_one_owner_and_a_root_cause_route(self):
        heading = "### 重复生成隔离输入、当前产物与旧产物"
        owners = [
            path.name for path in (SKILL_ROOT / "references").glob("*.md")
            if heading in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(owners, ["derived-artifact-governance.md"])
        route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        lines = [line for line in route.splitlines() if "旧产物回流或自引用" in line]
        self.assertEqual(len(lines), 1)
        self.assertIn("references/derived-artifact-governance.md", lines[0])
        self.assertNotIn(heading, MAIN_TEXT)

    def test_repeatable_generation_preserves_input_and_file_ownership(self):
        contract = DERIVED_TEXT.split(
            "### 重复生成隔离输入、当前产物与旧产物", 1
        )[1].split("## 10. 真实验证矩阵", 1)[0]
        for detail in (
            "权威输入、本轮有效产物、描述产物的生成元数据",
            "不得参与一个会重写自身的输入摘要循环",
            "本轮正式入口清单或等价生产结果",
            "构建、交付检查和服务消费者共享这份身份与选择规则",
            "没有删除授权不删除", "未知文件和用户拥有文件",
            "production-storage-governance.md", "repository-directory-governance.md",
            "只追加不可变历史", "普通一次性输出不因此增加",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_repeatable_generation_acceptance_uses_one_root_without_manual_cleanup(self):
        contract = DERIVED_TEXT.split(
            "### 重复生成隔离输入、当前产物与旧产物", 1
        )[1].split("## 10. 真实验证矩阵", 1)[0]
        steps = ("先首次生成", "再以相同输入重复生成", "最后修改一项真实输入")
        positions = [contract.index(step) for step in steps]
        self.assertEqual(positions, sorted(positions))
        matrix = DERIVED_TEXT.split("## 10. 真实验证矩阵", 1)[1].split(
            "## 11. 输出合同", 1
        )[0]
        self.assertIn("只处理重复输出时执行上一节的同根验收", matrix)
        self.assertIn("原合同已经要求的检查继续保留", matrix)
        for detail in (
            "同一正式入口和同一输出根", "先首次生成",
            "再以相同输入重复生成", "最后修改一项真实输入",
            "每次选中的输入、当前清单、摘要和消费者结果",
            "不得在两轮之间手工清场", "每次换空目录",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

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
