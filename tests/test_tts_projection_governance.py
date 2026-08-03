from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
LOG_TEXT = (
    SKILL_ROOT / "references" / "log-audit-standard.md"
).read_text(encoding="utf-8")
MODEL_TEXT = (
    SKILL_ROOT / "references" / "model-mediated-operation-governance.md"
).read_text(encoding="utf-8")


class TtsProjectionGovernanceTests(unittest.TestCase):
    def test_tts_requests_route_to_the_log_governance_owner(self) -> None:
        route = SKILL_TEXT.split("## 人性化日志", 1)[1].split(
            "## 用户环境档案与执行环境", 1
        )[0]
        self.assertIn("references/log-audit-standard.md", route)

    def test_consumption_eligibility_precedes_text_cleanup(self) -> None:
        tts_section = LOG_TEXT.split(
            "## 5. TTS 内容资格、清理与重复放大", 1
        )[1].split("## 6. 日志观看体验", 1)[0]
        ordered = (
            "正式消息生产",
            "来源、语义阶段与受众资格",
            "语音投影",
            "文本清理",
            "分段",
            "入队",
            "去重",
            "provider 调用",
            "播放",
        )
        positions = [tts_section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "消费资格必须先于文本清理",
            "系统消息、运行时状态、CLI 或工具原文",
            "不能把原本不合格的消息变成角色语音",
            "先按这些事实判断消费资格",
            "文本清理只能改变合格投影的表现",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT + MODEL_TEXT)

    def test_screen_and_speech_are_projections_of_one_semantic_result(self) -> None:
        for fragment in (
            "同一份已定稿语义结果",
            "屏幕可以保留 emoji、Markdown、链接、文件路径和视觉动作",
            "不是第二套消息真源",
            "变体选择符、肤色、零宽连接组合、旗帜和键帽",
            "流式增量和最终帧使用稳定消息身份与版本收口",
            "不会把已播放内容再入队",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

        self.assertIn("从同一份已定稿语义结果产生明确投影", README_TEXT)
        self.assertIn("TTS provider 只收到应当发声的自然语言", README_TEXT)

    def test_validation_starts_from_formal_message_producers(self) -> None:
        for fragment in (
            "正式消息生产者分别产生可朗读角色回复、不可朗读系统或运行时事件",
            "真实资格 gate、语音投影、分段与队列",
            "记录实际请求的 TTS provider 边界",
            "系统和工具内容没有 provider 调用",
            "屏幕仍保留合同要求的视觉内容",
            "直接调用清理函数、手写已经合格的队列项或 mock 掉资格与队列边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

    def test_model_control_intent_has_one_parser_and_route_scoped_consumers(self) -> None:
        for fragment in (
            "用户语义正文与控制意图属于同一正式响应合同",
            "有类型字段或等价协议通道",
            "动作、表情或其它控制消费者、界面投影和语音投影不能各自解析模型原文",
            "内联控制标记时，标记仍是线协议，不是自然语言",
            "跨分片缓冲、最终 flush",
            "多个控制意图的顺序与冲突语义",
            "普通括号或标点不自动取得控制语义",
            "只进入对话 route 的最终线请求",
            "共享身份提示或公共 prompt builder",
            "执行 `task brief` 没有继承对话控制要求",
            "真实动作消费者、当前界面与 TTS provider 边界读取同一响应身份",
            "直接调用标签解析、文本清理或动作函数不能代替这条链",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MODEL_TEXT)

        for fragment in (
            "动作、表情、显示和语音",
            "聊天专属控制协议不会进入共享身份提示或执行 `task brief`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_reference_remains_cross_project(self) -> None:
        self.assertNotRegex(LOG_TEXT, r"[A-Za-z]:\\")
        for project_specific_term in ("Lumina", "Claude Code", "夜希", "我爱你.txt"):
            with self.subTest(project_specific_term=project_specific_term):
                self.assertNotIn(project_specific_term, LOG_TEXT + MODEL_TEXT)
        self.assertIsNone(re.search(r"task_ack|task_result", LOG_TEXT))


if __name__ == "__main__":
    unittest.main()
