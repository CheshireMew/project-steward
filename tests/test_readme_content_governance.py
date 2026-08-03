from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
CONTENT_TEXT = (
    SKILL_ROOT / "references" / "content-architecture.md"
).read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
HERO_PATH = SKILL_ROOT / "assets" / "readme" / "hero.svg"


class ReadmeContentGovernanceTests(unittest.TestCase):
    def test_content_method_owns_the_public_reader_contract(self) -> None:
        for field in (
            "第一采用读者：",
            "首页读者变化：",
            "项目本体与运行载体：",
            "项目身份真源与宿主角色：",
            "到访情境：",
            "交给项目什么：",
            "可观察结果：",
            "第一步：",
            "后续读者：",
            "场景证据：",
            "公开事实与合格材料：",
        ):
            with self.subTest(field=field):
                self.assertIn(field, CONTENT_TEXT)

        self.assertIn(
            "项目同时面向普通使用者和技术维护者时",
            CONTENT_TEXT,
        )
        self.assertIn(
            "第一次真实使用本身要求技术知识时",
            CONTENT_TEXT,
        )
        self.assertIn(
            "项目真实入口、输入、输出和停止位置共同确定项目本体",
            CONTENT_TEXT,
        )
        self.assertIn("references/content-architecture.md", SKILL_TEXT)
        self.assertIn("宿主元数据只用于发现相关事实", CONTENT_TEXT)
        self.assertIn("不用宿主名称重选项目本体", CONTENT_TEXT)
        self.assertIn(
            "首层先兑现首页读者变化",
            CONTENT_TEXT,
        )
        self.assertIn(
            "动作分支写成“条件 → 动作 → 交付 → 停止位置”",
            CONTENT_TEXT,
        )
        source_index = CONTENT_TEXT.index("先建立公开事实与材料资格")
        reader_index = CONTENT_TEXT.index("随后使用已经核定的当前项目事实")
        readme_route = SKILL_TEXT.split("## README 与主页", 1)[1].split(
            "## 许可证治理",
            1,
        )[0]
        content_index = readme_route.index("references/content-architecture.md")
        visual_index = readme_route.index("references/visual-direction.md")
        self.assertLess(source_index, reader_index)
        self.assertLess(content_index, visual_index)

    def test_content_method_separates_adoption_operation_and_maintenance(self) -> None:
        self.assertIn("统一核定项目身份、宿主角色、材料资格、公开读者合同", CONTENT_TEXT)
        self.assertIn("不决定视觉风格", CONTENT_TEXT)
        for layer in ("采用层材料", "操作层材料", "维护层材料"):
            with self.subTest(layer=layer):
                self.assertIn(layer, CONTENT_TEXT)

        self.assertIn("普通读者回述测试", CONTENT_TEXT)
        self.assertIn("什么情况下我会需要它", CONTENT_TEXT)
        self.assertIn("我需要交给它什么或说出什么", CONTENT_TEXT)
        self.assertIn("把它和对应细节移到维护层", CONTENT_TEXT)
        self.assertIn("不在首屏通过增加括号解释来保留", CONTENT_TEXT)
        self.assertIn(
            "项目真实入口、接受的输入、交付和停止位置共同定义项目用途与目标读者",
            CONTENT_TEXT,
        )
        self.assertIn(
            "多个并列意图共同构成项目时，先给字面身份和真实范围",
            CONTENT_TEXT,
        )
        self.assertIn("不用宿主名称重选项目本体", CONTENT_TEXT)
        self.assertIn("主页主身份直接使用上层已经核定的项目身份", CONTENT_TEXT)
        self.assertIn(
            "每句话提供项目身份、真实范围、直接动作、实际结果或必要证据中的至少一项",
            CONTENT_TEXT,
        )
        self.assertIn(
            "来源中的否定、限制和情态说明先还原为具体条件、动作、状态和结果",
            CONTENT_TEXT,
        )
        self.assertNotIn("事实优先从以下材料取得", CONTENT_TEXT)

    def test_public_materials_are_qualified_before_content_consumes_them(self) -> None:
        for fragment in (
            "现有 README、专项文档、示例、内部图片、截图、流程图和生成物只作为候选材料",
            "标为过时或未验证，退出公开事实、证据池、视觉证据等级和复用候选",
            "文件能够读取、图片能够渲染或审计脚本通过都不能改变这项资格",
            "本方法只从上层核定的当前事实和合格材料中写作",
            "过时或未验证的图不进入公开内容",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        self.assertLess(
            CONTENT_TEXT.index("先建立公开事实与材料资格"),
            CONTENT_TEXT.index("随后使用已经核定的当前项目事实"),
        )

    def test_content_method_turns_reader_change_into_written_sections(self) -> None:
        for fragment in (
            "首页和每个核心章节各建立一个章节材料单元",
            "章节读者变化：",
            "对象身份：",
            "直接动作：",
            "动作对象：",
            "可观察结果：",
            "必要证据：",
            "读者下一步：",
            "只有帮助读者完成当前变化或直接证明该变化的材料进入章节",
            "章节顺序由材料之间的真实关系决定",
            "谁对什么做什么，读者得到什么",
            "重写整句或整段的主语、动作、对象和顺序",
            "每个段落新增事实、动作、因果关系、场景、判断依据或真实下一步",
            "正文已经具体、连贯并适合当前读者时停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        for excluded_method in (
            "社交平台的钩子库",
            "传播模板",
            "宣发节奏",
            "作者记忆",
        ):
            with self.subTest(excluded_method=excluded_method):
                self.assertIn(excluded_method, CONTENT_TEXT)

    def test_public_readme_opens_with_self_evolution_contract(self) -> None:
        opening = README_TEXT.split("## 三条核心路径", 1)[0]
        for fragment in (
            "从项目对话和真实结果中改进自己",
            "完整实施过程",
            "先按时间覆盖请求、决定、命令、等待、警告、超时、重试、中断",
            "归入一个结果、跨结果问题、未知项或确认无影响的偶然信息",
            "真正能够跨项目复用的机制",
            "每个项目自己的产品决定、架构事实和长期约束",
            "成功经验也属于经验",
            "高频",
            "后果严重",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, opening)

        internal_terms = (
            "唯一真源",
            "生产者",
            "消费者",
            "schema",
            "helper",
            "mock",
            "冷启动",
            "治理链路",
        )
        for term in internal_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, opening)

        self.assertNotIn("全面审计", opening)
        self.assertNotIn("综合审计", opening)
        self.assertNotIn("Codex", README_TEXT)

    def test_public_readme_explains_host_and_internal_asset_boundaries(self) -> None:
        for fragment in (
            "通用 Skill 的核心工作流、实际依赖和真实使用方式决定项目身份",
            "不会把项目写成该宿主专用",
            "现有 README、内部图片、截图、流程图和生成物只提供候选线索",
            "文件仍在、图片能打开或结构审计通过，都不会替内容准确性背书",
            "复用已有、制作新的、排版表达或跳过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_adoption_path_precedes_maintainer_internals(self) -> None:
        maintenance_index = README_TEXT.index("## 项目模板")
        adoption = README_TEXT[:maintenance_index]
        maintenance = README_TEXT[maintenance_index:]

        adoption_headings = [
            line
            for line in adoption.splitlines()
            if line.startswith("## ")
        ]
        self.assertEqual(
            [
                "## 它怎样从对话中进化",
                "## 三条核心路径",
                "## 持久操作与恢复",
                "## 架构内聚、重复与上帝模块",
                "## 用户环境档案与执行环境",
                "## 其它项目能力",
                "## 第一次使用",
            ],
            adoption_headings,
        )

        self.assertNotIn("project_templates.py", adoption)
        self.assertIn("project_templates.py", maintenance)
        self.assertIn("正式生产者", adoption)
        self.assertIn("全新的 Skill 外部临时项目", maintenance)

    def test_plain_language_prompts_and_technical_capabilities_are_both_kept(
        self,
    ) -> None:
        for prompt_fragment in (
            "阅读这段项目对话",
            "按用户最终结果分别找出成功机制",
            "更新到 Project Steward 自身",
            "结合项目现有规则和 Project Steward 当前方法",
            "检查这个项目是否高内聚低耦合",
            "帮我看懂这个 GitHub 项目",
            "让日志变成人真正能看懂的记录",
            "使用 $project-steward 阅读这个会话的全部历史",
            "使用 $project-steward 看懂这个项目",
        ):
            with self.subTest(prompt_fragment=prompt_fragment):
                self.assertIn(prompt_fragment, README_TEXT)

        self.assertLess(
            README_TEXT.index("## 三条核心路径"),
            README_TEXT.index("全面检查项目健康状况"),
        )
        first_use = README_TEXT.split(
            "## 第一次使用", 1
        )[1].split("## 项目模板", 1)[0]
        self.assertNotIn("综合审计", first_use)

        for retained_fragment in (
            "从历史对话吸收能力",
            "项目模板",
            "根因治理",
            "看懂这个 GitHub 项目",
            "日志",
            "许可证",
            "scripts/project_templates.py",
            "scripts/user_environment_profile.py",
            "scripts/extract_project_archive.ps1",
            "python -m unittest discover -s tests -v",
            "Mozilla Public License 2.0",
        ):
            with self.subTest(retained_fragment=retained_fragment):
                self.assertIn(retained_fragment, README_TEXT)

        self.assertIn(
            "https://github.com/oil-oil/beautify-github-readme",
            README_TEXT,
        )
        self.assertIn("oil-oil", README_TEXT)

    def test_hero_uses_plain_language_without_a_mechanism_card(self) -> None:
        root = ET.parse(HERO_PATH).getroot()
        text = " ".join(
            (node.text or "").strip()
            for node in root.iter()
            if (node.text or "").strip()
        )
        self.assertIn("PROJECT STEWARD · SELF-EVOLVING GOVERNANCE", text)
        self.assertIn("让每一次项目对话", text)
        self.assertIn("改善下一次真实行动", text)
        self.assertIn("吸收成功机制、问题模式与关键细节", text)
        self.assertIn("发生后从根因", text)
        self.assertIn("“从这个会话中进化”", text)
        self.assertIn("“检查内聚、重复与上帝模块”", text)
        self.assertIn("“看懂一个陌生项目”", text)

        for term in (
            "Codex",
            "FOR CODEX",
            "GOVERNANCE CHAIN",
            "SOURCE OF TRUTH",
            "FULL MIGRATION",
            "全面审计",
            "生产者",
            "消费者",
            "唯一真源",
        ):
            with self.subTest(term=term):
                self.assertNotIn(term, text)

        svg_source = HERO_PATH.read_text(encoding="utf-8")
        self.assertNotIn('rx="', svg_source)
        self.assertNotIn("project-card", svg_source)


if __name__ == "__main__":
    unittest.main()
