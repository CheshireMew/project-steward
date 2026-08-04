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
    def test_visual_method_owns_the_visual_evidence_decision(self) -> None:
        self.assertIn("建立视觉证据合同", VISUAL_TEXT)
        self.assertIn("证据等级：已有体系 / 原生材料充分 / 证据不足", VISUAL_TEXT)
        self.assertIn("按证据等级选择一次视觉路径", VISUAL_TEXT)
        self.assertIn(
            "当前 README 视觉、仓库内部图片和同批次生成的素材无论数量多少",
            VISUAL_TEXT,
        )
        self.assertIn("证明项目已有视觉体系", VISUAL_TEXT)
        self.assertIn("没有明确家族合同的项目按独立项目处理", VISUAL_TEXT)
        self.assertIn("才能进入视觉合同", VISUAL_TEXT)
        self.assertIn("不重新选择证据等级或恢复已退出材料", VISUAL_TEXT)

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

    def test_existing_visuals_require_current_source_qualification(self) -> None:
        for fragment in (
            "合格项目证据与适用状态：",
            "不采用材料及原因：",
            "只有上层已经核定来源、适用项目状态和公开职责的材料才能选择“复用已有”",
            "文件存在、链接有效、画面完整或曾在 README 出现都不构成复用资格",
            "Material basis:",
            "不恢复内容方法已经判定为过时或未验证的产物",
            "内部图片、旧截图或历史流程图不因文件存在而重新获得资格",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, VISUAL_TEXT + HERO_TEXT)

        self.assertIn(
            "整页模式必须明确选择复用已有、制作新的、排版表达或跳过",
            VISUAL_TEXT,
        )

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

        self.assertIn("至少两个候选方向", VISUAL_TEXT)
        self.assertIn("至少有三项实质不同", VISUAL_TEXT)
        self.assertIn("每个候选至少由两项项目特有证据支持", VISUAL_TEXT)
        self.assertIn("仓库类型、技术栈、流行风格", VISUAL_TEXT)
        self.assertIn("不能单独支持", VISUAL_TEXT)

    def test_cards_are_selected_by_content_boundaries(self) -> None:
        self.assertIn("从内容关系决定形状", VISUAL_TEXT)
        self.assertIn("多个独立、可比较或本身有明确表面的对象", VISUAL_TEXT)
        self.assertIn("连续阶段使用路径、轴线、编号或渐进空间", VISUAL_TEXT)
        self.assertIn("卡片是一种内容边界", VISUAL_TEXT)
        self.assertIn("真实界面本身采用卡片时，可以保留", VISUAL_TEXT)

    def test_every_surface_value_has_project_provenance(self) -> None:
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
        self.assertIn("不沿用示范代码或上一项目的取值", VISUAL_TEXT)

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

    def test_hero_and_canvas_expose_observable_anti_convergence_checks(self) -> None:
        self.assertIn("去文字轮廓检查", HERO_TEXT)
        self.assertIn("没有项目材料也成立的技术面板", HERO_TEXT)
        self.assertIn("三步卡片、仪表盘或左右分栏占位结构", HERO_TEXT)
        self.assertIn("同一任务处理多个没有家族合同的项目", HERO_TEXT)
        self.assertIn("不选择背景明暗、配色、字体角色、构图或容器样式", CANVAS_TEXT)
        self.assertIn("背景可以是浅色、深色或经双主题验证的透明表面", CANVAS_TEXT)

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
            "语言与项目导航共用第一段",
            "文档、贡献和反馈在语言组后使用竖线分隔",
            "当前语言使用文本，其它语言使用真实链接",
            "徽章图片由外层 `<a>` 提供点击目标",
            "不依赖徽章服务 URL 中的 `link` 参数",
            "scripts/readme_header.py",
            "语言文件、配置的本地导航目标或许可证文件缺失",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CANVAS_TEXT)

    def test_hybrid_and_motion_consumers_cannot_restore_card_defaults(self) -> None:
        self.assertIn("消费已经选定的视觉合同", HYBRID_TEXT)
        self.assertIn("合同没有网格或容器时不补加", HYBRID_TEXT)
        self.assertIn("不增加卡片、容器、配色或装饰", MOTION_TEXT)
        self.assertNotIn('"id": "project-card"', MOTION_TEXT)
        self.assertNotIn("圆角满幅背景", MOTION_TEXT)

    def test_existing_readme_visual_capabilities_remain_active(self) -> None:
        for role in ("结果证据", "机制解释", "身份支持"):
            with self.subTest(role=role):
                self.assertIn(role, VISUAL_TEXT)

        for fragment in (
            "真实界面、输出、截图、数据图或端到端产物",
            "证据不足分支只使用排版、比例和留白",
            "实际渲染 SVG",
            "`900px` 和 `360px`",
            "GitHub 深浅页面周围的对比度",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, VISUAL_TEXT + HERO_TEXT + SVG_TEXT)


if __name__ == "__main__":
    unittest.main()
