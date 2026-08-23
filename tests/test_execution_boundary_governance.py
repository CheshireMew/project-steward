from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
PREVENTION_TEXT = "".join(
    (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
    for name in (
        "change-prevention.md",
        "change-prevention-state-and-capability.md",
        "change-prevention-delivery-boundaries.md",
        "change-prevention-verification.md",
    )
)
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
    def test_desktop_audit_remediation_loads_specialization_before_work(self) -> None:
        route = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        for fragment in (
            "桌面项目涉及外壳、原生进程、界面线程、延迟工作、原生窗口或捕获",
            "再读 `references/desktop-app-governance.md`",
            "无关历史审计不扩张单点缺陷范围",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, route)
        self.assertLess(
            route.index("references/change-prevention.md"),
            route.index("references/desktop-app-governance.md"),
        )

    def test_build_profiles_cannot_remove_required_side_effects(self) -> None:
        for fragment in (
            "产生正式结果、改变状态或触发外部副作用的必需动作",
            "不得放在断言、调试断言、诊断专用宏",
            "断言只检查已经发生的事实",
            "会保留和移除该结构的实际配置",
            "Debug 通过不能替 Release 或其它正式 profile 背书",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

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

    def test_state_change_claims_require_the_same_actual_observation_object(
        self,
    ) -> None:
        for fragment in (
            "把前后结果解释为同一路径被外部改写前",
            "每次工具实际收到的字面路径、工作目录和解析后的稳定身份",
            "身份不同的结果只能分别描述各自对象",
            "不能先把同步软件、生成器或其它进程当成已经成立的原因",
            "对象标识的权威发现来源与传递方式",
            "各次输入解析后的稳定对象身份，以及是否相同",
            "身份不同只证明分别查询了不同对象",
            "单次稳定验证没有跨观测比较时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)


if __name__ == "__main__":
    unittest.main()
