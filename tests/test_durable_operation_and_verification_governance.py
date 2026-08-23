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
STRUCTURED_TEXT = read("references/structured-data-boundary.md")
DESKTOP_TEXT = read("references/desktop-app-governance.md")
IMPLEMENTATION_TEXT = read("references/implementation-review.md")
AGENT_TEXT = read("agents/openai.yaml")

PREVENTION_TEXT += "".join(
    read(f"references/{name}")
    for name in (
        "change-prevention-state-and-capability.md",
        "change-prevention-delivery-boundaries.md",
        "change-prevention-verification.md",
    )
)
REMEDIATION_TEXT += read("references/root-cause-verification-and-closure.md")
IMPLEMENTATION_TEXT += read("references/implementation-review-visual-evidence.md")


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

    def test_error_after_physical_effect_is_reconciled_once(self) -> None:
        ordered = (
            "生产者返回错误、连接中断或确认超时",
            "以操作身份、执行前基线和正式目标重新读取物理事实",
            "从权威事实重建同一结果合同",
            "交给既有的唯一结果接收边界并立即结束当前完成路径",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能单独证明物理操作没有发生",
            "可读取的成功后置条件、确定未发生的证据和冲突条件",
            "生产者只执行一次且账本只有一个成功终态",
            "前者得到唯一无产物失败，后者保持未决或冲突",
            "不得继续落入通用错误处理",
            "显式重试仍创建新的执行批次",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

    def test_all_completion_paths_validate_results_inside_lifecycle_owner(
        self,
    ) -> None:
        ordered = (
            "列出实际存在的完成路径矩阵",
            "所有正式生产者的返回值都先进入同一个结果接收边界",
            "结果校验必须位于当前操作生命周期所有者的异常边界内",
            "在正式生产者返回后、接受成功或写入终态之前执行",
            "校验失败形成稳定的结果合同失败终态",
            "同一执行器提交一个合法操作并证明它正常完成",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "即时同步、队列 worker、后台线程或进程、延期回调或聚合、显式重试和重启恢复",
            "不为形式完整补造分支",
            "不能逃逸并结束 worker 主循环",
            "不能让操作留在 `running` 或等价非终态",
            "不得分别复制校验与错误映射",
            "正式任务入口注册一个受控但真实的结果生产者",
            "由账本等待唯一失败终态",
            "不能证明结果合同、持久终态和执行器存活已经共同收口",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

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

    def test_planned_scope_and_actual_change_facts_are_distinct(self) -> None:
        for fragment in (
            "计划范围与实际变更事实分离",
            "用户意图与授权范围",
            "冲突集合",
            "观察集合",
            "实际变更集",
            "前三类是执行输入，不能直接成为已经发生的事实",
            "操作合法但没有改变权威事实时，实际变更集为空",
            "观察集合必须对合同内副作用闭合",
            "不能共用一个笼统的 `affected` 列表",
            "只消费实际变更集及其提交版本",
            "一次带关联副作用的真实修改",
            "一次合法无变化操作",
            "一次提交前冲突拒绝",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "事件或版本前进但权威事实没有对应变化",
            "提交前后权威状态",
            "计划目标或冲突集合直接被写成事件事实",
            "观察集合遗漏移动、拆分、重排等合同内副作用",
            "本路径只定位第一次混淆发生的位置",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        remediation_route = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        self.assertIn("计划影响范围误当成实际变更事实", remediation_route)
        self.assertIn("references/change-prevention.md", remediation_route)

    def test_observation_scope_is_the_smallest_provably_closed_set(self) -> None:
        for fragment in (
            "能够证明覆盖全部合同内副作用的最小稳定身份集合",
            "形成隐藏的性能耦合",
            "全聚合观察可以作为诊断基线",
            "沿规划、权威读取、提交、实际变更计算",
            "不能靠漏观察、跳过事件或放宽门槛换取速度",
            "同时证明最小闭合范围、正确持久化、下游消费和代表性耗时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_reads_declare_consistency_and_mutations_return_closed_projections(
        self,
    ) -> None:
        ordered = (
            "读取一致性与变更后置投影显式化",
            "事务快照、可取消时间点扫描或活动投影",
            "事务快照不得由独立查询拼接",
            "状态变更在同一提交边界返回可直接消费的版本化后置投影",
            "完整快照，或覆盖闭合且应用规则明确的补丁",
            "不能只返回局部状态",
            "闭合补丁足够时不强制全量快照",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "每个结果都带权威身份或版本",
            "从正式状态变更直接消费同一提交返回的完整快照或闭合补丁",
            "必须补查兄弟接口或拼接旧缓存",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_generation_identity_and_first_use_sync_identity_are_not_reused(
        self,
    ) -> None:
        for fragment in (
            "generation 的分配身份在旧请求、取消、分片或回调仍可能到达时不得复用",
            "清理当前记录只结束可发现性，不重置或回绕分配器",
            "只有旧身份已不可能再到达",
            "清理记录并启动 B，再投递迟到的 A 请求、取消、分片和回调",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "同步命名空间必须直接由规范化资源身份和合同版本确定",
            "在任何参与者创建侧边锁文件、状态目录或业务副作用之前取得",
            "不能把“侧边锁文件已经存在”作为其它进程加入同一同步边界的前提",
            "只读参与者也不能为了协调创建业务状态",
            "不存在任何侧边锁文件的状态启动读写进程",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

    def test_adapters_bind_explicit_inputs_before_defaults(self) -> None:
        ordered = (
            "稳定字段身份及其全部显式输入来源",
            "显式输入完成绑定后的规范命令",
            "只对仍缺失字段生效的默认值及注入位置",
            "消费规范命令的规划器、提交边界和最终结果",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "两个来源同时提供不等价值时在适配器边界明确拒绝",
            "在显式输入绑定完成前不得写入规范字段",
            "省略与显式空值不能由消费者事后猜测",
            "默认值只补充仍然缺失的字段",
            "仅位置参数、仅命名或正文参数、合法显式空值",
            "直接构造已经正确的命令对象只能证明下游",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_structured_message_capacity_preserves_atomic_replay(self) -> None:
        prevention_route = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        remediation_route = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        for route in (prevention_route, remediation_route):
            with self.subTest(route=route[:40]):
                self.assertIn("references/structured-data-boundary.md", route)
                self.assertIn("原子分片", route)
                self.assertIn("重放游标", route)

        for fragment in (
            "逻辑消息容量必须穿过完整传输链",
            "最大合法逻辑消息",
            "每一跳都要在明确余量内承载最大合法消息",
            "版本化分片协议",
            "稳定逻辑消息身份",
            "持久重放游标只在完整逻辑消息通过重组",
            "不能让同一条永久不可交付记录把游标卡住",
            "接近上限和最大合法规模的真实消息",
            "从真实游标重放同一消息",
            "消费端手写大对象",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STRUCTURED_TEXT)

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

    def test_discoverable_sessions_use_shared_admission_leases(self) -> None:
        for route_fragment in (
            "常驻有状态服务中可发现会话与共享资源",
            "会话准入与释放竞争",
        ):
            with self.subTest(route_fragment=route_fragment):
                self.assertIn(route_fragment, SKILL_TEXT)

        ordered = (
            "同一原子边界内验证对象仍可发现",
            "增加活动使用者并返回共享准入租约",
            "移出可发现集合并标记为 `closing`",
            "等待已经发放的共享准入租约归零",
            "取得对象的独占写入或关闭权",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "查表后返回裸对象，再由调用者晚些时候加锁",
            "派生工作必须在原命令释放前取得自己的租约",
            "不能用一把覆盖会话整个生命期的排他锁",
            "按实际依赖的资源域分类",
            "读取项目状态的工作必须在项目资源释放前排空",
            "状态保持 `closing` 且所有权未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

    def test_execution_topology_changes_reprove_shared_state_ownership(
        self,
    ) -> None:
        ordered = (
            "旧的“天然串行”结论立即失效",
            "重新建立执行拓扑与共享状态矩阵",
            "覆盖整个在途使用区间",
            "用受控屏障让它们在共享边界前形成重叠",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能证明仲裁器自身的可变状态",
            "操作身份、generation 和终态隔离继续负责关联结果，不能冒充执行互斥",
            "共享服务或原生资源的最大在途进入数符合合同",
            "把测试改成串行，不能证明执行拓扑已经安全",
            "内部已经创建的框架资源和子对象",
            "计时器、读取器、套接字、订阅、回调和句柄",
            "会随所有者正式迁移",
            "在原上下文停止并在目标上下文重建",
            "跨上下文启动、停止或销毁警告属于失败",
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

    def test_run_evidence_consumers_bind_explicit_run_identities(self) -> None:
        ordered = (
            "每次调用返回的明确运行身份",
            "类别 + 运行身份 + 工具所有权标记",
            "不能按目录修改时间、排序后的“最新目录”",
            "当前调用显式传入的运行身份集合",
            "不能用未匹配的旧运行补位",
            "聚合报告是派生证据",
            "列出完整输入运行身份集合",
        )
        positions = [DURABLE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "保留策略移动目录不能改变证据身份",
            "聚合保持不完整或未知",
            "目录修改时间或归档位置变化不会换入旧报告",
            "运行证据的身份、显式消费集合、聚合、保留、轮换和清理错误",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_TEXT)

    def test_public_identity_exposes_the_new_capability(self) -> None:

        self.assertIn(
            "durable operations",
            SKILL_TEXT,
        )
        self.assertIn(
            "治理项目变更、根因、README、仓库发布与可迁移经验",
            AGENT_TEXT,
        )
        self.assertIn(
            "一次用户意图、一次物理执行和一个最终可见结果",
            DURABLE_TEXT,
        )
        self.assertNotIn("持久意图、物理事实、唯一终态和可见确认", AGENT_TEXT)


if __name__ == "__main__":
    unittest.main()
