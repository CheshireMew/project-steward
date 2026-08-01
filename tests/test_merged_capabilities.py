from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
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
            "### 14. 用户环境档案与执行环境", 1
        )[1].split("### 15. 项目综合审计", 1)[0]
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
        desktop = (
            SKILL_ROOT / "references" / "desktop-app-governance.md"
        ).read_text(encoding="utf-8")
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

        self.assertIn(
            "窗口呈现状态矩阵",
            SKILL_TEXT,
        )
        self.assertIn(
            "每个自有顶层窗口是否进入录制",
            SKILL_TEXT,
        )

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
        review = (
            SKILL_ROOT / "references" / "implementation-review.md"
        ).read_text(encoding="utf-8")

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

    def test_media_surface_governance_is_routed_and_observable(self) -> None:
        root_cause = (
            SKILL_ROOT / "references" / "root-cause-remediation.md"
        ).read_text(encoding="utf-8")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")
        patterns = (
            SKILL_ROOT / "references" / "interface-problem-patterns.md"
        ).read_text(encoding="utf-8")
        review = (
            SKILL_ROOT / "references" / "implementation-review.md"
        ).read_text(encoding="utf-8")
        desktop = (
            SKILL_ROOT / "references" / "desktop-app-governance.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "媒体预览表现为内容缺失、裁切或比例留白且边界不清",
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
        review = (
            SKILL_ROOT / "references" / "implementation-review.md"
        ).read_text(encoding="utf-8")
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

    def test_collection_preview_and_reorder_contracts_are_active(self) -> None:
        interaction = (
            SKILL_ROOT / "references" / "interaction-motion.md"
        ).read_text(encoding="utf-8")
        layout = (
            SKILL_ROOT / "references" / "layout-responsive.md"
        ).read_text(encoding="utf-8")
        review = (
            SKILL_ROOT / "references" / "implementation-review.md"
        ).read_text(encoding="utf-8")

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
        interaction = (
            SKILL_ROOT / "references" / "interaction-motion.md"
        ).read_text(encoding="utf-8")
        review = (
            SKILL_ROOT / "references" / "implementation-review.md"
        ).read_text(encoding="utf-8")

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

        for fragment in (
            "集合抽样消费和排他转场",
            "分类播放与声音职责",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

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
            "### 6. 项目研究与讲解", 1
        )[1].split("### 7. 项目基线与模板", 1)[0]
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
