from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT_TEXT = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
    encoding="utf-8"
)
REFERENCE_COMPANIONS = {
    "desktop-app-governance.md": ("desktop-window-lifecycle-and-verification.md",),
    "implementation-review.md": ("implementation-review-visual-evidence.md",),
    "interaction-motion.md": ("interaction-navigation-and-media-lifecycle.md",),
    "root-cause-remediation.md": ("root-cause-verification-and-closure.md",),
}


def read_reference(name: str) -> str:
    names = (name, *REFERENCE_COMPANIONS.get(name, ()))
    return "".join(
        (SKILL_ROOT / "references" / current).read_text(encoding="utf-8")
        for current in names
    )


DESIGN_REFERENCES = (
    "surface-registers.md",
    "ux-design.md",
    "task-experience-audit.md",
    "interface-experience-quality.md",
    "design-method.md",
    "layout-responsive.md",
    "interface-guidelines.md",
    "interaction-motion.md",
    "design-system-alignment.md",
    "platform-guidelines.md",
    "implementation-review.md",
    "reference-interface-reconstruction.md",
)
PROJECT_RESEARCH_REFERENCES = (
    "project-research.md",
    "project-effectiveness-review.md",
    "project-research-report.md",
)


class MergedCapabilityTests(unittest.TestCase):
    def test_every_active_reference_has_a_main_route(self) -> None:
        active = {path.name for path in (SKILL_ROOT / "references").glob("*.md")}
        routed = set(re.findall(r"references/([A-Za-z0-9._-]+\.md)", SKILL_TEXT))
        self.assertEqual(active, routed)

    def test_main_router_owns_every_merged_design_resource(self) -> None:
        for name in DESIGN_REFERENCES:
            with self.subTest(name=name):
                self.assertTrue((SKILL_ROOT / "references" / name).is_file())
                self.assertIn(f"references/{name}", SKILL_TEXT)

        self.assertIn(
            "assets/reference-reconstruction/component-spec.md",
            SKILL_TEXT,
        )
        self.assertIn("scripts/context.mjs", SKILL_TEXT)
        retired_name = "design" + "-skill"
        self.assertNotIn(retired_name, SKILL_TEXT)
        self.assertNotIn(f"${retired_name}", SKILL_TEXT)

    def test_merged_references_do_not_reselect_other_references(self) -> None:
        for name in DESIGN_REFERENCES:
            with self.subTest(name=name):
                text = (SKILL_ROOT / "references" / name).read_text(
                    encoding="utf-8"
                )
                self.assertNotIn("references/", text)
                self.assertNotIn("assets/reference", text)
                self.assertNotIn("`SKILL.md`", text)

    def test_distillation_and_ui_governance_have_active_consumers(self) -> None:
        for name in (
            "conversation-learning-and-self-evolution.md",
            "user-environment-governance.md",
            "product-experience-governance.md",
            "interface-problem-patterns.md",
            "local-file-workspace-governance.md",
        ):
            with self.subTest(name=name):
                self.assertTrue((SKILL_ROOT / "references" / name).is_file())
                self.assertIn(f"references/{name}", SKILL_TEXT)

    def test_interface_review_has_a_non_optional_core_route(self) -> None:
        section = SKILL_TEXT.split(
            "## 产品体验与界面治理", 1
        )[1].split("## 仓库建立与发布", 1)[0]
        core_route = section.split("- 从零设计或改变视觉方向", 1)[0]
        readme_section = SKILL_TEXT.split(
            "## README 与主页", 1
        )[1].split("## 许可证治理", 1)[0]

        self.assertIn("固定入口和条件专项", section)
        self.assertNotIn("再按实际任务选择", section)
        self.assertIn(
            "直接负责 UI/UX、界面美观、设计实施与真实画面验收",
            section,
        )
        for owner in (
            "references/product-experience-governance.md",
            "references/ux-design.md",
            "references/interface-experience-quality.md",
            "references/interface-problem-patterns.md",
            "references/implementation-review.md",
        ):
            with self.subTest(core_owner=owner):
                self.assertIn(owner, core_route)

        self.assertIn("窗口、页面、面板、覆盖层、主要状态和用户旅程", core_route)
        self.assertIn("references/desktop-app-governance.md", section)
        self.assertIn("不得因当前反馈只提到颜色、间距或文案", section)
        self.assertIn("references/design-method.md", section)
        self.assertIn("references/surface-registers.md", section)
        self.assertNotIn("references/visual-direction.md", section)
        self.assertIn("references/visual-direction.md", readme_section)

    def test_real_acceptance_validates_runtime_and_business_target_before_launch(
        self,
    ) -> None:
        review = read_reference("implementation-review.md")
        ordered = (
            "真实验收先锁定运行产物与业务目标身份",
            "**运行产物**和**业务目标**作为两个分别成立的身份",
            "只提供历史指针，不得直接成为新一次启动参数",
            "先使用产品正式读取器、只读预检或等价业务合同证明目标可读且身份一致",
            "隔离测试夹具、演示对象和用户当前对象分别登记",
            "在产生应用启动副作用前停止并报告准确缺口",
            "实际运行产物身份、实际业务目标身份和当前可见结果",
        )
        positions = [review.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        all_design_text = "\n".join(
            (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            for name in DESIGN_REFERENCES
        )
        self.assertEqual(
            all_design_text.count("真实验收先锁定运行产物与业务目标身份"),
            1,
        )

    def test_interface_aesthetic_judgment_is_owned_and_not_delegated(
        self,
    ) -> None:
        quality = (
            SKILL_ROOT / "references" / "interface-experience-quality.md"
        ).read_text(encoding="utf-8")
        experience = (
            SKILL_ROOT / "references" / "product-experience-governance.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "界面美观度属于本方法的直接用户结果",
            "承担专业 UI/UX 设计者的判断责任",
            "不得只交付治理报告或组件清单",
            "紧凑、宽松、靠边、留白、卡片、圆角、深浅和信息密度",
            "不是软件感、现代感或专业感的固定同义词",
            "不能从一个感觉词跳到预设风格",
        ):
            with self.subTest(owner="quality", fragment=fragment):
                self.assertIn(fragment, quality)

        for fragment in (
            "视觉与听觉生产仍由相应专业能力负责",
            "这里的生产只指独立图片、视频、三维和音频等媒体",
            "不包含产品界面本身",
            "界面视觉方向、整体美观度、UI/UX 设计、代码实施与真实画面验收",
            "不能借媒体分工停在治理报告",
            "把界面判断推出 Project Steward",
        ):
            with self.subTest(owner="experience", fragment=fragment):
                self.assertIn(fragment, experience)

        self.assertIn("界面美观与 UI/UX", AGENT_TEXT)
        all_active_references = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL_ROOT / "references").glob("*.md")
        )
        self.assertEqual(
            all_active_references.count(
                "界面美观度属于本方法的直接用户结果"
            ),
            1,
        )

    def test_user_environment_resources_have_one_active_route(self) -> None:
        reference = (
            SKILL_ROOT / "references" / "user-environment-governance.md"
        )
        schema = (
            SKILL_ROOT
            / "assets"
            / "user-environment"
            / "profile.schema.json"
        )
        script = SKILL_ROOT / "scripts" / "user_environment_profile.py"

        for path in (reference, schema, script):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

        section = SKILL_TEXT.split(
            "## 用户环境档案与执行环境", 1
        )[1].split("## 项目综合审计", 1)[0]
        for route in (
            "references/user-environment-governance.md",
            "assets/user-environment/profile.schema.json",
            "scripts/user_environment_profile.py",
        ):
            with self.subTest(route=route):
                self.assertIn(route, section)

        self.assertNotIn(
            "references/",
            reference.read_text(encoding="utf-8"),
        )

    def test_desktop_presentation_and_capture_contracts_are_active(self) -> None:
        desktop = read_reference("desktop-app-governance.md")
        for fragment in (
            "窗口呈现状态矩阵",
            "外框尺寸是整个窗口占据的屏幕矩形",
            "系统标题栏、最小化、最大化、关闭按钮和调整大小边缘是平台保留区",
            "用户移动窗口后",
            "A → B → A",
            "屏幕捕获产品的自有窗口可见性",
            "从最终录制产物解码控制窗口所在区域",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, desktop)

        self.assertIn("references/desktop-app-governance.md", SKILL_TEXT)

    def test_human_projection_and_layout_accountability_are_active(
        self,
    ) -> None:
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")
        quality = (
            SKILL_ROOT / "references" / "interface-experience-quality.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "统一的用户显示投影",
            "稳定机器身份",
            "主项或默认项",
            "原始标识留给诊断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guidelines)

        for fragment in (
            "可变长度集合不能拥有固定主行动的可达性",
            "空集合、一个条目和超过首屏的真实数量",
            "同一排序和默认选择语义",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, layout)

        for fragment in (
            "可见元素职责清单",
            "没有职责的元素退出",
            "同组间距使用一致规则",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, quality)

    def test_compact_layout_and_localized_projection_keep_user_contracts(
        self,
    ) -> None:
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "先退出无职责导航、重复容器、并行技术路径、说明和空白",
            "字号、行高、图标光学尺寸和命中范围是保护项",
            "不能把全部元素同比缩小当成紧凑",
            "收紧无职责间距，重排或合并区域",
        ):
            with self.subTest(owner="layout", fragment=fragment):
                self.assertIn(fragment, layout)

        for fragment in (
            "用户标题随当前界面语言从同一显示投影产生",
            "稳定身份、协议键和存储值不翻译",
            "列表、当前选择、任务、历史、错误和重新打开后的回显",
            "不能退回内部 ID、文件名或协议值",
        ):
            with self.subTest(owner="guidelines", fragment=fragment):
                self.assertIn(fragment, guidelines)

        all_design_text = "\n".join(
            (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            for name in DESIGN_REFERENCES
        )
        self.assertEqual(
            all_design_text.count("不能把全部元素同比缩小当成紧凑"),
            1,
        )

    def test_usage_binding_and_reusable_resources_have_distinct_owners(
        self,
    ) -> None:
        ux = (SKILL_ROOT / "references" / "ux-design.md").read_text(
            encoding="utf-8"
        )

        for fragment in (
            "用途绑定与可复用资源分开建模",
            "用户用途：哪类任务需要什么结果",
            "能力载体：哪个模型、CLI、插件、设备或服务能够完成",
            "连接配置只决定“怎样访问这个资源”",
            "当前分工位于资源库或单个详情之外",
            "可执行文件路径、供应商默认地址、环境变量和命令参数",
            "统一能力角色",
            "稳定身份的适配器选项",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ux)

    def test_controls_settings_and_secret_feedback_have_observable_contracts(
        self,
    ) -> None:
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "外部布局矩形、内部内容矩形和真实命中矩形",
            "目标语言长文案、系统文字缩放和显示缩放",
            "不能用负偏移、未经验证的固定坐标",
            "每个应有选项都形成可见、可读、可命中且不被裁切的行",
            "本地、可逆、彼此独立的开关、模式和单项选择",
            "失去焦点、关闭面板或退出应用前强制提交",
            "关闭并重新打开由同一消费者读取",
            "持久原值、编辑缓冲和显示投影",
            "掩码只用于呈现，不能回写成凭据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guidelines)

    def test_visual_quality_diagnosis_separates_design_and_technology(
        self,
    ) -> None:
        design = (
            SKILL_ROOT / "references" / "design-method.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "先从用户结果、对象与内容结构、层级、空间、排版、色彩、组件一致性和运行时完成度",
            "编程语言、UI 框架和渲染方案本身不是审美结论",
            "确实不能满足已经定义的字体、布局、合成、动效、性能、可访问性或系统集成合同",
            "不用“换一种语言会更好看”代替设计与实现判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)

    def test_agent_operated_products_keep_human_and_machine_roles_clear(
        self,
    ) -> None:
        experience = (
            SKILL_ROOT / "references" / "product-experience-governance.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "任务由用户、AI 或 Agent 和确定性系统共同完成时",
            "用户负责表达目标、决定真正影响结果的取舍并审阅后果",
            "AI 或 Agent 负责读取结构化事实、形成带理由的操作计划",
            "公开 CLI 或 API 承担稳定 schema、对象身份、版本、预检和提交",
            "先证明它是正式消费者",
            "不能只通过虚拟化、分页或缓存把无职责表面保留下来",
            "应退出该表面的状态投影、控制器、交互入口和专用恢复分支",
            "人工精细编辑本身具有独立价值时继续保留",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, experience)

    def test_visual_recovery_and_action_content_contracts_are_active(
        self,
    ) -> None:
        design = (
            SKILL_ROOT / "references" / "design-method.md"
        ).read_text(encoding="utf-8")
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "最近一次被接受的界面重新成为当前改版基线",
            "被否定方案退出活动设计",
            "与保留基线混成第三套界面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)

        for fragment in (
            "用于说明类别或用途的上下文",
            "不自动成为界面标签",
            "是否获准改变容器尺寸或视觉",
            "不自动改变已接受容器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guidelines)

    def test_perceptual_layer_and_icon_family_contracts_are_active(
        self,
    ) -> None:
        quality = (
            SKILL_ROOT / "references" / "interface-experience-quality.md"
        ).read_text(encoding="utf-8")
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        review = read_reference("implementation-review.md")

        for fragment in (
            "先锁定用户感受所在的感知层",
            "仍可能的竞争解释",
            "不能因为用户提到“现代”就直接选择换色",
            "不因局部纠正重开整体改版",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, quality)

        for fragment in (
            "图标是独立的视觉组件家族",
            "名义图形尺寸与光学边界",
            "独立的按钮命中范围",
            "扩大按钮边界，不按同一比例放大图形和线宽",
            "共享图标与状态来源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guidelines)

        for fragment in (
            "自动断言只能证明结构约束已生效",
            "整体画面和实际显示尺度的代表性局部画面",
            "任一尺度通过都不能替另一尺度通过",
            "哪些主观目标仍等待用户接受",
            "不把“现代、轻量、舒服、美观或与参考一致”写成已证明结论",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, review)

    def test_interface_polish_contracts_have_unique_active_owners(
        self,
    ) -> None:
        quality = (
            SKILL_ROOT / "references" / "interface-experience-quality.md"
        ).read_text(encoding="utf-8")
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        interaction = read_reference("interaction-motion.md")
        review = read_reference("implementation-review.md")

        for fragment in (
            "让检查范围和取舍可以复核",
            "未覆盖部分及原因",
            "真正考虑但没有采用的边界候选",
            "“阻断”“需要调整”或“可接受”",
        ):
            with self.subTest(owner="quality", fragment=fragment):
                self.assertIn(fragment, quality)

        for fragment in (
            "等宽数字能力",
            "保持同心关系",
            "阴影优先表达高度",
            "扩大后的相邻命中矩形不得重叠",
            "支持从右到左界面时按语义",
            "共享图标自身能够修正时不让每个消费者各自追加边距",
        ):
            with self.subTest(owner="guidelines", fragment=fragment):
                self.assertIn(fragment, guidelines)

        for fragment in (
            "Web 动效实现服从现有系统",
            "不能为了一个细节引入第二套样式写法",
            "不使用 `transition: all`",
            "不能写成 `all`",
            "不把示例数值升级成跨项目默认",
        ):
            with self.subTest(owner="interaction", fragment=fragment):
                self.assertIn(fragment, interaction)

        for fragment in (
            "动效在正常速度与慢放中分别验收",
            "减速播放、逐帧、filmstrip 或录屏回放",
            "减速工具只改变观察方式",
            "回到正常速度完成同一任务",
        ):
            with self.subTest(owner="review", fragment=fragment):
                self.assertIn(fragment, review)

        headings = (
            "让检查范围和取舍可以复核",
            "Web 动效实现服从现有系统",
            "动效在正常速度与慢放中分别验收",
        )
        all_design_text = "\n".join(
            (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            for name in DESIGN_REFERENCES
        )
        for heading in headings:
            with self.subTest(unique_owner=heading):
                self.assertEqual(all_design_text.count(heading), 1)

    def test_ui_automation_uses_stable_identity_and_design_truth(self) -> None:
        review = read_reference("implementation-review.md")

        ordered = (
            "对象身份优先来自稳定对象标识、可访问语义或组件公开身份",
            "当前翻译文案、列表位置和临时像素坐标",
            "不能充当其它行为的定位键",
            "设计值从活动 token、组件公开属性或正式布局合同取得",
            "不能把当前像素常量复制进测试形成第二套设计真源",
            "几何断言验证边界和关系",
            "整体与局部画面验证可读性、视觉重量和构图",
            "共享组件修改还要覆盖全部正式消费者",
            "实例级覆盖则证明共享默认值未被改变",
        )
        positions = [review.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_media_surface_governance_is_routed_and_observable(self) -> None:
        root_cause = read_reference("root-cause-remediation.md")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")
        patterns = (
            SKILL_ROOT / "references" / "interface-problem-patterns.md"
        ).read_text(encoding="utf-8")
        review = read_reference("implementation-review.md")
        desktop = read_reference("desktop-app-governance.md")

        self.assertIn(
            "references/root-cause-remediation.md",
            SKILL_TEXT,
        )
        for fragment in (
            "源媒体或正式素材",
            "输出尺寸与比例契约",
            "渲染表面的逻辑尺寸与物理像素",
            "布局容器与外壳空间预算",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, root_cause)

        self.assertIn("媒体预览同时区分四层几何", layout)
        self.assertIn("标题栏、导航、状态提示或固定操作", layout)
        self.assertIn(
            "媒体内容、渲染表面与布局容器混为一层",
            patterns,
        )
        self.assertIn("播放、定位或其它实际消费动作", review)
        self.assertIn("程序化调用或自动化 `Invoke`", desktop)
        self.assertIn("真实指针点击验证命中", desktop)

    def test_scope_visual_media_and_process_contracts_are_active(self) -> None:
        experience = (
            SKILL_ROOT / "references" / "product-experience-governance.md"
        ).read_text(encoding="utf-8")
        guidelines = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        review = read_reference("implementation-review.md")
        design_system = (
            SKILL_ROOT / "references" / "design-system-alignment.md"
        ).read_text(encoding="utf-8")
        platform = (
            SKILL_ROOT / "references" / "platform-guidelines.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "点名对象是查找同类问题的入口，不是完整范围",
            "全面检查不等于全面修改",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, experience)

        self.assertIn("不能自动决定文案语气", guidelines)

        for fragment in (
            "最终占用端点的进程",
            "不能根据启动命令推定所有权",
            "放大构造尺度",
            "实际显示尺度",
            "网页图片的 `complete`",
            "Resource Timing 条目数量",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, review)

        self.assertIn("强缓存消费者", design_system)
        self.assertIn("扩展注入内容", platform)
        self.assertIn("不通过破坏语义标记", platform)

    def test_visual_acceptance_classifies_browser_runtime_diagnostics(self) -> None:
        visual = (
            SKILL_ROOT
            / "references"
            / "implementation-review-visual-evidence.md"
        ).read_text(encoding="utf-8")
        for fragment in (
            "浏览器运行诊断与画面一起收口",
            "页面导航和首次交互前订阅",
            "控制台 `error`",
            "未捕获的页面异常",
            "产品拥有的运行错误",
            "验证器失败",
            "无关宿主噪声",
            "不自动判为产品缺陷",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, visual)

    def test_clean_and_deliberate_hover_visual_evidence_are_distinct(self) -> None:
        visual = read_reference("implementation-review.md")
        ordered = (
            "默认或干净状态画面前",
            "真实指针移到不触发控件的中性区域",
            "等待 tooltip、hover card、菜单和其它瞬态表面按合同关闭",
            "记录指针位置、焦点所有者和仍可见的瞬态表面",
            "省略号、截断或长文本执行有意悬停",
            "边界、换行、屏幕边缘避让、遮挡范围、关闭条件和焦点恢复",
            "中性截图与有意悬停截图证明不同状态",
        )
        positions = [visual.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_collection_preview_and_reorder_contracts_are_active(self) -> None:
        interaction = read_reference("interaction-motion.md")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")
        review = read_reference("implementation-review.md")

        for fragment in (
            "已提交选择",
            "人工临时预览",
            "系统临时预览",
            "人工临时预览 ?? 系统临时预览 ?? 已提交选择",
            "系统轮动不能改写已提交选择",
            "系统临时预览只从本轮样本取得推进顺序",
            "不能把本轮样本回写成新的内容全集",
            "键盘可见焦点仍在集合内时保持人工接管",
            "粗指针、纯触摸和减少动态效果模式下默认关闭",
            "计时器、事件订阅和系统临时状态随所有者一起创建、重建和清理",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, interaction)

        retired_single_state_rule = (
            "悬停、焦点、点击、回车" + "和触摸更新同一个当前选择"
        )
        self.assertNotIn(retired_single_state_rule, interaction)

        for fragment in (
            "内容全集",
            "本轮样本",
            "当前项",
            "抽样只改变本轮样本",
            "不能用抽样冒充筛选",
            "同一个变更前快照",
            "目标位置有效且不冲突",
            "未移动对象按变更前的相对顺序填入其余位置",
            "不能留下半次重排",
            "序号、默认项、当前选择、读数、预热列表",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, layout)

        for fragment in (
            "人工输入立即接管",
            "已提交选择保持不变",
            "约定的空闲条件满足时恢复",
            "自动演示只消费本轮样本",
            "访问样本外对象",
            "只看到本轮样本按顺序播放，不能证明全集仍可访问",
            "重排前稳定身份顺序",
            "核对精确最终顺序",
            "其它顺序消费者必须读取这份最终顺序",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, review)

    def test_temporal_media_ownership_and_acceptance_are_active(self) -> None:
        interaction = read_reference("interaction-motion.md")
        review = read_reference("implementation-review.md")

        for fragment in (
            "异步切换使用操作身份和原子提交",
            "不能通过随后已经指向新对象的可变 `current` 引用清理",
            "过期回调直接失效",
            "稳定画面最多有一个主视觉对象",
            "建立一个排他操作窗口",
            "从请求通过目标、权限和当前状态检查并被正式接受时开始",
            "鼠标、触摸、滚轮、键盘、自动推进和旧延迟回调",
            "后一稳定状态已经可见、可命中并可继续操作才释放",
            "预热集合为空时状态是 `idle` 或“不适用”",
            "媒体责任矩阵",
            "声音开关只控制责任矩阵中归属于它的声音源",
            "不是“所有视频”共享的全局事实",
            "`advance-on-ended` 必须调用",
            "原生 `loop` 属性只能证明浏览器会重新开始",
            "各编码变体共享同一内容身份、有效播放区间、poster 和接缝合同",
            "连续跨越多个循环边界",
            "一次性过场、引导或故事必须定义消费时点和重置范围",
            "滚动回到页面起点、组件重新挂载和路由恢复不自动等于完整加载",
            "成功路径不能先闪现一个不属于加载合同的旧页面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, interaction)

        for fragment in (
            "时序结果建立逐里程碑证据",
            "自动等待必须绑定本次预期对象、资源和当前活动消费者",
            "排他操作还要从请求刚被接受的时刻开始",
            "到达后一稳定状态后，再证明正常输入已经恢复",
            "预热集合为空，都不能证明目标已经就绪",
            "稳定帧最多存在一个主视觉对象",
            "双重轮廓、非合同内跳变、短暂空白",
            "不能用磁盘上已有的转码文件或请求成功代替消费证据",
            "实际播放速度、起点、默认静音、声音归属",
            "声音入口只应改变责任矩阵分配给它的声音源",
            "每个实际媒体角色或对象级速度、声音、起点、完成与回访覆盖",
            "同一生命周期内滚动返回、组件重建或产品内导航不会重放",
            "过期回调失效、原子可见提交",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, review)

        self.assertIn("references/interaction-motion.md", SKILL_TEXT)
        self.assertIn("references/implementation-review.md", SKILL_TEXT)

    def test_desktop_launch_prewarm_and_audio_modes_have_real_acceptance(
        self,
    ) -> None:
        desktop = read_reference("desktop-app-governance.md")
        review = read_reference("implementation-review.md")

        for fragment in (
            "进程树可见表面合同",
            "不能只隐藏第一层启动器",
            "实际宿主解析并经过正常用户入口执行",
            "昂贵资源准备与活动设备会话分离",
            "被动准备与活动会话",
            "不能借“预热”提前取得这些活动设备和外部副作用",
            "说完后播放模式必须按",
            "播放期间的输出不能再次成为新一段输入",
            "环境噪音不会独立触发播放或形成反馈循环",
        ):
            with self.subTest(owner="desktop", fragment=fragment):
                self.assertIn(fragment, desktop)

        for fragment in (
            "GUI 正常入口、完整进程树及允许和禁止的可见表面",
            "主窗口、辅助窗口、托盘、通知、控制台、终端标签和脚本宿主错误框",
            "活动会话仍是停止状态",
            "不触发开始操作的情况下等待正式准备所有者",
            "环境底噪、短促脉冲和一段有效语音",
            "输出期间不能接受播放声形成的新语段",
            "不能证明回声环路已经断开",
        ):
            with self.subTest(owner="review", fragment=fragment):
                self.assertIn(fragment, review)

        self.assertIn("references/desktop-app-governance.md", SKILL_TEXT)
        self.assertIn("references/implementation-review.md", SKILL_TEXT)

    def test_project_research_capability_is_fully_migrated(self) -> None:
        for name in PROJECT_RESEARCH_REFERENCES:
            with self.subTest(name=name):
                path = SKILL_ROOT / "references" / name
                self.assertTrue(path.is_file())
                self.assertIn(f"references/{name}", SKILL_TEXT)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("references/", text)
                self.assertNotIn("`SKILL.md`", text)

        archive_script = (
            SKILL_ROOT / "scripts" / "extract_project_archive.ps1"
        )
        self.assertTrue(archive_script.is_file())
        self.assertIn(
            "scripts/extract_project_archive.ps1",
            SKILL_TEXT,
        )
        script_text = archive_script.read_text(encoding="utf-8")
        research_section = SKILL_TEXT.split(
            "## 项目研究与讲解", 1
        )[1].split("## 项目基线与模板", 1)[0]
        self.assertIn(
            "[Parameter(Mandatory = $true, Position = 1)]",
            script_text,
        )
        self.assertNotIn(".project-steward-extracted", script_text)
        self.assertNotIn(
            r"E:\Work\BaiduSyncdisk\Code\Example",
            script_text,
        )
        self.assertIn(
            r"E:\Work\BaiduSyncdisk\Code\Example",
            research_section,
        )
        self.assertIn("-DestinationRoot <目标根>", research_section)


if __name__ == "__main__":
    unittest.main()
