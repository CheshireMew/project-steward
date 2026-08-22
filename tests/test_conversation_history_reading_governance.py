from __future__ import annotations

from governance_text_fixtures import LEARNING_TEXT, unittest


class ConversationHistoryReadingGovernanceTests(unittest.TestCase):
    @staticmethod
    def history_section() -> str:
        return LEARNING_TEXT.split("## 1. 先完整覆盖过程证据", 1)[1].split(
            "## 2. 再按用户最终结果分组",
            1,
        )[0]

    def test_record_layers_close_before_results_are_analyzed(self) -> None:
        section = self.history_section()
        ordered = (
            "冻结本次历史材料边界、准确任务身份和用户要求的时间范围",
            "会话来源先查清宿主原生入口返回哪一层",
            "公开对话账本",
            "过程事件账本",
            "完整性不等于当前权威性",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_top_level_projection_is_not_complete_dialogue_evidence(self) -> None:
        section = self.history_section()
        for fragment in (
            "顶层回合容器、用户可见消息、过程事件、摘要投影或稳定原始记录",
            "`hasMore=false`、没有下一页或顶层回合遍历完成",
            "只能关闭当前返回层",
            "消息列表为空",
            "公开消息被摘要代替",
            "稳定原始会话记录、数据库导出或等价真源",
            "不能用当前上下文、自动摘要、最近几轮、模型记忆或阶段结论补齐",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_public_dialogue_and_process_evidence_are_separate_ledgers(self) -> None:
        section = self.history_section()
        for fragment in (
            "每一条用户可见的用户消息、批注或更正",
            "助手 commentary 和 final",
            "系统与开发者指令、隐藏推理、工具调用和工具输出不是公开对话",
            "事件身份与顺序必须覆盖完整",
            "冗长载荷不整份灌入对话",
            "字段、页、行或字节区间读到可核对末尾",
            "不能把“避免输出淹没”执行成删除失败、等待或范围变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_requested_range_does_not_expand_or_hide_incomplete_sources(self) -> None:
        section = self.history_section()
        for fragment in (
            "用户只要求最近若干消息时，以该范围关闭完整性",
            "不自行升级为完整会话",
            "任何明确必选来源未完成时",
            "不得声称“全部来源”“完整历史”",
            "一个来源没有贡献新问题也必须交账",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


if __name__ == "__main__":
    unittest.main()
