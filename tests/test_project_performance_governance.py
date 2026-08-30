from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
AUDIT_TEXT = (SKILL_ROOT / "references" / "project-audit.md").read_text(
    encoding="utf-8"
)
PERFORMANCE_TEXT = (
    SKILL_ROOT / "references" / "project-performance-governance.md"
).read_text(encoding="utf-8")


class ProjectPerformanceGovernanceTests(unittest.TestCase):
    def test_performance_remediation_consumes_owner_before_candidate_freeze(
        self,
    ) -> None:
        section = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        self.assertEqual(
            section.count("`references/project-performance-governance.md`"), 1
        )
        self.assertIn("性能、资源或规模项", section)
        self.assertIn("再按下文生成适用矩阵", PERFORMANCE_TEXT)
        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        ordered = (
            "直接因果检查",
            "二次性能复审",
            "冻结准确候选",
        )
        start = closure.index("先完成直接因果检查")
        positions = [closure.index(fragment, start) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("同一正式入口、代表性输入和当前目标平台上的用户链证据", closure)

    def test_proactive_performance_changes_route_before_writing_without_scope_growth(
        self,
    ) -> None:
        prevention = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        route = "性能计划或提速：`references/project-performance-governance.md`"
        self.assertEqual(prevention.count(route), 1)
        self.assertLess(prevention.index(route), prevention.index("实施授权才修改"))
        contract = PERFORMANCE_TEXT.split("## 1. 先冻结性能合同和动作边界", 1)[1].split(
            "## 2. 建立阶段、规模和生命周期覆盖矩阵", 1
        )[0]
        for fragment in (
            "性能计划写入前先冻结基线、适用范围、正确性合同与收益判据",
            "缓存、预热、并行、增量处理或加速后端",
            "即使尚无缺陷也执行这一步",
            "局部改动只覆盖获准结果，不自动扩成全仓性能审计",
            "普通解释或只读计划在证据与方案交付后停止，不实施优化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, contract)

    def test_acceleration_claims_have_three_independent_evidence_layers(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        start = "准备宣称硬件加速、指定设备或零拷贝时"
        self.assertEqual(PERFORMANCE_TEXT.count(start), 1)
        evidence = measurement.split(start, 1)[1].split("验收门槛与性能评价分开记录", 1)[0]
        ordered = (
            "请求策略、实际后端和数据路径",
            "配置接受、能力协商成功或偏好硬件参数",
            "同一次操作的运行时回执、追踪或正式诊断接口",
            "数据路径从正式生产者追到消费者",
            "三层证据分别输出已证明、已否定或未知",
        )
        positions = [evidence.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "框架或加速接口名称不能替物理编码器、设备型号或厂商背书",
            "CPU 回读、上传、跨进程搬运",
            "硬件执行与零拷贝相互独立",
            "减少一次复制也不能证明全链零拷贝",
            "计划后端或早期硬件初始化替后续软件执行背书",
            "没有相关主张时不强制底层追踪",
            "不自行重编运行时、增加原生桥接或扩大验收",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, evidence)
        output = PERFORMANCE_TEXT.split("## 7. 输出与停止", 1)[1]
        self.assertIn("请求策略、实际后端与数据路径各自的证据和未知项", output)

    def test_comprehensive_audit_routes_one_performance_owner(self) -> None:
        section = AUDIT_TEXT.split("## 8. 审计性能、资源与规模", 1)[1].split(
            "## 9. 审计兼容性、安装与外部边界", 1
        )[0]
        self.assertIn("固定读取 `project-performance-governance.md`", section)
        self.assertIn("唯一负责性能覆盖矩阵", section)
        self.assertIn("hard-to-reproduce-diagnostics.md", section)
        self.assertIn("唯一负责阶段、竞争解释、工作放大和资源趋势", section)

    def test_performance_matrix_covers_stage_scale_and_lifecycle(self) -> None:
        for fragment in (
            "新鲜进程、冷缓存、首次可用、惰性初始化或预热、后续热运行",
            "空闲、正常活动、持续活动、突发输入、过载、解除压力后的恢复",
            "普通输入、代表性大输入、大量对象或事件、长项目、长时间运行",
            "成功、失败、取消、重试、模型或配置切换、页面离开、关闭、重启恢复",
            "静态审查可以完成清单和风险分析",
            "不得声称速度、吞吐、泄漏或真实硬件表现已经成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_one_cheap_operation_cannot_represent_distinct_cost_topologies(self) -> None:
        for fragment in (
            "按会改变成本拓扑的操作形状拆分",
            "属性原地修改、集合成员增加或删除、拆分或合并",
            "重排或涟漪更新、关系变化和二级投影更新",
            "各选择至少一个代表性操作",
            "一个廉价操作通过不能代表这些结构操作",
            "同一闭合变更集并产生同一种工作放大",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_amplification_and_all_queue_layers_are_audited(self) -> None:
        for fragment in (
            "代表性单次成本 × 实际次数",
            "每条进度写数据库",
            "每个事件重新读取完整任务",
            "操作系统或原生事件队列",
            "线程池或执行器内部等待队列",
            "按键合并映射",
            "不可丢终态",
            "最终权威状态能通过快照或协调扫描恢复",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_stream_shape_and_observability_sinks_are_first_class_work(self) -> None:
        amplification = PERFORMANCE_TEXT.split("## 3. 沿完整用户链计算工作放大", 1)[
            1
        ].split("## 4. 按真实表面检查性能所有权", 1)[0]
        ordered = (
            "总字节量",
            "分片数量与分布",
            "未消费尾部",
            "累计复制和扫描字节",
            "代表性重复分片",
            "一个会跨越协议或 token 边界的对抗切分",
        )
        positions = [amplification.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "一个短前缀加一个剩余大块",
            "日志、追踪、审计、持久重放、缓存和调试导出",
            "正式下游消费者",
            "权威无损记录和有界诊断投影分别核算",
            "二级消费者仍无必要地完整物化并持久化同一大对象",
            "不能为了更快静默降低可诊断性",
            "一次性处理已有权威小上限的内存值",
            "不触发流式工作形状与观测副本闭包",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, amplification)

        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        self.assertIn("真实重复分片下产生累计复制或扫描放大", closure)
        self.assertIn("无必要地完整物化同一大对象", closure)

    def test_runtime_surfaces_have_specific_performance_contracts(self) -> None:
        for fragment in (
            "不可见不等于未实例化",
            "实际查询计划",
            "索引存在但未被使用不算修复",
            "逐项输入重新启动同一进程或加载同一模型",
            "旧代结果不得进入新代任务",
            "实时回调只承担有明确上界的搬运与状态更新",
            "分别测量回调占用时间、排队等待、模型或处理耗时",
            "缓存优化先冻结信任边界",
            "关闭顺序从停止生产者开始",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_resource_accounting_uses_the_owned_process_tree_and_lifecycle(self) -> None:
        for fragment in (
            "完整进程树核算根进程、子进程和全部后代",
            "不能用父进程工作集、配置的 worker 数或单进程估算替代",
            "共享池或常驻服务基线、单任务增量",
            "任务执行峰值、任务结束后的保留量、空闲回收后的稳定水平",
            "正式关闭后的释放",
            "共享进程只在一个所有者下计入一次",
            "资源总量保持未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_execution_context_memory_budget_separates_stack_from_process_total(
        self,
    ) -> None:
        resources = PERFORMANCE_TEXT.split("### 资源趋势和关闭", 1)[1].split(
            "## 5. 建立可比较的测量证据", 1
        )[0]
        ordered = (
            "单个执行上下文的分配账本",
            "线程栈、堆或对象池、共享映射还是设备内存",
            "单实例大小、最大同时实例数",
            "当前目标平台的线程栈预算",
            "最坏调用链 + 框架保留",
            "有界堆对象、复用池或分块处理",
        )
        positions = [resources.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "每线程限制独立生效",
            "不能用进程总内存、低并发或正常短跑替它背书",
            "改到堆上只退出栈耗尽风险",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, resources)

    def test_retained_resource_closure_bounds_items_aggregate_and_transient_peak(
        self,
    ) -> None:
        resources = PERFORMANCE_TEXT.split("### 资源趋势和关闭", 1)[1].split(
            "## 5. 建立可比较的测量证据", 1
        )[0]
        ordered = (
            "从正式内容身份展开完整保留闭包",
            "活动工作副本",
            "预览、索引、DOM 或设备投影",
            "单对象成本和当前最外层正式所有者内的累计成本",
            "正常路径与最坏生命周期的同时峰值",
        )
        positions = [resources.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "单对象大小、活动对象数量",
            "操作过程中的瞬时峰值",
            "单文件、单请求或单标签有限，不能证明",
            "硬上界",
            "拒绝、回收、卸载或降级语义",
            "不会因此自动触发无关的全仓容量治理",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, resources)

    def test_read_only_measurement_cannot_mutate_user_state(self) -> None:
        for fragment in (
            "只读性能审计不能借“需要测量”改变项目状态",
            "自动迁移 schema、写运行缓存",
            "不得把它直接指向用户真实数据根",
            "数据库只读连接、隔离数据根或经过内容身份核对的副本",
            "不能把它造成的结果归到产品",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PERFORMANCE_TEXT)

    def test_each_optimization_remeasures_its_direct_work_before_broad_regression(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        ordered = (
            "根因假设连接到一个能够直接观察的工作量",
            "同一正式入口、输入身份和冷、热或命中状态",
            "再运行宽泛回归",
            "停止叠加优化",
            "重新取得 profile 或查询计划并更新根因",
        )
        positions = [measurement.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_suite_time_is_not_compared_when_collected_workload_changes(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "实际收集到的测试身份、参数化展开、夹具、并行方式",
            "测试新增、删除、改名、改变选择范围或迁移执行路径后",
            "只作为对应身份的正确性回归证据",
            "不能据此声称产品或测试套件获得了性能提升",
            "冻结共同测试身份或建立独立代表性 benchmark",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_smaller_workload_cannot_close_the_original_performance_contract(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "性能优化和容量合同变化必须分账",
            "正式入口继续接受相同的代表性输入",
            "缩小允许输入规模、降低原有容量上限",
            "拒绝此前合法输入",
            "不能被记为性能优化",
            "由产品合同的权威来源确认",
            "原性能发现仍然开放",
            "较小工作负载下的更快数字只证明较小边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_approximation_cannot_masquerade_as_exact_optimization(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "近似捷径不能伪装成等价优化",
            "候选数量上限、采样、代表项或锚点比较、近似搜索",
            "质量、完整性或产品合同变化",
            "未优化的参考实现或其它结果预言",
            "代表性与对抗性输入",
            "输出集合、排序、召回、精度、终态",
            "只证明比较次数、延迟或资源下降不构成等价证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_logical_retention_requires_product_authority_and_preview(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        ordered = (
            "物理存储维护与业务记录的逻辑淘汰必须分账",
            "性能目标不能凭空发明 30 天、365 天等保留期",
            "权威数据生命周期决定",
            "时间字段、终态与进行中关系、豁免项",
            "报告或快照依赖和恢复语义",
            "现有数据生成可核对的影响预演",
            "迁移、回滚、观测与异常停止条件",
        )
        positions = [measurement.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能把删除数据记为性能修复", measurement)

    def test_performance_regression_guard_is_bounded_on_bad_candidate(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "在故障或退化实现上也必须有界",
            "计数预算或断路器，一旦超过预算立即失败",
            "规模更小但仍能区分正确与退化实现的固定夹具",
            "能够按准确进程树安全回收的外部超时",
            "不能先让病态工作完整跑完再断言",
            "不能要求维护者猜测进程身份后手工终止",
            "已知坏候选在规定边界内失败",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_gate_compliance_is_not_overclaimed_as_performance_health(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "验收门槛与性能评价分开记录",
            "权威预算被超过时是合同失败",
            "预算内只证明该项门禁成立",
            "不能自动推出整体性能健康",
            "体验风险或优化候选",
            "门禁仍然通过",
            "不能把风险改写成合同失败",
            "没有权威预算时",
            "待确认的产品判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_automatic_parallelism_preserves_absolute_and_relative_guards(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        for fragment in (
            "自动并发策略以已经声明的用户结果为选择目标",
            "总耗时、尾部延迟、启动与收尾固定成本",
            "相同输入、后端和缓存条件",
            "独立的绝对安全上限与同机相对不退化",
            "相对改善不能关闭已经超过的用户预算",
            "候选运行前分别冻结并记录权威来源",
            "不能让已经看见的候选数字反向成为它自己的通过标准",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, measurement)

    def test_audit_owned_observers_are_terminal_before_timing(self) -> None:
        measurement = PERFORMANCE_TEXT.split("## 5. 建立可比较的测量证据", 1)[1].split(
            "## 6. 修复交接与二次性能复审", 1
        )[0]
        ordered = (
            "第一条计时前",
            "取得终态",
            "不启动无边界目录遍历",
            "重叠期间取得的全部性能数字失效",
            "重新核对资源",
        )
        positions = [measurement.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能擅自终止", measurement)
        self.assertIn("不能与审计自扰合并成产品结论", measurement)

    def test_closure_requires_invariants_user_chain_and_reaudit(self) -> None:
        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        ordered = (
            "一个直接保护性能不变量的目标检查",
            "同一正式入口、代表性输入和当前目标平台上的用户链证据",
            "正确性、取消、错误、恢复和资源所有权没有因提速退化",
            "最后一次性能相关修改之后",
            "重新生成一次二次性能复审",
        )
        positions = [closure.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "新的原生或执行器队列是否无界",
            "事件限频是否丢终态",
            "缓存是否跨越信任边界",
            "关闭后入口是否重启服务",
            "验证器是否写入用户数据或全局缓存",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, closure)

    def test_worker_crash_keeps_current_attempt_cause_across_host_restart(
        self,
    ) -> None:
        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        ordered = (
            "操作接受点",
            "精确失败分类",
            "正式入口接受一次真实操作",
            "原操作身份、尝试 generation、实际可执行文件",
            "结构化退出状态或操作系统崩溃证据",
            "原操作先进入准确终态",
            "只为新的操作建立新 generation",
            "提交一个合法操作",
            "正式消费者取得完整结果",
        )
        positions = [closure.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "`durable-operation-governance.md`",
            "`hard-to-reproduce-diagnostics.md`",
            "不能把当前失败改写成“没有活动任务”",
            "执行器仍可用",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, closure)

    def test_secondary_reaudit_precedes_candidate_freeze_and_expensive_qualification(
        self,
    ) -> None:
        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        workflow = "先完成直接因果检查" + closure.split(
            "先完成直接因果检查", 1
        )[1].split("完整测试、静态检查", 1)[0]
        ordered = (
            "直接因果检查",
            "二次性能复审",
            "冻结准确候选",
            "最终完整用户链、规模、视觉、原生或其它昂贵资格检查",
        )
        positions = [workflow.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "候选保持未冻结",
            "不能先用完整套件取得完成资格",
            "相关资格立即失效并返回二次复审与候选冻结",
            "为何对最终候选仍然新鲜",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, workflow)


if __name__ == "__main__":
    unittest.main()
