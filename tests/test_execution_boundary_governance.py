from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
DESKTOP_TEXT = (
    SKILL_ROOT / "references" / "desktop-app-governance.md"
).read_text(encoding="utf-8")
REMEDIATION_TEXT = (
    SKILL_ROOT / "references" / "root-cause-remediation.md"
).read_text(encoding="utf-8")
CI_TEXT = (
    SKILL_ROOT / "references" / "ci-execution-governance.md"
).read_text(encoding="utf-8")
USER_ENVIRONMENT_TEXT = (
    SKILL_ROOT / "references" / "user-environment-governance.md"
).read_text(encoding="utf-8")


class ExecutionBoundaryGovernanceTests(unittest.TestCase):
    def test_rules_stay_in_reachable_unique_owners(self) -> None:
        self.assertIn("references/desktop-app-governance.md", SKILL_TEXT)
        self.assertIn("references/root-cause-remediation.md", SKILL_TEXT)
        self.assertIn("references/ci-execution-governance.md", SKILL_TEXT)
        self.assertIn("references/user-environment-governance.md", SKILL_TEXT)

        reference_texts = [
            path.read_text(encoding="utf-8")
            for path in (SKILL_ROOT / "references").glob("*.md")
        ]
        for fragment in (
            "线程池、executor 和框架全局工作池只是调度机制",
            "补丁和写入载荷必须来自完整真源",
            "测试的正式启动身份还要包含实际 runner",
            "终止前先区分进程存活与可枚举残留",
        ):
            with self.subTest(fragment=fragment):
                self.assertEqual(
                    sum(text.count(fragment) for text in reference_texts),
                    1,
                )

    def test_shared_executor_does_not_own_subsystem_lifecycle(self) -> None:
        for fragment in (
            "不是子系统的生命周期所有者",
            "登记自己提交的操作、Future、取消和结果投递",
            "等待整个共享池会把无关工作绑进本子系统的关闭",
            "观察共享池空闲也不能证明本子系统的结果已经交付",
            "自有执行器或能够登记全部派生工作的窄调度器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        acceptance = DESKTOP_TEXT.split("## 11. 实机验收", 1)[1]
        self.assertIn("受控的无关长任务", acceptance)
        self.assertIn("只等待并收口自己的登记项和结果投递", acceptance)

    def test_incomplete_tool_output_cannot_become_a_write_payload(self) -> None:
        section = REMEDIATION_TEXT.split(
            "### 补丁和写入载荷必须来自完整真源", 1
        )[1].split("修复请求明确指向", 1)[0]
        for fragment in (
            "只是可观察投影，不再自动等于完整真源",
            "截断、省略、下一页游标、未读区间、输出预算耗尽",
            "不得把它复制、拼接或转交给补丁和写入工具",
            "从实际文件、正式生成器或稳定的行、字节、页和游标区间读取到明确末尾",
            "不能把展示层回显的候选文本当作源文件绕一圈写回",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_patch_target_and_actual_diff_are_verified(self) -> None:
        section = REMEDIATION_TEXT.split(
            "### 补丁和写入载荷必须来自完整真源", 1
        )[1].split("修复请求明确指向", 1)[0]
        ordered = (
            "应用补丁前固定准确目标路径",
            "相同字面量出现多次时",
            "应用后从磁盘重新读取实际差异和受影响文件",
            "再运行对应解析、编译或正式消费者验证",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能因工具报告“应用成功”", section)
        self.assertIn("后续测试的偶然成功", section)

    def test_formal_test_identity_prevents_gui_loader_dialogs(self) -> None:
        section = CI_TEXT.split("### 测试命令先展开再取得运行资格", 1)[1]
        for fragment in (
            "实际 runner 或包装入口",
            "动态库、插件与运行时模块搜索根",
            "直接双击或从终端运行 runner 生成的桌面测试可执行文件不能替代正式入口",
            "在进入 `main()` 和测试框架日志之前",
            "由系统加载器弹出模态错误框",
            "不打包”只排除安装包和可分发目录",
            "不规定把全部运行库一律复制到输出目录",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_process_liveness_is_classified_before_escalation(self) -> None:
        section = USER_ENVIRONMENT_TEXT.split(
            "### 终止前先区分进程存活与可枚举残留", 1
        )[1]
        for fragment in (
            "正在运行”“已经退出但仍可枚举的残留”或“状态未知",
            "仍返回一行记录，只证明系统还能枚举该对象",
            "访问被拒绝”只证明当前调用缺少终止权限",
            "不重复提权",
            "不为清掉一行记录而终止父进程、宿主或整个会话",
            "不能对用户声称已经关闭",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


if __name__ == "__main__":
    unittest.main()
