from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
TRANSPORT_TEXT = (
    SKILL_ROOT / "references" / "runtime-message-transport-governance.md"
).read_text(encoding="utf-8")
REMEDIATION_TEXT = (
    SKILL_ROOT / "references" / "root-cause-remediation.md"
).read_text(encoding="utf-8")
PERFORMANCE_TEXT = (
    SKILL_ROOT / "references" / "project-performance-governance.md"
).read_text(encoding="utf-8")


class RuntimeMessageTransportGovernanceTests(unittest.TestCase):
    def test_prevention_route_is_specific_and_owner_is_unique(self) -> None:
        prevention = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        route = "references/runtime-message-transport-governance.md"
        self.assertEqual(1, prevention.count(route))
        for fragment in (
            "IPC、MessagePort、worker 或线程消息",
            "数据表示、传输、首条或终态投递、懒加载监听",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, prevention)

        for exclusion in (
            "普通进程内函数调用",
            "没有消息边界的纯计算优化",
            "只读取已经类型化对象的消费者",
        ):
            with self.subTest(exclusion=exclusion):
                self.assertIn(exclusion, TRANSPORT_TEXT)

    def test_wire_contract_uses_actual_runtime_representation(self) -> None:
        ordered = (
            "目标平台、运行时、框架及准确版本",
            "实际发送 API、允许的数据与 transfer list",
            "接收事件及 event.data 的真实形态",
            "跨 realm 或语言边界的规范化入口",
            "正式消费者与最终用户结果",
        )
        positions = [TRANSPORT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不能从浏览器同名 API",
            "`null`、`undefined`、空载荷、错误类型",
            "当前 realm 的 `instanceof`",
            "控制帧成功掩盖正文缺失",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, TRANSPORT_TEXT)

    def test_consumer_readiness_ack_and_backpressure_are_separate_facts(self) -> None:
        for fragment in (
            "端口创建、连接打开、模块开始加载、监听器注册",
            "由消费者提交 ready 握手后生产者才可发送",
            "有界缓冲并在 ready 后原样排空",
            "不可丢终态不得与可合并遥测共用覆盖槽",
            "ACK 必须声明它确认的是",
            "最大在途消息、单条和累计字节",
            "停止新生产 → 处理或拒绝在途消息",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, TRANSPORT_TEXT)

    def test_actual_target_runtime_precedes_performance_claims(self) -> None:
        ordered = (
            "用最小真实消息从正式生产者",
            "覆盖合法消息",
            "先证明正确性、终态和释放",
            "再测复制次数、在途字节、内存、延迟和吞吐",
        )
        positions = [TRANSPORT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "浏览器 MessageChannel 不能替代 Electron MessagePortMain",
            "直接调用接收 handler",
            "真实往返、资源和用户结果标为未验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, TRANSPORT_TEXT)

    def test_remediation_and_performance_consumers_route_before_workarounds(self) -> None:
        for fragment in (
            "消息事件得到 `null`、空载荷或错误类型",
            "不能只增加空值保护、重试或固定等待",
            "定位第一次改变表示或丢失投递的边界",
            "实际目标运行时往返和终态收口",
        ):
            with self.subTest(remediation_fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        closure = PERFORMANCE_TEXT.split("## 6. 修复交接与二次性能复审", 1)[1]
        ordered = (
            "性能修改新增或替换 IPC、MessagePort、worker 或线程消息通道",
            "先消费 `runtime-message-transport-governance.md`",
            "目标运行时从正式生产者经过实际发送 API 到正式消费者",
            "该链失败时候选保持未冻结",
            "性能修改触及 worker 或辅助进程的缓冲区",
        )
        positions = [closure.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("只能用于诊断，不能证明优化成立", closure)


if __name__ == "__main__":
    unittest.main()
