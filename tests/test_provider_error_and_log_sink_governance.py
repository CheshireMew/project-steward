from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


SKILL_TEXT = read("SKILL.md")
REMEDIATION_TEXT = read("references/root-cause-remediation.md")
COMPATIBILITY_TEXT = read("references/external-tool-compatibility.md")
LOG_TEXT = read("references/log-audit-standard.md")


class ProviderErrorAndLogSinkGovernanceTests(unittest.TestCase):
    def test_failure_scope_is_preserved_from_producer_to_projection(self) -> None:
        for fragment in (
            "错误作用范围必须由生产者保留",
            "发生阶段、作用范围、稳定操作身份、错误类别",
            "不能由异常文字、出现位置或消费者当前页面反向猜测",
            "局部失败由对应生产者提交带身份的类型化事件",
            "不能覆盖已经成立的启动成功",
            "退出被多种范围共用的通用错误事件",
            "让真实局部生产者失败",
            "手写已经带正确范围的事件只能证明消费者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_attempt_failure_is_reconciled_before_user_notification(self) -> None:
        for fragment in (
            "单次尝试失败不能直接升级为用户可见故障",
            "尝试失败、协调后的当前健康状态和用户通知必须分层",
            "界面只消费协调后的已保存、未保存或失败状态",
            "自动重试资格继续由 `hard-to-reproduce-diagnostics.md` 的精确失败分类拥有",
            "操作本身幂等或部分写入已经受协调",
            "未知或不可重试错误不能因为可能是平台抖动就进入宽限期",
            "失败从未对用户可见时，既不产生失败通知，也不补发恢复通知",
            "才只产生一次恢复结果",
            "关闭流程必须消费仍未保存的权威状态",
            "诊断记录继续消费 `log-audit-standard.md`",
            "瞬时失败后在有限窗口内恢复、重试耗尽、不可重试错误立即失败",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_service_upgrade_preserves_product_availability_contract(
        self,
    ) -> None:
        for fragment in (
            "产品必须保持的可用性合同",
            "是否允许或要求凭据",
            "是否承担默认或零配置能力",
            "上游当前推荐、版本更新或新端点不能自动改写",
            "这不是普通兼容更新，而是新的产品决定",
            "不能为了使用“最新版”先改适配器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_connection_test_reuses_the_production_adapter_contract(
        self,
    ) -> None:
        for fragment in (
            "服务可用性测试必须复用正式调用合同",
            "不是独立探针，而是正式适配器的消费者",
            "流式或非流式模式、响应解析和稳定错误",
            "正式运行使用流式响应而测试只发非流式请求",
            "通过只能证明该探针",
            "不静默尝试多个端点、切换认证方式、关闭流式",
            "运行连接测试，再运行一项代表性正常操作",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_every_promised_log_sink_uses_the_real_runtime_chain(self) -> None:
        for fragment in (
            "日志落点是用户可见合同",
            "每个落点都是独立的正式消费者",
            "控制台承诺要从受支持的正常启动入口捕获真实进程输出",
            "开发命令中的 stdout 通过不能替它背书",
            "改变窗口类型、打包方式、服务宿主或用户启动体验",
            "真实请求构造和 provider serializer 生成最终线请求",
            "记录线协议的受控本地端点",
            "mock 网络返回、直接调用 formatter",
            "每个承诺落点都要在同一次关联链中看见完整请求",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

    def test_transport_success_does_not_replace_background_terminal_state(
        self,
    ) -> None:
        human_log_route = SKILL_TEXT.split("## 人性化日志", 1)[1].split(
            "## 用户环境档案与执行环境", 1
        )[0]
        for reference in (
            "references/log-audit-standard.md",
            "references/durable-operation-governance.md",
            "references/task-progress-governance.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, human_log_route)

        for fragment in (
            "传输结果不代替业务终态",
            "它不证明业务操作成功",
            "接收事件只表达 `request_accepted`、`queued` 或明确拒绝",
            "只有任务生命周期所有者提交的唯一终态",
            "后台终态失败仍按 `ERROR`",
            "高频成功轮询可以在访问日志生产端降级或抑制",
            "轮询错误、状态版本变化、重试、恢复和任务终态必须保留",
            "代码已验证，当前用户实例待重启验证",
            "不能宣称控制台已经修好",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

    def test_diagnostic_evidence_projects_fields_and_redacts_credentials_before_output(
        self,
    ) -> None:
        ordered = (
            "诊断读取先投影再输出",
            "先读取文件身份、schema 和字段名",
            "只输出当前判断需要的允许字段",
            "API Key、访问令牌、认证 header",
            "在进入控制台、工具输出、对话、日志或诊断导出前",
            "原始证据继续留在正式所有者",
        )
        positions = [LOG_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不在发现结构的步骤输出字段值",
            "禁止递归输出未知结构化文件",
            "包括嵌套对象、数组和动态键",
            "不能先输出再依赖下游界面遮盖",
            "本地桌面应用也不把方便诊断解释成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

    def test_existing_routes_and_public_description_consume_the_contracts(
        self,
    ) -> None:
        for reference in (
            "references/root-cause-remediation.md",
            "references/external-tool-compatibility.md",
            "references/log-audit-standard.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, SKILL_TEXT)


    def test_active_rules_do_not_retain_case_specific_evidence(self) -> None:
        combined = REMEDIATION_TEXT + COMPATIBILITY_TEXT + LOG_TEXT
        for fragment in (
            "Lumina",
            "Pollinations",
            "The read operation timed out",
            "160ms",
            "TURN_FAILED",
        ):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, combined)


if __name__ == "__main__":
    unittest.main()
