from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
VISUAL_TEXT = (
    SKILL_ROOT / "references" / "visual-direction.md"
).read_text(encoding="utf-8")
HERO_TEXT = (
    SKILL_ROOT / "references" / "project-native-hero.md"
).read_text(encoding="utf-8")
SVG_TEXT = (
    SKILL_ROOT / "references" / "svg-production.md"
).read_text(encoding="utf-8")
CANVAS_TEXT = (
    SKILL_ROOT / "references" / "github-readme-canvas.md"
).read_text(encoding="utf-8")
HYBRID_TEXT = (
    SKILL_ROOT / "references" / "hybrid-svg-production.md"
).read_text(encoding="utf-8")
MOTION_TEXT = (
    SKILL_ROOT / "references" / "motion-production.md"
).read_text(encoding="utf-8")


class ReadmeVisualGovernanceTests(unittest.TestCase):
    def test_visual_method_owns_the_image_blind_source_boundary(self) -> None:
        self.assertIn("锁定图片盲输入边界", VISUAL_TEXT)
        self.assertIn("事实等级：项目事实充分 / 项目事实不足", VISUAL_TEXT)
        self.assertIn("项目是唯一真源", VISUAL_TEXT)
        self.assertIn(
            "现有、旧版、参考、生成、远程和用户附带的图片全部退出输入集合",
            VISUAL_TEXT,
        )
        self.assertIn(
            "不得打开、查看、截图、渲染、OCR、取色、临摹、比较或分析",
            VISUAL_TEXT,
        )
        self.assertIn("没有明确的非图片家族合同", VISUAL_TEXT)
        self.assertIn("项目就按独立项目处理", VISUAL_TEXT)
        self.assertIn("旧 Logo、现有 hero、机制图、结果图", VISUAL_TEXT)
        self.assertIn("不能给新素材提供母题", VISUAL_TEXT)
        self.assertIn("不让任何图片进入后续步骤", VISUAL_TEXT)

        readme_route = SKILL_TEXT.split("## README 与主页", 1)[1].split(
            "## 许可证治理",
            1,
        )[0]
        delivery_index = readme_route.index("references/readme-delivery.md")
        content_index = readme_route.index("references/content-architecture.md")
        visual_index = readme_route.index("references/visual-direction.md")
        hero_index = readme_route.index("references/project-native-hero.md")
        canvas_index = readme_route.index("references/github-readme-canvas.md")
        svg_index = readme_route.index("references/svg-production.md")
        self.assertLess(delivery_index, content_index)
        self.assertLess(content_index, visual_index)
        self.assertLess(visual_index, hero_index)
        self.assertLess(hero_index, canvas_index)
        self.assertLess(canvas_index, svg_index)

    def test_images_cannot_reenter_through_reuse_or_role_transfer(self) -> None:
        for fragment in (
            "图片排除边界：",
            "保留现有引用但不读取内容",
            "不得向新素材贡献任何表面选择",
            "hero、机制图、结果图和旧 Logo 都不能向它捐赠母题、配色或构图",
            "不得读取当前 SVG、旧 Logo、hero、参考图、截图或生成图",
            "旧源码也不向新设计提供形状、颜色或构图",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, VISUAL_TEXT + HERO_TEXT + SVG_TEXT)

        for retired in ("复用已有 / 制作新的", "已有体系 / 原生材料充分"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, VISUAL_TEXT)

    def test_project_category_no_longer_selects_a_surface_style(self) -> None:
        retired_defaults = (
            "仓库类型 | 可用线索",
            "基础设施、安全、研究、系统和硬件项目可以优先考虑黑白技术方向",
            "大型无衬线标题 + 等宽元数据",
            "分栏：标题一侧",
        )
        combined = VISUAL_TEXT + HERO_TEXT
        for retired in retired_defaults:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, combined)

        self.assertIn("至少两个只用文字描述的候选方向", VISUAL_TEXT)
        self.assertIn("至少有三项实质不同", VISUAL_TEXT)
        self.assertIn("每个候选至少由两项项目特有事实支持", VISUAL_TEXT)
        self.assertIn("仓库类型、技术栈、流行风格", VISUAL_TEXT)
        self.assertIn("不能单独支持", VISUAL_TEXT)
        self.assertIn("语义概念合同", VISUAL_TEXT)
        self.assertIn("冻结几何合同", VISUAL_TEXT)

    def test_logo_discovery_prefers_formal_code_producers(self) -> None:
        for fragment in (
            "先调查项目已有的正式身份源",
            "判断 Logo 缺失、形成新概念或调用任何素材制作方法前",
            "先从真实消费端反查生产者",
            "应用标题栏与外壳",
            "绘图或 Canvas 代码",
            "不能只搜索包含 `logo`、`icon` 或品牌名的文件名",
            "都不是“没有 Logo”的证据",
            "正式身份消费者及入口：",
            "代码或配置生产者：",
            "从代码确定性派生",
            "派生结果必须由测试或等价结构检查与生产者保持同步",
            "调查后确认缺失并新建设计",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, VISUAL_TEXT)

        for fragment in (
            "Logo 正式身份源结论与同步验证：",
            "本页不重新寻找或裁决身份源",
            "优先复用或确定性派生并保留同步验证",
            "只有上游确认身份源缺失时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HERO_TEXT)

    def test_cards_are_selected_by_content_boundaries(self) -> None:
        self.assertIn("从内容关系决定形状", VISUAL_TEXT)
        self.assertIn("多个独立、可比较或本身有明确表面的对象", VISUAL_TEXT)
        self.assertIn("连续阶段使用路径、轴线、编号或渐进空间", VISUAL_TEXT)
        self.assertIn("卡片是一种内容边界", VISUAL_TEXT)
        self.assertIn("活动接口或数据合同确实定义独立容器", VISUAL_TEXT)

    def test_every_surface_value_has_project_provenance(self) -> None:
        self.assertIn("Project basis:", VISUAL_TEXT)
        self.assertIn("Image exclusion:", VISUAL_TEXT)
        for field in (
            "Palette:",
            "Typography:",
            "Composition:",
            "Shape:",
            "Motif:",
            "Density:",
            "Family reuse:",
            "Evidence boundary:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, VISUAL_TEXT)

        self.assertIn("以及各自来源", VISUAL_TEXT)
        self.assertIn("不沿用示范代码、上一项目或任何图片的取值", VISUAL_TEXT)

    def test_svg_skeleton_carries_no_surface_defaults(self) -> None:
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b", SVG_TEXT))
        for retired_fragment in (
            'rx="',
            'id="title-block"',
            'id="project-proof"',
            "translate(56 40)",
            "translate(760 40)",
        ):
            with self.subTest(retired_fragment=retired_fragment):
                self.assertNotIn(retired_fragment, SVG_TEXT)

        self.assertIn('aria-labelledby="title desc"', SVG_TEXT)
        self.assertIn("<title", SVG_TEXT)
        self.assertIn("<desc", SVG_TEXT)
        self.assertIn('id="composition"', SVG_TEXT)
        self.assertIn("背景、位置、圆角、描边、颜色和分组数量来自上游视觉合同", SVG_TEXT)

    def test_hero_and_canvas_use_structural_anti_convergence_checks(self) -> None:
        self.assertIn("去文字语义检查", HERO_TEXT)
        self.assertIn("没有项目事实也成立的技术面板", HERO_TEXT)
        self.assertIn("三步卡片、仪表盘或左右分栏占位结构", HERO_TEXT)
        self.assertIn("同一任务处理多个没有家族合同的项目", HERO_TEXT)
        self.assertIn("不选择背景明暗、配色、字体角色、构图或容器样式", CANVAS_TEXT)
        self.assertIn("不得打开图片做桌面、窄屏或深浅主题预览", CANVAS_TEXT)
        self.assertIn("结构检查不能证明对比度或深浅主题观感", CANVAS_TEXT)

    def test_clickable_and_live_header_content_stays_outside_hero(self) -> None:
        for fragment in (
            "语言切换、文档、贡献、反馈、个人入口、Stars、Forks、许可证",
            "不属于 hero 元数据",
            "不能画进 SVG、PNG 或 WebP",
            "首屏辅助区不能把第一屏挤成只有链接和数字",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HERO_TEXT)

        for fragment in (
            "同一个管理边界按固定顺序生成",
            "Logo、项目名称、本地化一句话介绍、语言与项目导航、个人入口徽章、仓库状态徽章",
            "项目名称和介绍使用普通 HTML 文本",
            "个人与仓库徽章图片都由外层 `<a>` 提供点击目标",
            "语言与项目导航共用一段",
            "文档、贡献和反馈在语言组后使用竖线分隔",
            "当前语言使用文本，其它语言使用真实链接",
            "不依赖徽章服务 URL 中的 `link` 参数",
            "scripts/readme_header.py",
            "语言文件、配置的本地导航目标或许可证文件缺失",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CANVAS_TEXT)

        self.assertIn(
            "完整 README 优化还必须交付一个可在首屏独立使用的 Logo",
            HERO_TEXT,
        )
        self.assertIn(
            "完整优化不能省略 Logo",
            VISUAL_TEXT,
        )

    def test_logo_precedes_expression_visuals_and_full_width_identity_is_rejected(self) -> None:
        for fragment in (
            "Logo 与 hero 是两个职责不同的素材",
            "全宽 hero、机制图、结果图或展示图不能充当 Logo",
            "完整首屏管理区和正向项目定义之后出现",
            "第一个图片节点是否仍是紧凑 Logo",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HERO_TEXT)

        for fragment in (
            "Logo 是 README 的第一个图片节点",
            "identity_image_width` 只接受 `1–480` 的整数",
            "全宽 hero、机制图、结果图和展示图不能作为身份图",
            "全宽 hero、机制图、结果图和展示图属于正文",
            "紧跟所解释章节的引入文字",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CANVAS_TEXT)

        self.assertLess(
            CANVAS_TEXT.index("## 首屏身份与辅助区"),
            CANVAS_TEXT.index("## 表达性视觉的落点"),
        )

    def test_hybrid_and_motion_consumers_cannot_restore_card_defaults(self) -> None:
        self.assertIn("消费已经冻结的非图片项目事实、语义概念、几何合同和视觉合同", HYBRID_TEXT)
        self.assertIn("合同没有网格或容器时不补加", HYBRID_TEXT)
        self.assertIn("不增加卡片、容器、配色或装饰", MOTION_TEXT)
        self.assertIn("图片输入集合为空", HYBRID_TEXT)
        self.assertIn("不打开生成结果", HYBRID_TEXT)
        self.assertIn("不得打开、播放、查看或截图", MOTION_TEXT)
        self.assertIn("不查看 GIF 或帧图", MOTION_TEXT)
        self.assertNotIn('"id": "project-card"', MOTION_TEXT)
        self.assertNotIn("圆角满幅背景", MOTION_TEXT)

    def test_visual_outputs_keep_structural_and_consumer_validation(self) -> None:
        for role in ("结果证据", "机制解释", "身份支持"):
            with self.subTest(role=role):
                self.assertIn(role, VISUAL_TEXT)

        for fragment in (
            "入口、输出合同、数据结构或端到端行为",
            "项目事实不足分支只使用排版、比例和留白",
            "不打开或渲染 SVG",
            "XML 能解析",
            "README、本地文件、提交 blob、远端 raw 内容和 GitHub 页面引用消费同一内容身份",
            "没有进行人工画面判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, VISUAL_TEXT + HERO_TEXT + SVG_TEXT)


if __name__ == "__main__":
    unittest.main()
