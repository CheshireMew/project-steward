from __future__ import annotations

from governance_text_fixtures import LEARNING_TEXT, MAIN_TEXT, unittest


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
            "在 Codex 读取完整会话或完整历史时",
            "第一项取证动作固定运行本 Skill 根的 `scripts/read_codex_session.py`",
            "公开对话账本",
            "过程事件账本",
            "完整性不等于当前权威性",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_codex_raw_record_is_first_and_semantic_history_is_supporting_evidence(
        self,
    ) -> None:
        section = self.history_section()
        for fragment in (
            "消费准确的 `CODEX_THREAD_ID` 或 `CODEX_SESSION_ID`",
            "兼容活动写入的共享只读句柄",
            "只保留最后一个完整换行之前的记录",
            "逐行校验 JSON 与内容身份",
            "不得先用普通文件读取、哈希命令、相似标题、最近时间或语义历史探测活动源",
            "一次成功快照是本轮唯一记录真源",
            "只报告脚本的单一结构化失败",
            "语义历史只核对身份或补充投影",
            "其它宿主选择能关闭范围的最强稳定来源",
            "不得声称完整",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)
        self.assertLess(
            section.index("第一项取证动作固定运行本 Skill 根的 `scripts/read_codex_session.py`"),
            section.index("语义历史只核对身份或补充投影"),
        )

    def test_main_router_rejects_an_empty_or_summarized_history_projection(
        self,
    ) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        ordered = (
            "Codex 完整历史先运行本 Skill 的 `scripts/read_codex_session.py`",
            "只读其稳定快照",
            "不先以普通文件命令或语义入口探测活动源",
            "其它宿主选择能关闭范围的最强稳定来源",
            "不得声称完整",
        )
        positions = [shared.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_public_dialogue_and_process_evidence_are_separate_ledgers(self) -> None:
        section = self.history_section()
        for fragment in (
            "从同一快照确定性生成公开对话、上下文来源和过程事件三份 JSONL 投影",
            "路径、数量、内容身份与原记录游标写入清单",
            "兼容新版与旧版公开消息事件",
            "按身份及邻接去重，不按文字合并",
            "保留工具调用和结果关联",
            "格式修复仍读原快照",
            "漏识别不得报零消息成功",
            "隐藏推理不进入投影",
            "未知公共消息结构失败关闭",
            "不得另写 Shell 或行内解释器解析快照",
            "每一条用户可见的用户消息、批注或更正",
            "助手 commentary 和 final",
            "系统与开发者指令、隐藏推理、工具调用和工具输出不是公开对话",
            "事件身份与顺序必须覆盖完整",
            "冗长载荷不整份灌入对话",
            "按投影的原记录游标",
            "字段、页、行或字节区间读到可核对末尾",
            "不能把“避免输出淹没”执行成删除失败、等待或范围变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_transport_user_role_does_not_grant_user_authority(self) -> None:
        section = self.history_section()
        for fragment in (
            "传输层的 `role=user` 不能单独证明是用户原话",
            "宿主注入的环境、Skill、插件或上下文",
            "单列为上下文来源",
            "不得作为用户请求、确认或动作授权",
            "用户可见且可归因的消息事件或宿主作者元数据",
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
