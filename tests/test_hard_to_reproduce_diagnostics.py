from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
DIAGNOSTIC_TEXT = (
    SKILL_ROOT / "references" / "hard-to-reproduce-diagnostics.md"
).read_text(encoding="utf-8")


class HardToReproduceDiagnosticTests(unittest.TestCase):
    def test_skill_routes_the_method_from_prevention_and_root_cause(self) -> None:
        prevention = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        remediation = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 项目研究与讲解", 1
        )[0]
        route = "references/hard-to-reproduce-diagnostics.md"

        self.assertIn(route, prevention)
        self.assertIn(route, remediation)
        self.assertIn("进入原因和适用的特殊维度", DIAGNOSTIC_TEXT)
        self.assertIn("普通确定性问题不需要这项加重方法", DIAGNOSTIC_TEXT)

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
            "### 连续实时管线的进度真值与分层验收",
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


    def test_chronological_latest_uses_a_formal_total_order_under_clock_collision(
        self,
    ) -> None:
        for fragment in (
            "有限精度时间戳只能记录时间区间，不能单独建立全序",
            "序列、revision 或事务内单调递增的排序值",
            "UUID、对象 ID、列表位置",
            "冻结时钟",
            "相同时间戳下连续创建多个对象",
            "存储重开、查询和最终消费者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)


    def test_overlapping_operations_are_correlated_by_producer_identity(
        self,
    ) -> None:
        concurrent = DIAGNOSTIC_TEXT.split("### 并发、所有权与顺序", 1)[
            1
        ].split("### 确定性派生产物的单一生产者", 1)[0]
        ordered = (
            "正式生产者分配稳定操作身份",
            "开始、更新、完成、失败、取消和清理事件",
            "消费者按操作身份与 generation 建立索引",
            "正式入口启动两个真实操作",
            "实际事件、队列或传输边界",
            "正式消费者处理",
            "第二个操作没有被修改、移除或错误终止",
        )
        positions = [concurrent.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "缺少它们的事件都是合同失败",
            "不得退回“最后一个”“当前项”",
            "过期回调、较晚失败和取消只能收尾它们所属的旧尝试",
            "直接调用消费者 handler 或手写事件 payload",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, concurrent)


    def test_foreground_work_has_explicit_shared_resource_arbitration(
        self,
    ) -> None:
        ordered = (
            "阻止后台重新取得资源",
            "请求当前后台生产者停止",
            "等待它确认退出或释放",
            "开始前台生产者",
            "前台完成后恢复调度",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "交互前台与后台整理、索引、预热、同步或维护任务",
            "不能让后台任务碰巧先取得普通互斥锁",
            "未完成批次是否允许推进游标或检查点",
            "等待超时保持资源所有权未知并阻止第二个生产者",
            "用受控阻塞生产者让后台先取得真实共享资源",
            "未完成后台进度没有前移",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)


    def test_continuous_realtime_progress_uses_layered_authoritative_evidence(
        self,
    ) -> None:
        for fragment in (
            "逐层列出每个实际读取者",
            "不能用某一层的局部含义推断整条链",
            "正式生产完成序列",
            "正式消费或展示确认",
            "最终可见或提交结果",
            "序列连续只能证明没有离散缺口",
            "不能证明整条管线没有整体变慢",
            "每一个可能跳过、丢弃、延后或追赶结果的决定点",
            "正常负载下的实时能力",
            "过载时如实报告",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

        ordered_stages = (
            "启动和短窗口",
            "目标平台的真实消费者",
            "持续运行与长时累计",
            "过载、解除压力与恢复",
        )
        positions = [DIAGNOSTIC_TEXT.index(stage) for stage in ordered_stages]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("前一层通过不能替代后一层", DIAGNOSTIC_TEXT)
        self.assertIn("环境饱和可以让正常能力基准失去代表性", DIAGNOSTIC_TEXT)
        self.assertIn("仍可证明过载合同", DIAGNOSTIC_TEXT)


    def test_health_metrics_require_real_measurement_and_user_calibration(
        self,
    ) -> None:
        for fragment in (
            "先证明诊断指标确实测量了所声称的事实",
            "正式测量生产者与测量边界",
            "尚未测量、不可用和真实零值怎样区分",
            "用于校准的独立用户可观察结果",
            "默认值、常量、缺失回调",
            "零是已经测量得到的值",
            "用户结果是失败证据，指标失去诊断资格",
            "从公共表面、成功条件和测试断言中退出",
            "不保留没有来源的兼容属性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

        self.assertIn("两者冲突时，用户结果是失败证据", DIAGNOSTIC_TEXT)
        self.assertIn("默认值、常量、缺失回调", DIAGNOSTIC_TEXT)

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

    def test_comparative_fast_path_benchmarks_hold_backend_identity_constant(
        self,
    ) -> None:
        for fragment in (
            "两边除目标变量外使用同一实际生产者、后端、资格状态和输入身份",
            "最终选中的身份写入证据",
            "结果已经被后端差异混杂",
            "冻结同一个合格后端再比较目标变量",
            "把后端作为显式矩阵",
            "资格与正确性判定要同性能选择分开",
            "不能同时决定采用哪个生产者并充当该生产者更快的证明",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)

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

    def test_repeated_observations_prove_the_same_object_before_state_change(
        self,
    ) -> None:
        ordered = (
            "先证明多次观测针对同一个对象",
            "对象标识的权威发现来源",
            "每次探测实际收到的字面标识",
            "各次解析后的稳定对象身份",
            "只有各次探测身份相同",
            "才允许进入同一对象的状态变化解释",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "直接把这个值传给后续探测",
            "相对路径相同但工作目录不同",
            "身份不同的探测分别描述各自对象",
            "“未找到”只证明该次字面标识解析到的对象不存在",
            "在此之前不得归因于同步、并发写入、缓存或外部进程",
            "不得开始等待或重试",
            "没有跨观测比较的单次稳定检查不增加这份对象对照",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)


    def test_multistage_toolchains_are_verified_at_the_handoff_boundaries(
        self,
    ) -> None:
        ordered = (
            "建立从父入口到正式消费者的多层工具链执行闭包",
            "逐层记录实际可执行文件与版本",
            "工具在当前终端能够单独运行",
            "与正式入口相同的启动器和交接语义",
            "每次只改变一个能够排除竞争解释的变量",
            "最早出现身份或语义偏离的边界取证",
        )
        positions = [DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "手工复制产物、跳过正式任务",
            "从新鲜输出状态重新运行同一个正常入口",
            "正式消费者读取本轮结果",
            "不能把替代路径留下的产物与新运行拼成一次通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DIAGNOSTIC_TEXT)


    def test_external_process_attempts_keep_one_owner_until_terminal(self) -> None:
        external_process = DIAGNOSTIC_TEXT.split("### 环境与外部进程", 1)[
            1
        ].split("### 数据、缓存与版本沿袭", 1)[0]
        ordered = (
            "本次执行尝试身份",
            "外层等待结束不改变原执行所有权",
            "查询失败、部分返回或空输出只让相应事实保持未知",
            "重新执行前先取得原执行的正式终态",
            "整个进程树已经结束",
            "资源已经释放",
            "停止后重新核对进程、监听端口、锁和输出位置",
        )
        positions = [external_process.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("一个进程已经消失不能替其它进程退出", DIAGNOSTIC_TEXT)
        self.assertIn("不启动争用同一资源的重复任务", DIAGNOSTIC_TEXT)

    def test_validator_drains_child_output_without_hiding_results(self) -> None:
        validator = DIAGNOSTIC_TEXT.split("### 验证器与测试驱动干扰", 1)[1]
        ordered = (
            "从子进程启动起为两条流分别登记消费所有者",
            "并发排空到 EOF",
            "等待子进程终态的线程不能先停止读取",
            "任一未消费管道写满",
            "外层超时只证明验证器破坏了运行条件",
            "产品状态保持未知",
        )
        positions = [validator.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "stdout 或 stderr",
            "受控文件、有界日志接收器或空设备",
            "结构化结果、致命错误和终态仍使用独立无损通道",
            "不能为了避免管道阻塞把权威结果静默丢弃",
            "持续高频输出的受控子进程",
            "对比有无并发排空",
            "正式消费者读取结构化结果",
            "不能拿来给产品失败背书",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, validator)

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



if __name__ == "__main__":
    unittest.main()
