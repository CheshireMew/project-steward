from __future__ import annotations

from governance_text_fixtures import *


class DesktopWindowTopologyAndEntryGovernanceTests(unittest.TestCase):
    def test_multi_window_states_are_verified_as_one_visible_composition(
        self,
    ) -> None:
        for fragment in (
            "多窗口工作流按用户状态登记",
            "必须同时可见的顶层窗口",
            "最小可用尺寸、允许重叠、主窗尺寸和关闭去向",
            "从自然按钮打开后同时证明各窗可用",
            "主窗未被布局挤压",
            "对象存在、`visible = true` 或单窗截图不能证明组合",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

    def test_daily_entry_and_single_instance_use_the_production_boundary(
        self,
    ) -> None:
        for fragment in (
            "日常入口只启动已就绪产品",
            "不隐式重演配置、构建或部署",
            "分别测首次准备、冷启动和重复启动",
            "单实例把排他所有权与二次启动激活分开",
            "并发运行两个生产入口",
            "只有一个主实例及一组窗口和子进程",
            "第二次只移交或激活",
            "退出后锁可重取",
            "IPC 名称存在不证明排他",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

    def test_preview_evidence_rejects_wrong_or_information_free_frames(
        self,
    ) -> None:
        for fragment in (
            "请求的稳定来源身份、实际捕获或解码来源和画面信息内容",
            "黑屏、纯色、陈旧帧或错误对象",
            "准确来源不可得时显示明确的不可用状态",
            "不能用可能被遮挡、属于其它窗口或其它显示器的桌面像素冒充目标预览",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


if __name__ == "__main__":
    unittest.main()
