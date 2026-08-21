from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT_TEXT = (SKILL_ROOT / "references" / "project-audit.md").read_text(
    encoding="utf-8"
)
PERFORMANCE_TEXT = (
    SKILL_ROOT / "references" / "project-performance-governance.md"
).read_text(encoding="utf-8")


class ProjectPerformanceGovernanceTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
