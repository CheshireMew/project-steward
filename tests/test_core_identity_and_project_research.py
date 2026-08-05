from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT_TEXT = (
    SKILL_ROOT / "agents" / "openai.yaml"
).read_text(encoding="utf-8")
PROJECT_RESEARCH_TEXT = (
    SKILL_ROOT / "references" / "project-research.md"
).read_text(encoding="utf-8")
EFFECTIVENESS_TEXT = (
    SKILL_ROOT / "references" / "project-effectiveness-review.md"
).read_text(encoding="utf-8")


class CoreIdentityTests(unittest.TestCase):
    def test_default_identity_is_learning_prevention_and_governance(self) -> None:
        router = SKILL_TEXT.split("## 角色与路由", 1)[1].split(
            "## 共同边界",
            1,
        )[0]
        for fragment in (
            "保存跨项目可复用的治理方法",
            "同一请求中的独立结果分别建账",
            "对话学习与自我进化",
            "改动前预防",
            "根因治理",
            "项目综合审计",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, router)

        self.assertNotIn("默认执行只读的项目综合审计", SKILL_TEXT)
        self.assertIn(
            "用户和机器的可变工具事实留在项目与 Skill 之外的环境档案中",
            router,
        )

    def test_main_router_places_core_loop_before_specialties_and_audit(
        self,
    ) -> None:
        router = SKILL_TEXT.split("## 角色与路由", 1)[1].split(
            "## 共同边界",
            1,
        )[0]

        ordered = (
            "对话学习与自我进化。",
            "改动前预防。",
            "根因治理。",
            "项目研究与讲解。",
            "README 与主页。",
            "人性化日志。",
            "用户环境档案与执行环境。",
            "项目综合审计。",
        )
        positions = [router.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_bare_repository_uses_project_explanation(self) -> None:
        self.assertIn(
            "看懂仓库、目录或源码包",
            SKILL_TEXT,
        )

        research_section = SKILL_TEXT.split(
            "## 项目研究与讲解", 1
        )[1].split("## 项目基线与模板", 1)[0]
        self.assertIn(
            "references/project-research.md",
            research_section,
        )
        self.assertIn(
            r"E:\Work\BaiduSyncdisk\Code\Example",
            research_section,
        )
        self.assertIn("项目解决什么问题、用户得到什么、什么时候有用", PROJECT_RESEARCH_TEXT)
        self.assertIn("达到对应结果后返回上层主流程", PROJECT_RESEARCH_TEXT)
        self.assertIn(
            "-DestinationRoot <目标根>",
            research_section,
        )
        self.assertIn(
            "上层已经选择实际效果、可靠性、上下文噪音、适用性或采用判断时",
            PROJECT_RESEARCH_TEXT,
        )
        self.assertIn("understand or organize a codebase", SKILL_TEXT)
        self.assertNotIn("one-off explanation", SKILL_TEXT)

    def test_source_archive_research_preparation_needs_no_extra_confirmation(
        self,
    ) -> None:
        common_boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "解压是进入只读研究所需的材料准备，不是项目正式写入",
            "独立避重名目录",
            "无需额外取得解压确认",
            "只授权创建研究副本和读取其内容",
            "安装依赖或解压工具",
            "移动或删除原文件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, common_boundaries)

        research_section = SKILL_TEXT.split(
            "## 项目研究与讲解", 1
        )[1].split("## 项目基线与模板", 1)[0]
        self.assertIn("scripts/extract_project_archive.ps1", research_section)
        self.assertIn("-DestinationRoot <目标根>", research_section)
        self.assertIn(
            r"E:\Work\BaiduSyncdisk\Code\Example",
            research_section,
        )

    def test_validation_depth_follows_change_risk(self) -> None:
        common_boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "验证按改动风险选择层级",
            "直接覆盖本次改动和验收主张的目标检查",
            "文档、许可证、致谢或纯元数据",
            "不启动无关浏览器或端到端链路",
            "公共合同、核心运行时、跨仓库边界、发布",
            "才升级为完整回归和真实用户链",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, common_boundaries)

    def test_metadata_and_first_use_expose_the_core_route(self) -> None:
        self.assertIn(
            "治理项目变更、根因、README、仓库发布与可迁移经验",
            AGENT_TEXT,
        )
        self.assertIn(
            "使用 $project-steward 完整研究这个开源代码项目",
            AGENT_TEXT,
        )
        self.assertIn("判断值得吸收的能力、原始上游和复用关系", AGENT_TEXT)
        self.assertIn("明确要求时再自我进化", AGENT_TEXT)
        self.assertNotIn("综合审计", AGENT_TEXT)

    def test_complete_capability_absorption_has_a_bounded_research_handoff(
        self,
    ) -> None:
        research_section = SKILL_TEXT.split(
            "## 项目研究与讲解", 1
        )[1].split("## 项目基线与模板", 1)[0]
        for fragment in (
            "完整研究或能力采用",
            "references/project-research.md",
            "references/project-effectiveness-review.md",
            "references/project-research-report.md",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, research_section)

        for fragment in (
            "只有用户明确要求完整阅读参考项目",
            "完整覆盖边界",
            "规范真源、手工维护来源与派生视图",
            "名称、别名和示例只负责发现",
            "目标项目的用户结果与唯一边界",
            "候选能力在目标项目中属于核心对象、现有对象操作、获取渠道、视图或筛选、状态反馈还是可选集成",
            "建议入口：现有统一入口 / 对象内行动 / 次级入口 / 独立工作区 / 不采用",
            "来源项目存在某个导航项、独立页面、显眼按钮",
            "与现有对象共享同一组保存、查找、编辑、删除、恢复和交付行为",
            "独立且反复发生的结果、关键决定、生命周期或恢复路径",
            "会改变专业判断与结果的构成性细节",
            "目标项目已经有相同职责、对象或入口",
            "不能证明具体细节已经存在",
            "具体细节已经存在、只有大方向、值得吸收的新细节、不吸收",
            "只要求“看看有哪些值得吸收”时保持只读",
            "不自行创建目标 schema、资源、兼容层或演示实现",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_RESEARCH_TEXT)

        self.assertIn(
            "普通项目介绍、一般比较和只问“它能做什么”继续读取最少够用的材料",
            PROJECT_RESEARCH_TEXT,
        )

        common_boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "先完成独立结果拆分和必要的因果排序",
            "遮住来源检查目标能否认出同一条件",
            "只有上位治理框架算部分具备",
            "完成逐项比较后才提炼共同机制和特殊维度",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, common_boundaries)

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
            "## 根因治理", 1
        )[1].split("## 项目研究与讲解", 1)[0]
        self.assertIn(
            "实施才一次迁移全部生产者、边界和消费者，并退出旧架构",
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
            "项目自己的产品决定、架构事实和长期约束留在项目现有真源中",
            SKILL_TEXT,
        )
        self.assertIn(
            "references/conversation-learning-and-self-evolution.md",
            SKILL_TEXT,
        )

    def test_harness_comparisons_control_one_variable_and_preserve_raw_evidence(
        self,
    ) -> None:
        for fragment in (
            "Harness 或调用路径的受控对照",
            "每次只改变待比较的调用路径",
            "`scenario_id`、标题、类别和期望标签保留在编排器与结果文件中",
            "不发送给候选模型",
            "使用隔离的会话、工作区和副作用目标",
            "先证明每条候选路径按其正式协议运行",
            "先修正实验协议并保留失败证据",
            "不能把编排器缺陷算成模型质量",
            "原始响应、结构化结果、最终用户可见正文、延迟、token",
            "质量评审尽量盲化候选身份",
            "一个指标领先不自动成为总冠军",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, EFFECTIVENESS_TEXT)


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
