from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
DELIVERY_TEXT = (
    SKILL_ROOT / "references" / "readme-delivery.md"
).read_text(encoding="utf-8")
CONTENT_TEXT = (
    SKILL_ROOT / "references" / "content-architecture.md"
).read_text(encoding="utf-8")
LEARNING_TEXT = (
    SKILL_ROOT / "references" / "conversation-learning-and-self-evolution.md"
).read_text(encoding="utf-8")
LEARNING_TEXT += (
    SKILL_ROOT / "references" / "skill-self-evolution-governance.md"
).read_text(encoding="utf-8")
README_TEXTS = {
    "zh-CN": (SKILL_ROOT / "README.md").read_text(encoding="utf-8"),
    "en": (SKILL_ROOT / "README.en.md").read_text(encoding="utf-8"),
    "ja": (SKILL_ROOT / "README.ja.md").read_text(encoding="utf-8"),
}
HERO_PATH = SKILL_ROOT / "assets" / "readme" / "hero.svg"
HEADER_PROFILE_PATH = (
    SKILL_ROOT / "assets" / "readme-profile" / "profile.json"
)
HEADER_PROFILE_SCHEMA_PATH = (
    SKILL_ROOT / "assets" / "readme-profile" / "profile.schema.json"
)


class ReadmeContentGovernanceTests(unittest.TestCase):
    def test_readme_route_starts_with_the_complete_delivery_owner(self) -> None:
        route = SKILL_TEXT.split("## README 与主页", 1)[1].split(
            "## 许可证治理",
            1,
        )[0]

        ordered = (
            "references/readme-delivery.md",
            "references/content-architecture.md",
            "references/visual-direction.md",
            "references/project-native-hero.md",
            "references/github-readme-canvas.md",
        )
        positions = [route.index(item) for item in ordered]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("references/github-star-history.md", route)
        self.assertIn("references/repository-publication.md", route)
        self.assertIn("scripts/readme_header.py", route)
        self.assertIn("scripts/audit_readme.py", route)
        self.assertIn("scripts/github_topics.py", route)
        self.assertIn("scripts/github_about.py", route)
        self.assertIn("代码优先的正式身份源调查", route)
        self.assertIn("公开 GitHub 仓库完整优化默认交付 Star History、Topics 与 About", route)
        self.assertIn("缺少任一真实消费者的成功结果都不能完成整项交付", route)
        self.assertIn(
            "README 不作为每项内部治理规则的第二份活动真源",
            route,
        )

    def test_delivery_method_owns_the_full_repository_result(self) -> None:
        for field in (
            "准确项目根与上层 Git 边界：",
            "README 是否存在、当前动作与活动语言：",
            "公开安装入口、已验证的最短命令与实际安装验证等级：",
            "项目活动真源与图片排除边界：",
            "Logo 正式生产者、现有消费端、复用 / 派生 / 新建设计结论：",
            "许可证文件、GitHub 识别与权利边界：",
            "Star History 生产者、输出分支、raw 文件与消费端：",
            "GitHub Topics 当前集合、项目事实依据与目标集合：",
            "GitHub About 当前 Description、Website，项目事实依据与目标值：",
            "GitHub Issues、Discussions 与 Release 事实：",
            "本次允许的本地写入、提交、推送和远端元数据动作：",
            "最终停止位置：",
        ):
            with self.subTest(field=field):
                self.assertIn(field, DELIVERY_TEXT)

        for outcome in (
            "当前是否已经初始化 Git",
            "README 不存在时选择新写",
            "设计和写作不打开、查看、渲染、OCR、取色或分析任何图片",
            "配置的完整语言页和贡献指南已经交付",
            "判断 Logo 缺失前已经先调查代码、配置、正式资源声明与消费端",
            "缺少 `README.en.md`、`README.ja.md`",
            "单个项目专属入口不成立时不影响其它组",
            "文档、贡献和反馈分别抵达真实且职责不同的目标",
            "GitHub 识别",
            "零星标仓库可以生成真实的零基线",
            "现有公开 GitHub 仓库的完整 README 优化默认包含 Star History",
            "Topics 是公开 GitHub 仓库完整 README 优化的默认交付项",
            "About Description 是公开 GitHub 仓库完整 README 优化的默认交付项",
            "Website 是有合格目标时才写入的可选字段",
            "远端 HEAD",
            "自动写入全部活动语言 README",
        ):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, DELIVERY_TEXT)

    def test_star_history_is_automatic_and_cannot_be_silently_dropped(self) -> None:
        for fragment in (
            "Star History 是现有公开 GitHub 仓库完整 README 优化的默认交付项",
            "不等待第二次专项请求",
            "只有用户明确退出",
            "不是 GitHub 仓库、不是公开仓库、没有现有远端时才不适用",
            "权限、Actions 或推送失败只能标为受阻",
            "工作流派发成功后停止并把后续层标为异步未验证",
            "只有用户另行要求远端验收时才读取已经完成的链路",
            "不能静默省略",
            "受阻时保留准确的未完成状态",
            "不写空章节、示例图或必然失效的 raw 地址",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

    def test_logo_absence_requires_a_code_first_identity_source_result(self) -> None:
        for fragment in (
            "由 `visual-direction.md` 完成代码优先的正式身份源调查",
            "没有这份结论不得判断 Logo 缺失或开始新设计",
            "找不到名为 logo 的文件",
            "都不能证明 Logo 缺失",
            "代码或配置已经定义标志时优先复用或确定性派生",
            "建立同步验证",
            "只有确认不存在正式生产者和可用消费端后",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

    def test_topics_and_about_are_default_but_values_remain_evidence_bound(self) -> None:
        for fragment in (
            "Topics 是公开 GitHub 仓库完整 README 优化的默认交付项",
            "不能因为 Project Steward 被调用就添加",
            "`codex` 只有在 Codex 确实是项目当前公开的主要运行载体",
            "Topics 随同一完整交付自动写入",
            "About 随同一完整交付自动写入",
            "GitHub API 一次替换",
            "scripts/github_topics.py inspect",
            "scripts/github_topics.py apply",
            "scripts/github_about.py inspect",
            "scripts/github_about.py apply",
            "--clear-website",
            "--expected-head FULL_SHA",
            "api_verified",
            "github_page_verified",
            "metadata_verified",
            "不能用规则文字、测试中的预期集合、一次 PUT 成功",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

        for language, text in README_TEXTS.items():
            with self.subTest(language=language):
                self.assertIn("Topics", text)

    def test_about_description_is_default_but_website_is_optional(self) -> None:
        for fragment in (
            "Description 消费 `content-architecture.md` 已核定的默认语言一句公开定义",
            "保持单行纯文本并与 README 的项目身份一致",
            "Website 是有合格目标时才写入的可选字段",
            "没有合格 Website 是一个成功的目标状态",
            "不为填满字段联网搜索、拼接或猜测网址",
            "不会阻塞 Description 与 About 交付",
            "只读审计先运行 `python scripts/github_about.py inspect",
            "只在交付账本保留目标值，不改变远端",
            "同一次 GitHub API 请求提交 Description 与 Website",
            "从 GitHub 仓库主页的 About 数据回读同一结果",
            "website_destination_validation",
            "caller_qualified_not_checked",
            "not_applicable",
            "`github_page_verified` 只证明 GitHub 仓库页面",
            "不能用方法文字、一次 PATCH 成功",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

        self.assertNotIn(
            "About Description 与 Website 是公开 GitHub 仓库完整 README 优化的默认交付项",
            DELIVERY_TEXT,
        )

    def test_website_requires_an_authoritative_real_user_surface(self) -> None:
        for fragment in (
            "项目活动配置、正式项目导航、部署配置或用户明确指定",
            "第三方目录、技能市场、包注册页、搜索结果或仓库地址",
            "`200`、最终 URL、canonical、页面标题或仓库名相符",
            "404、soft 404、空页、登录或访问门槛",
            "文档、安装、下载或其它明确的第一次采用用途",
            "必须通过真实浏览器核对",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

    def test_star_history_precedes_license_and_attribution_in_every_language(self) -> None:
        legal_headings = {
            "zh-CN": "## 许可证与第三方来源",
            "en": "## License and third-party sources",
            "ja": "## ライセンスと第三者ソース",
        }
        for language, text in README_TEXTS.items():
            with self.subTest(language=language):
                self.assertLess(
                    text.index("## Star History"),
                    text.index(legal_headings[language]),
                )

    def test_text_feedback_preserves_the_other_complete_readme_outputs(self) -> None:
        self.assertIn("只改变正文的写作与验收", DELIVERY_TEXT)
        self.assertIn("不能把对正文的纠正解释为把其它交付改成按需", DELIVERY_TEXT)
        for preserved_output in (
            "语言页",
            "贡献指南",
            "个人入口",
            "仓库状态",
            "许可证",
            "Star History",
            "GitHub Topics",
            "About Description/Website",
        ):
            with self.subTest(preserved_output=preserved_output):
                self.assertIn(preserved_output, DELIVERY_TEXT)

    def test_content_and_learning_methods_forbid_readme_method_mirrors(self) -> None:
        for fragment in (
            "README 不是内部方法的镜像",
            "不会自动成为 README 段落",
            "README 默认不在影响文件中",
            "README 测试只保护上述公开合同与可读性",
            "不能为了让每项内部规则“有公开消费者”",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        for fragment in (
            "公开 README 不是每项内部能力的默认消费者",
            "也不是自我进化日志",
            "不能用 README 原文断言证明内部能力已经迁移",
            "不能因为测试要求公开出现",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_content_method_still_owns_reader_contract_and_deletion(self) -> None:
        for field in (
            "第一采用读者：",
            "首页读者变化：",
            "项目本体与运行载体：",
            "宿主依赖证据与公开身份排除：",
            "到访情境：",
            "交给项目什么：",
            "可观察结果：",
            "第一步：",
            "后续读者：",
            "场景证据：",
            "公开事实与图片排除边界：",
        ):
            with self.subTest(field=field):
                self.assertIn(field, CONTENT_TEXT)

        self.assertIn("采用层材料", CONTENT_TEXT)
        self.assertIn("操作层材料", CONTENT_TEXT)
        self.assertIn("维护层材料", CONTENT_TEXT)
        self.assertIn("普通读者回述测试", CONTENT_TEXT)
        self.assertIn("对每个段落执行删除测试", CONTENT_TEXT)
        for fragment in (
            "不能因一个项目专属目标不同就判定整份 profile 不适用",
            "完整优化时缺少的配置语言是待创建的完整页面",
            "旧页面缺少哪一项就补齐哪一项",
            "完整首屏身份链",
            "本次已存在或新建的真实 `CONTRIBUTING.md`",
            "--navigation-target docs=<活动 Markdown>",
            "不能临时改写 profile",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

    def test_readme_writing_uses_only_project_truth_and_never_reads_images(self) -> None:
        for fragment in (
            "图片退出写作真源",
            "项目是这三类任务的唯一真源",
            "不得打开、查看、截图、渲染、OCR、取色、临摹或分析",
            "不得从图片推断项目事实、主题、结构、语气或措辞",
            "图片内容始终排除",
            "找不到非图片证据就不写",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        for fragment in (
            "项目事实、语义概念、几何合同、素材源码结构",
            "视觉验收不得打开、查看、截图或渲染最终候选",
            "报告必须明确没有进行人工画面判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

    def test_project_definition_rejects_defensive_filler_in_every_language(self) -> None:
        for fragment in (
            "项目定义直接说明项目是什么、接收什么、做什么和交付什么",
            "防御性分类或反事实说明",
            "改变读者的采用选择、安装、操作或结果解释",
            "不能用它给正向定义补尾",
            "全部活动语言执行同一判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        self.assertIn(
            "项目定义是否使用正向事实",
            CONTENT_TEXT,
        )

    def test_optional_host_adapters_cannot_own_agent_skill_identity(self) -> None:
        for fragment in (
            "宿主适配不拥有通用 Skill 身份",
            "适配文件存在、当前恰好由某个 Agent 执行",
            "只证明兼容关系，不证明排他依赖",
            "把项目核定为宿主中立的 Agent Skill",
            "全部活动语言 README",
            "--forbid-public-term <名称>",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTENT_TEXT)

        for fragment in (
            "宿主依赖证据、宿主中立结论与公开身份排除项：",
            "用 `--forbid-public-term` 传给全部活动语言",
            "宿主中立时增加全部活动语言的公开身份排除审计",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DELIVERY_TEXT)

    def test_header_profile_has_one_owner_and_real_consumers(self) -> None:
        profile = json.loads(HEADER_PROFILE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(3, profile["schema_version"])
        self.assertEqual(["CheshireMew"], profile["applies_to"]["github_owners"])
        self.assertEqual(
            ["zh-CN", "en", "ja"],
            [language["code"] for language in profile["languages"]],
        )
        self.assertTrue(profile["languages"][0]["default"])
        self.assertEqual(
            ["docs", "contribute", "feedback"],
            [link["id"] for link in profile["navigation_links"]],
        )
        self.assertEqual(
            ["文档", "贡献", "反馈"],
            [link["label"] for link in profile["navigation_links"]],
        )
        self.assertEqual("project_path", profile["navigation_links"][0]["kind"])
        self.assertNotIn("path", profile["navigation_links"][0])
        self.assertEqual(
            "CONTRIBUTING.md", profile["navigation_links"][1]["path"]
        )
        self.assertEqual(
            ["x", "telegram", "blog", "homepage"],
            [link["id"] for link in profile["social_links"]],
        )
        for link in profile["social_links"]:
            self.assertEqual(
                {"id", "label", "url", "badge_src", "alt"}, set(link)
            )
        self.assertEqual(
            ["stars", "forks", "license"],
            profile["repository_badges"],
        )

        schema = json.loads(
            HEADER_PROFILE_SCHEMA_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(3, schema["properties"]["schema_version"]["const"])
        self.assertEqual(
            ["existing_path", "project_path", "repository_path"],
            schema["properties"]["navigation_links"]["items"]["properties"][
                "kind"
            ]["enum"],
        )
        self.assertEqual(
            ["stars", "forks", "license"],
            schema["properties"]["repository_badges"]["items"]["enum"],
        )

    def test_all_language_pages_are_complete_concise_reader_surfaces(self) -> None:
        current_labels = {
            "zh-CN": "<strong>中文</strong>",
            "en": "<strong>English</strong>",
            "ja": "<strong>日本語</strong>",
        }
        locale_sections = {
            "zh-CN": ("## 它能帮你完成什么", "## 直接这样说", "## 许可证与第三方来源"),
            "en": ("## What it helps you accomplish", "## Say it directly", "## License and third-party sources"),
            "ja": ("## できること", "## そのまま依頼できます", "## ライセンスと第三者ソース"),
        }
        locale_taglines = {
            "zh-CN": "一个帮助你研究和审计项目、预防返工、修复根因，并改善界面设计与使用体验的 Agent Skill。",
            "en": "An Agent Skill for project research and audits, preventing rework, fixing root causes, and improving UI design and usability.",
            "ja": "プロジェクトの調査・監査、手戻りの予防、根本原因の修正、UI デザインと使いやすさの改善を支援する Agent Skill。",
        }

        for language, text in README_TEXTS.items():
            with self.subTest(language=language):
                self.assertLess(len(text), 12000)
                self.assertLess(len(text.splitlines()), 230)
                self.assertIn("./assets/readme/hero.svg", text)
                self.assertIn("<!-- readme-header:start -->", text)
                self.assertIn("<!-- readme-header:end -->", text)
                self.assertTrue(text.startswith("<!-- readme-header:start -->"))
                self.assertEqual(
                    1, text.count('<h1 align="center">Project Steward</h1>')
                )
                self.assertNotIn("\n# Project Steward\n", text)
                logo_index = text.index('./assets/readme/hero.svg')
                name_index = text.index('<h1 align="center">Project Steward</h1>')
                tagline_index = text.index(locale_taglines[language])
                language_index = text.index(current_labels[language])
                social_index = text.index("img.shields.io/badge/X-")
                repository_index = text.index(
                    "github/stars/CheshireMew/project-steward"
                )
                self.assertLess(logo_index, name_index)
                self.assertLess(name_index, tagline_index)
                self.assertLess(tagline_index, language_index)
                self.assertLess(language_index, social_index)
                self.assertLess(social_index, repository_index)
                self.assertIn(current_labels[language], text)
                self.assertIn('./SKILL.md">文档</a>', text)
                self.assertIn('./CONTRIBUTING.md">贡献</a>', text)
                self.assertIn(
                    'https://github.com/CheshireMew/project-steward/issues">反馈</a>',
                    text,
                )
                self.assertIn("https://x.com/0xCheshire", text)
                self.assertIn("https://t.me/CheshireBTC", text)
                self.assertIn("博客：blog.blacknico.com", text)
                self.assertIn("个人主页：blacknico.com", text)
                self.assertIn("img.shields.io/badge/X-", text)
                self.assertIn("github/stars/CheshireMew/project-steward", text)
                self.assertIn("github/forks/CheshireMew/project-steward", text)
                self.assertIn("github/license/CheshireMew/project-steward", text)
                self.assertIn("--navigation-target docs=SKILL.md", text)
                self.assertIn("--identity-image assets/readme/hero.svg", text)
                self.assertIn(
                    "npx skills add CheshireMew/project-steward",
                    text,
                )
                self.assertIn("## Star History", text)
                self.assertIn(
                    "raw.githubusercontent.com/CheshireMew/project-steward/star-history",
                    text,
                )
                self.assertIn("./LICENSE", text)
                for heading in locale_sections[language]:
                    self.assertIn(heading, text)

    def test_public_pages_keep_stable_outcomes_without_internal_rule_walls(self) -> None:
        chinese = README_TEXTS["zh-CN"]
        for public_entry in (
            "从真实工作中进化",
            "在动手前预防返工",
            "问题发生后沿根因收口",
            "看懂或治理一个仓库",
            "优化 README",
            "README 完整优化会做什么",
        ):
            with self.subTest(public_entry=public_entry):
                self.assertIn(public_entry, chinese)

        for retired_wall in (
            "## 它怎样从对话中进化",
            "## 持久操作与恢复",
            "## 架构内聚、重复与上帝模块",
            "## 用户环境档案与执行环境",
            "## 其它项目能力",
            "全面审计会先建立维度覆盖账本",
            "来源只有读到明确末尾才算完整",
            "当前真实支持的参考输入",
        ):
            with self.subTest(retired_wall=retired_wall):
                self.assertNotIn(retired_wall, chinese)

    def test_shared_logo_is_language_neutral_and_project_specific(self) -> None:
        root = ET.parse(HERO_PATH).getroot()
        text = " ".join(
            (node.text or "").strip()
            for node in root.iter()
            if (node.text or "").strip()
        )
        self.assertIn("Project Steward logo", text)
        self.assertIn("A deep green shield with a white two-leaf sprout", text)

        self.assertIsNone(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text))
        source = HERO_PATH.read_text(encoding="utf-8")
        self.assertIn('id="steward-sprout"', source)
        self.assertIn('id="steward-boundary"', source)
        self.assertIn('viewBox="0 0 240 240"', source)
        self.assertNotIn("<text", source)
        self.assertNotIn('rx="', source)
        self.assertNotIn("project-card", source)

    def test_license_and_attribution_remain_public(self) -> None:
        for text in README_TEXTS.values():
            self.assertIn("Mozilla Public License 2.0", text)
            self.assertIn(
                "https://github.com/oil-oil/beautify-github-readme",
                text,
            )
            self.assertIn("THIRD_PARTY_NOTICES.md", text)
            self.assertIn("NOTICE", text)


if __name__ == "__main__":
    unittest.main()
