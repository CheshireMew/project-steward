from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
PROGRESS_TEXT = (
    SKILL_ROOT / "references" / "task-progress-governance.md"
).read_text(encoding="utf-8")


class TaskProgressTruthGovernanceTests(unittest.TestCase):
    def test_skill_routes_progress_from_all_formal_consumers(self) -> None:
        prevention = SKILL_TEXT.split("### 4. 改动前预防", 1)[1].split(
            "### 5. 根因治理", 1
        )[0]
        remediation = SKILL_TEXT.split("### 5. 根因治理", 1)[1].split(
            "## 支撑与专项能力", 1
        )[0]
        experience = SKILL_TEXT.split("### 9. 产品体验与界面治理", 1)[1].split(
            "### 10. 仓库建立与发布", 1
        )[0]
        route = "references/task-progress-governance.md"

        self.assertIn(route, prevention)
        self.assertIn(route, remediation)
        self.assertIn(route, experience)
        self.assertIn("普通、能够稳定验证的进度功能不因此进入高成本诊断", prevention)
        self.assertIn("不在单个任务旁调整数字", remediation)

    def test_contract_separates_state_phase_and_measured_progress(self) -> None:
        for fragment in (
            "状态、阶段和进度是三种事实",
            "任务生命周期的唯一所有者",
            "当前正式生产步骤",
            "实际执行工作的测量生产者",
            "可计算",
            "不可计算",
            "已完成量、总量和单位",
            "百分比只由这三个事实派生",
            "未知、不可用和未开始不能借零值表达",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROGRESS_TEXT)

    def test_measurement_sources_and_external_tools_are_real(self) -> None:
        for fragment in (
            "正式工作生产者",
            "字节 / 帧 / 媒体时间 / 样本 / 条目 / 批次",
            "默认常量和界面动画都不能替代正式工作量",
            "机器可读进度流",
            "使用与生产入口相同的版本、参数和流式读取边界",
            "正式解析器至少消费一次真实工具输出",
            "不能从最后一行、自然语言关键词或进程仍在运行推算百分比",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROGRESS_TEXT)

    def test_multistage_and_aggregate_progress_do_not_invent_math(self) -> None:
        for fragment in (
            "共享一个真实总量",
            "人为权重、固定起止数字",
            "旧百分比在未知阶段继续冒充当前进展",
            "单位兼容、总量语义一致",
            "按总工作量求和，而不是平均各任务百分比",
            "整体进度保持不可计算",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROGRESS_TEXT)

    def test_full_migration_has_one_model_and_no_compatibility_runtime(self) -> None:
        ordered = (
            "正式进度生产者",
            "回调、事件或结构化消息",
            "任务状态与持久化",
            "聚合或投影",
            "活动界面、CLI 或公共调用者",
            "完成后的正式结果",
        )
        positions = [PROGRESS_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "无法证明来源的旧运行数字迁移为不可计算",
            "移除旧标量字段、旧回调签名、旧 helper、兼容属性、双读",
            "活动运行时不能长期同时解释两套进度真源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROGRESS_TEXT)

    def test_real_chain_covers_determinate_indeterminate_and_visible_result(
        self,
    ) -> None:
        for fragment in (
            "完成前产生至少一次可计算更新",
            "一个无法取得可靠总量的真实阶段保持不可计算",
            "解析器消费真实输出",
            "保存、关闭、重开和真实旧状态迁移",
            "等待正式消费者的可观察状态变化",
            "固定睡眠不能代替用户已经看到",
            "正式结果、文件、记录或外部状态确实可用",
            "消费端手写一份结构化进度只能验证显示组件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROGRESS_TEXT)

    def test_reference_is_cross_project_and_remains_a_leaf_method(self) -> None:
        self.assertNotIn("references/", PROGRESS_TEXT)
        self.assertNotRegex(PROGRESS_TEXT, r"[A-Za-z]:\\")
        self.assertNotRegex(PROGRESS_TEXT, re.compile(r"\b(?:5|10|95|98|99)%"))
        for project_specific_term in ("MediaFlow", "FFmpeg", "MLT", "QML"):
            with self.subTest(project_specific_term=project_specific_term):
                self.assertNotIn(project_specific_term, PROGRESS_TEXT)

    def test_readme_exposes_task_progress_without_conflating_diagnostics(self) -> None:
        for fragment in (
            "用户可见的任务进度不会再把“当前阶段”和“完成比例”混成一个数字",
            "已完成量、总量和单位",
            "总量未知、单次外部请求或无法连续测量的阶段显示不定进度",
            "不同单位或未知成员也不会通过平均百分比伪造聚合进度",
            "退出旧标量字段与固定阶段数字",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

        self.assertIn("诊断指标也必须证明自己真的测量了所声称的事实", README_TEXT)


if __name__ == "__main__":
    unittest.main()
