from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


SKILL_TEXT = read("SKILL.md")
README_TEXT = read("README.md")
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

        for fragment in (
            "局部超时不会被显示成启动失败",
            "连接测试也必须复用正式运行的适配器",
            "控制台、日志文件、查看器和诊断导出分别是正式日志消费者",
            "开发 stdout 不替原生产物背书",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

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
