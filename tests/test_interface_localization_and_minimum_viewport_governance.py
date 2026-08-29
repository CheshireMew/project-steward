from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
INTERFACE_TEXT = (
    SKILL_ROOT / "references" / "interface-guidelines.md"
).read_text(encoding="utf-8")
LAYOUT_TEXT = (
    SKILL_ROOT / "references" / "layout-responsive.md"
).read_text(encoding="utf-8")


class InterfaceLocalizationAndMinimumViewportTests(unittest.TestCase):
    def test_visible_localization_covers_dynamic_producers_and_real_surfaces(
        self,
    ) -> None:
        ordered = (
            "登记本轮受影响的全部用户可见文案生产者",
            "静态源字符串提取、翻译目录键数或目录完整性只证明登记的一部分",
            "至少选择一种非默认语言，从自然入口逐项首次打开受影响表面",
            "机器扫描用于发现意外语言泄漏",
            "同一状态的实际画面与真实交互共同证明",
        )
        positions = [INTERFACE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "控制器和展示模型生成的状态或错误",
            "首次访问或延迟创建的窗口、页面和面板",
            "不能证明当前语言的可见界面已经完整",
            "用户内容、品牌名、文件路径和合同允许保留的技术名称逐项分类",
            "扫描零命中、测试夹具通过或尚未打开的延迟表面，都不能单独结项",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERFACE_TEXT)

    def test_declared_minimum_window_is_a_real_acceptance_boundary(self) -> None:
        ordered = (
            "从正式窗口配置与目标平台原生回读取得",
            "结合目标 DPI、系统缩放、标题栏和其它系统占用计算实际内容视口",
            "这组边界是布局与关键任务的必测极值",
            "在最小边界下从自然入口执行关键任务",
            "应修复布局",
            "修改唯一窗口合同并重新验证新的边界",
        )
        positions = [LAYOUT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "开发机默认窗口、显示器分辨率或任意常见宽高不能替代它",
            "不能由实现者为方便验收凭空编一个数字",
            "使用会放大空间压力的目标语言、真实内容和缩放",
            "不能一边保留旧最小值，一边只在更大的测试窗口宣称通过",
            "不能用未经说明地禁止继续缩小代替产品决定",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LAYOUT_TEXT)


if __name__ == "__main__":
    unittest.main()
