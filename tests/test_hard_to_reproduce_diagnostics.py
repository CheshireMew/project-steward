from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
DIAGNOSTIC_TEXT = (
    SKILL_ROOT / "references" / "hard-to-reproduce-diagnostics.md"
).read_text(encoding="utf-8")


class HardToReproduceDiagnosticTests(unittest.TestCase):
    def test_skill_routes_the_method_from_prevention_and_root_cause(self) -> None:
        prevention = SKILL_TEXT.split("### 4. 改动前预防", 1)[1].split(
            "### 5. 根因治理", 1
        )[0]
        remediation = SKILL_TEXT.split("### 5. 根因治理", 1)[1].split(
            "## 支撑与专项能力", 1
        )[0]
        route = "references/hard-to-reproduce-diagnostics.md"

        self.assertIn(route, prevention)
        self.assertIn(route, remediation)
        self.assertIn("先记录本次进入原因与适用维度", prevention)
        self.assertIn("先明确进入原因与适用维度", remediation)
        self.assertIn("普通确定性问题不加载这项方法", prevention)
        self.assertIn("普通确定性缺陷继续沿本节的常规根因路径", remediation)

    def test_common_path_precedes_and_composes_special_dimensions(self) -> None:
        common = DIAGNOSTIC_TEXT.index("## 2. 共同路径")
        dimensions = DIAGNOSTIC_TEXT.index("## 3. 特殊维度可以同时叠加")
        self.assertLess(common, dimensions)
        self.assertIn(
            "共同路径始终负责“竞争解释 → 可区分信号 → 最便宜实验 → 最终确认”",
            DIAGNOSTIC_TEXT,
        )
        self.assertIn("同一个问题可以同时选择多个维度", DIAGNOSTIC_TEXT)

        for dimension in (
            "### 时间与累计",
            "### 并发、所有权与顺序",
            "### 确定性派生产物的单一生产者",
            "### 吞吐、背压与资源",
            "### 受验证的高速路径与原子回退",
            "### 环境与外部进程",
            "### 数据、缓存与版本沿袭",
            "### 验证器与测试驱动干扰",
        ):
            with self.subTest(dimension=dimension):
                self.assertIn(dimension, DIAGNOSTIC_TEXT)

    def test_time_waits_isolation_and_assertions_use_formal_signals(self) -> None:
        for fragment in (
            "生产者记录的发生顺序",
            "消费者终于获得执行机会的墙钟",
            "不能用事件送达后的固定睡眠重新发明发生顺序",
            "固定睡眠只能作为有界等待的上限",
            "正式消费者可观察的状态变化",
            "稳定一一对应",
            "不能靠放宽阈值",
            "新鲜进程、上下文、缓存和输出位置",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

        for public_behavior in (
            "输入自带发生时间或序列",
            "固定睡眠只作为等待上限",
            "独立部署目标和浏览器场景使用新鲜环境",
        ):
            with self.subTest(public_behavior=public_behavior):
                self.assertIn(public_behavior, README_TEXT)

    def test_verified_fast_paths_are_qualified_and_fallback_atomically(self) -> None:
        ordered = (
            "先冻结标准路径、输出合同",
            "每个真正参与生产的 worker",
            "验证完成后从新鲜生产状态开始",
            "注入一次运行期故障",
            "废弃本次高速路径的全部临时结果",
            "从新鲜状态完整运行标准路径",
            "才原子发布",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能保留前半段高速结果", DIAGNOSTIC_TEXT)
        self.assertIn("文件存在或非空不能代表成功", DIAGNOSTIC_TEXT)
        self.assertIn("快慢路径混合产物", README_TEXT)

    def test_large_immutable_content_reuses_only_bound_validation_receipts(self) -> None:
        for fragment in (
            "成为不可变对象时",
            "一次完整读取、内容校验和写入复核",
            "同时绑定内容身份、版本、物理对象和成功状态的回执",
            "必须重新读取正式内容",
            "唯一能建立不可变事实的边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

        self.assertIn("正式进入不可变状态", README_TEXT)

    def test_deterministic_derivatives_have_one_cross_process_producer(
        self,
    ) -> None:
        self.assertIn(
            "当多个线程或进程可能为同一稳定键生产",
            DIAGNOSTIC_TEXT,
        )
        ordered = (
            "无锁快速检查现有结果",
            "取得覆盖整个生产过程的同键租约",
            "在租约内重新检查结果与版本",
            "唯一生产者生成、校验并原子发布",
            "等待者读取同一已发布结果",
            "释放租约",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能只在最终重命名时加锁",
            "相同稳定键必须合并为一个生产过程",
            "不同键保持并行",
            "实际生产调用恰好一次",
            "损坏或旧版本结果证明只触发一次重建",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

        for fragment in (
            "覆盖整个生产过程的同键租约",
            "在租约内重新检查后只生产一次",
            "不同键仍可并行",
            "只触发一次重建",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_diagnostic_order_reduces_uncertainty_before_expensive_runs(self) -> None:
        ordered = (
            "一次代表性真实失败",
            "列出相互竞争的解释",
            "为每个解释写出可区分信号",
            "在最早相关边界补足观测",
            "先做最便宜的区分实验",
            "把产品、运行环境和验证器分开",
            "冻结产品代码、配置和验证器",
            "昂贵的完整链路只用于最终确认",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能 mock 掉正在判断的核心边界", DIAGNOSTIC_TEXT)
        self.assertIn("不直接开始另一轮相同的昂贵运行", DIAGNOSTIC_TEXT)

    def test_reference_is_cross_project_and_remains_a_leaf_method(self) -> None:
        self.assertNotIn("references/", DIAGNOSTIC_TEXT)
        self.assertNotRegex(DIAGNOSTIC_TEXT, r"[A-Za-z]:\\")
        self.assertNotRegex(DIAGNOSTIC_TEXT, r"\b\d+\s*秒")

        for cross_project_boundary in (
            "外部系统",
            "队列或缓冲",
            "内存、句柄、连接、文件或工作项",
            "数据、缓存与版本沿袭",
            "验证器与测试驱动干扰",
        ):
            with self.subTest(cross_project_boundary=cross_project_boundary):
                self.assertIn(cross_project_boundary, DIAGNOSTIC_TEXT)

    def test_readme_exposes_the_behavior_without_making_it_the_default(self) -> None:
        self.assertIn("不会靠反复跑昂贵长测碰运气", README_TEXT)
        self.assertIn("同一个问题可以同时叠加", README_TEXT)
        self.assertIn("不会把这些专项检查强加给普通确定性改动", README_TEXT)
        self.assertIn("昂贵完整链才用于最终确认", README_TEXT)


if __name__ == "__main__":
    unittest.main()
