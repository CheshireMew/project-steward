from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """Select one complete Markdown section, not a global phrase match."""
    level = len(heading) - len(heading.lstrip("#"))
    matches = list(re.finditer(rf"^{re.escape(heading)}$", text, re.MULTILINE))
    if len(matches) != 1:
        raise AssertionError(f"Expected one heading: {heading}")
    remainder = text[matches[0].end():]
    boundary = re.search(rf"^#{{1,{level}}} ", remainder, re.MULTILINE)
    return remainder[:boundary.start()] if boundary else remainder


class BrowserAcceptanceContractTests(unittest.TestCase):
    def test_capability_and_browser_preflight_are_on_the_remediation_route(self):
        route = section(read("SKILL.md"), "## 根因治理")
        matches = [line for line in route.splitlines() if "输入能力" in line]
        self.assertEqual(len(matches), 1)
        self.assertIn("references/interaction-motion.md", matches[0])
        self.assertIn("浏览器验收", matches[0])
        self.assertIn("references/implementation-review.md", matches[0])
        ux = section(read("SKILL.md"), "## 产品体验与界面治理")
        for reference in (
            "implementation-review.md", "interaction-motion.md", "layout-responsive.md"
        ):
            with self.subTest(reference=reference):
                self.assertIn(f"references/{reference}", ux)

    def test_each_method_has_one_owner_and_consumers_resolve_it(self):
        contracts = (
            ("interaction-motion.md", "输入增强按实际能力启用",
             "implementation-review.md"),
            ("implementation-review.md", "浏览器场景先验证实际前提",
             "interaction-motion.md"),
            ("layout-responsive.md", "固定控件先确认实际定位参照",
             "interaction-motion.md"),
        )
        references = SKILL_ROOT / "references"
        for owner, title, consumer in contracts:
            with self.subTest(owner=owner):
                heading = f"### {title}"
                owners = [
                    path.name for path in references.glob("*.md")
                    if heading in path.read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual(owners, [owner])
                section(read(f"references/{owner}"), heading)
                consumer_text = read(f"references/{consumer}")
                self.assertIn(f"`{owner}`", consumer_text)
                self.assertIn(title, consumer_text)
                self.assertNotIn(heading, read("SKILL.md"))

    def test_input_contract_preserves_positive_capability_and_lifecycle(self):
        contract = section(read("references/interaction-motion.md"),
                           "### 输入增强按实际能力启用")
        self.assertNotIn("排他操作窗口", contract)
        self.assertNotIn("### 异步切换", contract)
        for detail in (
            "pointer: fine", "pointer: coarse", "pointer: none", "hover: hover",
            "any-pointer", "当前操作", "减少动态效果", "网络或资源预算",
            "同一生命周期所有者", "订阅相关变化", "保留正式选择",
            "恢复时只重建一份实例",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_preflight_precedes_product_chain_and_rejects_unproven_emulation(self):
        text = read("references/implementation-review.md")
        contract = section(text, "### 浏览器场景先验证实际前提")
        self.assertLess(text.index("### 浏览器场景先验证实际前提"),
                        text.index("## 2. 走真实链路"))
        for detail in (
            "预期条件 → 实际回读 → 选中分支 → 允许结论",
            "工具正式支持", "动作后重新读取实际值",
            "不能在测试中复制一套产品启用规则",
            "通过降级分支不能证明增强分支通过", "不把跳过记为成功",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_page_recovery_preserves_identity_and_background_scenarios(self):
        contract = section(read("references/implementation-review.md"),
                           "### 浏览器场景先验证实际前提")
        for detail in (
            "document.visibilityState", "焦点", "输入驱动的目标",
            "同一浏览器会话所有者", "跟踪本轮新建页面",
            "重新取得并激活原目标", "原目标失效时停止该场景",
            "场景本来验证后台、失焦或隐藏行为时保留这些条件",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_media_transport_probe_is_conditional_and_has_a_real_consumer(self):
        contract = section(read("references/implementation-review.md"),
                           "### 浏览器场景先验证实际前提")
        gate = contract.index("消费者确实依赖字节范围请求时")
        probe = contract.index("有界 Range 探针")
        consumer = contract.index("再由正式播放器执行跳转")
        self.assertLess(gate, probe)
        self.assertLess(probe, consumer)
        for detail in (
            "基础路径", "同一服务的准确资源", "206", "Content-Range",
            "不依赖范围请求的完整下载或直播路径不强制套用该门槛",
            "不能把换服务器后的通过写成原交付方式已通过",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_automation_control_binds_to_the_current_runtime_instance(self):
        text = read("references/implementation-review.md")
        heading = "### 浏览器自动化控制必须绑定当前运行实例"
        contract = section(text, heading)
        owners = [
            path.name for path in (SKILL_ROOT / "references").glob("*.md")
            if heading in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(["implementation-review.md"], owners)
        self.assertLess(text.index(heading), text.index("## 2. 走真实链路"))
        for detail in (
            "页面实际加载的产物或模块代次",
            "同一活动实例",
            "导航、重载、热更新、frame 重建或运行时重新连接后",
            "重新导入同一源路径不能证明取得页面正在使用的实例",
            "不同 module graph、frame、worker、bundle 或缓存",
            "结论是验证器未就绪，不是产品失败或通过",
            "不能修改产品来迁就这份控制链",
            "真实界面输入和正式生产边界",
            "同一活动实例的回读证据",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)

    def test_fixed_controls_distinguish_position_clipping_and_scroll_owners(self):
        contract = section(read("references/layout-responsive.md"),
                           "### 固定控件先确认实际定位参照")
        for detail in (
            "实际包含块、裁切祖先和滚动所有者", "transform", "contain",
            "position: fixed", "z-index", "sticky",
            "不能全局移除", "相关断点两侧", "正反滚动",
            "实际命中结果", "普通内容不引入固定层",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail, contract)


if __name__ == "__main__":
    unittest.main()
