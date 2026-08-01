from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
AGENT_TEXT = (
    SKILL_ROOT / "agents" / "openai.yaml"
).read_text(encoding="utf-8")


class CoreIdentityTests(unittest.TestCase):
    def test_default_identity_is_learning_prevention_and_governance(self) -> None:
        goal = SKILL_TEXT.split("## 目标", 1)[1].split("## 路由", 1)[0]
        for fragment in (
            "按时间完整覆盖请求、决定、动作、警告、超时、重试、纠正与证据",
            "按多个用户最终结果分别恢复成功与失误",
            "找到已证明机制、能力缺口和最早预防点",
            "用可迁移机制更新 Project Steward 的活动能力",
            "在后续改动前预防或在缺陷后完成根因治理",
            "用新的真实结果继续校正同一项能力",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, goal)

        self.assertIn(
            "只有用户明确要求全面检查、健康判断或综合审计时",
            goal,
        )
        self.assertNotIn("默认执行只读的项目综合审计", SKILL_TEXT)
        self.assertIn(
            "用户环境档案保存当前用户与机器的可变工具事实",
            goal,
        )

    def test_main_router_places_core_loop_before_specialties_and_audit(
        self,
    ) -> None:
        router = SKILL_TEXT.split(
            "### 1. 先按最终结果选择主路径", 1
        )[1].split("### 2. 建立共同项目事实", 1)[0]

        ordered = (
            "进入“对话学习与自我进化”",
            "进入“改动前预防”",
            "进入“根因治理”",
            "进入“项目研究与讲解”",
            "进入“README 与主页”",
            "进入“人性化日志”",
            "进入“用户环境档案与执行环境”",
            "进入“项目综合审计”",
        )
        positions = [router.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_bare_repository_uses_project_explanation(self) -> None:
        goal = SKILL_TEXT.split("## 目标", 1)[1].split("## 路由", 1)[0]
        self.assertIn(
            "只提供 GitHub 仓库、本地目录或源码包进入“项目研究与讲解”",
            goal,
        )

        research_section = SKILL_TEXT.split(
            "### 6. 项目研究与讲解", 1
        )[1].split("### 7. 项目基线与模板", 1)[0]
        self.assertIn(
            "它为谁解决什么问题、用户最终得到什么、什么时候有用",
            research_section,
        )
        self.assertIn(
            "达到当前问题的理解结果后停止",
            research_section,
        )
        self.assertIn(
            r"E:\Work\BaiduSyncdisk\Code\Example",
            research_section,
        )
        self.assertIn(
            "-DestinationRoot <目标根>",
            research_section,
        )
        self.assertIn("失败时保留已产生目录", research_section)
        self.assertIn("停止本条路径", research_section)
        self.assertIn("上下文噪音", research_section)
        self.assertIn(
            "只有第 4 项条件成立时，才进一步给出效果、适用性或“值不值得用”的判断",
            research_section,
        )
        self.assertIn("understand a repository", SKILL_TEXT)
        self.assertNotIn("one-off explanation", SKILL_TEXT)

    def test_metadata_and_first_use_expose_the_core_route(self) -> None:
        self.assertIn(
            "从完整项目过程持续学习，并治理架构、持久操作、用户环境、仓库研究与发布链路",
            AGENT_TEXT,
        )
        self.assertIn(
            "使用 $project-steward 阅读这个会话",
            AGENT_TEXT,
        )
        self.assertIn("让 Project Steward 的可复用治理能力自我进化", AGENT_TEXT)
        self.assertIn("项目专属事实继续留在项目原有真源", AGENT_TEXT)
        self.assertNotIn("综合审计", AGENT_TEXT)

        first_use = README_TEXT.split(
            "## 第一次使用", 1
        )[1].split("## 安装", 1)[0]
        self.assertIn("从一次已经发生的工作里进化", first_use)
        self.assertIn("按多个用户最终结果", first_use)
        self.assertIn("项目专属事实继续留在项目原有真源", first_use)
        self.assertNotIn("综合审计", first_use)

    def test_self_evolution_is_explicit_and_project_paths_stop_at_result(
        self,
    ) -> None:
        learning = (
            SKILL_ROOT
            / "references"
            / "conversation-learning-and-self-evolution.md"
        ).read_text(encoding="utf-8")
        prevention = (
            SKILL_ROOT / "references" / "change-prevention.md"
        ).read_text(encoding="utf-8")
        remediation = (
            SKILL_ROOT / "references" / "root-cause-remediation.md"
        ).read_text(encoding="utf-8")

        self.assertIn("按用户最终结果分组", learning)
        self.assertIn("先完整覆盖过程证据", learning)
        self.assertIn("外层命令执行器超时", learning)
        self.assertIn("成功经验和暴露的问题都属于候选", learning)
        self.assertIn("高频问题模式或专项方法", learning)
        self.assertIn("Project Steward 当前方法", prevention)
        self.assertIn("实现完成后交付本次预防合同的实际结果并停止", prevention)
        self.assertIn("完成项目结果并按已选路径停止", remediation)
        self.assertIn(
            "只有用户在请求开始时同时明确要求 Project Steward 自我进化",
            prevention,
        )
        self.assertIn(
            "用户在请求开始时同时明确要求 Project Steward 自我进化时",
            remediation,
        )
        remediation_section = SKILL_TEXT.split(
            "### 5. 根因治理", 1
        )[1].split("## 支撑与专项能力", 1)[0]
        self.assertIn(
            "完成后交付根因、最终边界、迁移结果、旧架构退出证据和真实用户链，随后停止",
            remediation_section,
        )

    def test_architecture_governance_is_a_direct_active_capability(self) -> None:
        reference = (
            SKILL_ROOT
            / "references"
            / "architecture-cohesion-governance.md"
        )
        self.assertTrue(reference.is_file())
        self.assertIn(
            "references/architecture-cohesion-governance.md",
            SKILL_TEXT,
        )
        text = reference.read_text(encoding="utf-8")
        for fragment in (
            "高内聚低耦合",
            "语义重复",
            "上帝模块",
            "变化原因",
            "公共表面",
            "把函数移动到多个文件但保留一个暴露全部成员的巨型 facade",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_learning_updates_the_skill_and_preserves_project_truth(
        self,
    ) -> None:
        learning = (
            SKILL_ROOT
            / "references"
            / "conversation-learning-and-self-evolution.md"
        ).read_text(encoding="utf-8")
        for fragment in (
            "先完整覆盖过程证据",
            "再按用户最终结果分组",
            "成功经验和暴露的问题都属于候选",
            "写入权限由主路由的两阶段确认结果决定",
            "只更新本轮行为实际影响的直接消费者",
            "高频问题模式或专项方法",
            "决定行为的协议字段、平台限制、生命周期顺序和版本范围",
            "`archive/` 只保存历史与来源价值",
            "不创建 `.project-steward/experience`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, learning)

        self.assertIn(
            "项目已有的规则、设计文档、代码、配置和测试共同承担项目事实",
            SKILL_TEXT,
        )
        self.assertIn(
            "references/conversation-learning-and-self-evolution.md",
            SKILL_TEXT,
        )

class ProjectArchiveExtractionTests(unittest.TestCase):
    def test_destination_root_is_required_and_no_hidden_fallback_is_created(
        self,
    ) -> None:
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("pwsh is unavailable")

        script = (
            SKILL_ROOT / "scripts" / "extract_project_archive.ps1"
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "sample-project.zip"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr(
                    "sample-project/README.md",
                    "A real project result.",
                )

            completed = subprocess.run(
                [
                    pwsh,
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(script),
                    "-ArchivePath",
                    str(archive),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )

            self.assertNotEqual(0, completed.returncode)
            self.assertFalse((root / ".project-steward-extracted").exists())

    def test_real_zip_is_extracted_and_returned_root_is_consumable(
        self,
    ) -> None:
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("pwsh is unavailable")

        script = (
            SKILL_ROOT / "scripts" / "extract_project_archive.ps1"
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "sample-project.zip"
            destination = root / "extracted"

            with zipfile.ZipFile(archive, "w") as package:
                package.writestr(
                    "sample-project/README.md",
                    "A real project result.",
                )

            completed = subprocess.run(
                [
                    pwsh,
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(script),
                    "-ArchivePath",
                    str(archive),
                    "-DestinationRoot",
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            output_lines = [
                line.strip()
                for line in completed.stdout.splitlines()
                if line.strip()
            ]
            self.assertTrue(output_lines)
            project_root = Path(output_lines[-1])
            readme = project_root / "README.md"
            self.assertTrue(readme.is_file())
            self.assertEqual(
                "A real project result.",
                readme.read_text(encoding="utf-8"),
            )

            readme.write_text("Preserved first extraction.", encoding="utf-8")
            second = subprocess.run(
                [
                    pwsh,
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(script),
                    "-ArchivePath",
                    str(archive),
                    "-DestinationRoot",
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            second_root = Path(
                [
                    line.strip()
                    for line in second.stdout.splitlines()
                    if line.strip()
                ][-1]
            )
            self.assertNotEqual(project_root, second_root)
            self.assertEqual(
                "Preserved first extraction.",
                readme.read_text(encoding="utf-8"),
            )
            self.assertTrue((second_root / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
