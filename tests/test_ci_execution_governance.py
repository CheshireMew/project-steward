from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
CI_TEXT = (
    SKILL_ROOT / "references" / "ci-execution-governance.md"
).read_text(encoding="utf-8")


class CiExecutionGovernanceTests(unittest.TestCase):
    def test_project_level_ci_method_is_reachable_from_both_change_paths(
        self,
    ) -> None:
        route = "references/ci-execution-governance.md"
        prevention = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        remediation = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]

        self.assertIn(route, prevention)
        self.assertIn(route, remediation)
        self.assertIn("普通单个 CI 报错仍按当前开发任务处理", CI_TEXT)

    def test_one_validation_plan_drives_cost_ordered_execution(self) -> None:
        ordered = (
            "先生成一份验证计划",
            "工作流预检",
            "便宜的确定性检查",
            "目标平台冷启动冒烟",
            "受影响测试与资源分片",
            "昂贵合同与真实用户链",
            "质量门",
        )
        positions = [CI_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("全部 CI 作业消费它", CI_TEXT)
        self.assertIn("文档、许可证、致谢和纯仓库元数据", CI_TEXT)

    def test_environment_cache_is_reproducible_and_separate_from_products(
        self,
    ) -> None:
        for fragment in (
            "缓存完整语言或依赖环境",
            "操作系统与架构",
            "解释器或运行时的准确版本和 ABI",
            "依赖锁文件内容身份",
            "刷新当前候选源码的 editable 或等价安装",
            "执行依赖一致性检查",
            "语言依赖环境与原生 SDK、浏览器、媒体运行时",
            "首次冷运行与后续热运行分别记录",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

        self.assertIn("derived-artifact-governance.md", CI_TEXT)
        self.assertIn("产品派生产物及其语义缓存", CI_TEXT)

    def test_resource_partition_is_complete_without_marker_churn(self) -> None:
        for fragment in (
            "测试框架实际收集的唯一节点身份",
            "不要为了形式给大量测试机械添加多套 marker",
            "分区完整且互斥",
            "轻量档位不安装、启动或暴露重型能力",
            "测试意外请求它们时明确失败",
            "参数化和生成测试按实际节点计入",
            "大迁移后以最新收集与真实调用重新建立基线",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_shards_use_timing_and_report_wall_and_compute_cost(self) -> None:
        for fragment in (
            "历史耗时",
            "测试文件字节数、测试函数数量和一次偶然运行不能代表耗时",
            "新节点没有历史时使用公开的保守默认权重",
            "最慢分片的墙钟时间",
            "全部分片的总计算量",
            "冷启动成本",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_preflight_and_failed_scope_rerun_preserve_failure_evidence(
        self,
    ) -> None:
        for fragment in (
            "输出的缺失、空字符串、真假值和错误值语义",
            "以与 CI 相同的 shell、模块或包入口启动",
            "测试收集实际非空",
            "只有存在真实瞬态依据时",
            "允许在相同提交、输入、runner 和命令下做一次原样重跑",
            "限于失败作业及依赖其结果的质量门",
            "不重新运行完整工作流",
            "不能用通用 retry",
            "不能把失败归咎于“冒烟太早”后移除它",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_method_reports_real_bottlenecks_and_stays_cross_project(self) -> None:
        for fragment in (
            "排队与启动",
            "依赖恢复、下载与安装",
            "各分片耗时、最长关键路径与总计算量",
            "冷运行、热运行及失败范围重跑",
            "只有阶段计时和关键路径能够证明瓶颈",
            "不为每条说明制作镜像断言",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

        for forbidden in (
            "MediaFlow",
            "Qt",
            "MLT",
            "Chromium",
            "524",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, CI_TEXT)

        self.assertNotRegex(CI_TEXT, r"[A-Za-z]:\\")
        self.assertLessEqual(len(SKILL_TEXT.splitlines()), 220)
        self.assertLessEqual(len(SKILL_TEXT), 14_000)

        direct_references = set(
            re.findall(r"references/[A-Za-z0-9._/-]+\.md", SKILL_TEXT)
        )
        self.assertIn("references/ci-execution-governance.md", direct_references)
        for reference in direct_references:
            with self.subTest(reference=reference):
                self.assertTrue((SKILL_ROOT / reference).is_file())


if __name__ == "__main__":
    unittest.main()
