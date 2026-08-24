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
REMEDIATION_TEXT = "".join(
    (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
    for name in (
        "root-cause-remediation.md",
        "root-cause-verification-and-closure.md",
    )
)
CI_TEXT = (
    SKILL_ROOT / "references" / "ci-execution-governance.md"
).read_text(encoding="utf-8")
USER_ENVIRONMENT_TEXT = (
    SKILL_ROOT / "references" / "user-environment-governance.md"
).read_text(encoding="utf-8")


class ExecutionBoundaryGovernanceTests(unittest.TestCase):
    def test_loaded_method_identity_is_revalidated_at_resume_and_completion(
        self,
    ) -> None:
        boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        identity_rule = boundaries.split("记录 Skill 与方法的内容身份", 1)[1]
        ordered = (
            "自动续跑",
            "压缩恢复",
            "结项前复核",
            "只重读变化文件",
            "旧确认失效",
            "重新规划并确认",
        )
        positions = [identity_rule.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_desktop_audit_remediation_loads_specialization_before_work(self) -> None:
        route = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]
        ordered = (
            "写入前读 `references/project-audit.md`",
            "`references/change-prevention.md`",
            "账本合格才写",
            "桌面、移动或归档叠加 `references/desktop-app-governance.md`",
            "无关审计不扩张单点范围",
        )
        positions = [route.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
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
            "验证命令先固定正式身份",
            "多轮证据不重复累计",
            "临时根由正式消费者决定",
        ):
            with self.subTest(fragment=fragment):
                self.assertEqual(
                    sum(text.count(fragment) for text in reference_texts),
                    1,
                )

    def test_root_cause_route_loads_environment_governance_for_background_work(
        self,
    ) -> None:
        route = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        self.assertIn("后台、跨观察窗口任务、路径或执行环境", route)
        self.assertIn("references/user-environment-governance.md", route)

    def test_project_commands_freeze_the_effective_child_runtime(self) -> None:
        section = USER_ENVIRONMENT_TEXT.split(
            "### 正式项目命令先固定任务级执行环境", 1
        )[1].split("## 5. 包、缓存与安装位置", 1)[0]
        for fragment in (
            "解释器、包装器、PATH 变化、工作目录",
            "包存储与缓存根",
            "包装器的绝对路径不能证明子进程使用了同一解释器",
            "通过同一个正式包装入口",
            "子进程实际可执行文件与版本",
            "整项任务复用同一组执行环境",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_package_manager_side_effects_need_install_authority(self) -> None:
        section = USER_ENVIRONMENT_TEXT.split(
            "### 正式项目命令先固定任务级执行环境", 1
        )[1].split("## 5. 包、缓存与安装位置", 1)[0]
        for fragment in (
            "`exec`、临时下载、依赖安装、工作区重连或链接重建",
            "没有安装授权时不得调用",
            "锁文件、工作树、包链接和缓存或存储根",
            "只能作为诊断或聚焦检查",
            "不能冒充正式项目命令已经通过",
            "直接调用内部脚本绕过版本门",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_temporary_roots_follow_their_formal_consumer(self) -> None:
        section = PREVENTION_TEXT.split(
            "### 受限执行路径与临时产物",
            1,
        )[1].split("### 大型内容默认根先消费用户环境策略", 1)[0]
        ordered = (
            "临时根由正式消费者决定",
            "项目测试、构建或正式项目工具会继续读取的对象",
            "只被浏览器、调试器、执行器或机器环境消费",
            "不进入活动仓库或项目归档",
            "没有删除权限只改变清理终态",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能把环境残留改称项目历史", section)
        self.assertIn("普通工具能够直接完成动作且不会建立这些产物", section)
        self.assertIn("不增加临时流程", section)

    def test_static_verifiers_use_the_formal_project_command_identity(self) -> None:
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        ordered = (
            "首测前固定正式 runner",
            "预期关键测试身份",
            "测试框架实际收集的唯一身份",
            "缺失或非唯一身份即停批",
            "标为未覆盖",
        )
        positions = [shared.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "项目配置、正式包装脚本或默认命令",
            "准确工作目录、runner、默认输入范围",
            "临时增加路径参数、从其它目录调用或绕过包装器属于另一命令身份",
            "验证器或前置条件失败",
            "不能为迁就错误验证入口修改产品",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_validation_totals_deduplicate_actual_test_identities(self) -> None:
        for fragment in (
            "每次运行身份、实际选择的唯一测试节点和结果",
            "总覆盖只能按唯一测试节点去重",
            "不能相加成新增覆盖",
            "架构测试、功能测试、静态检查和用户链不能因汇报方便互相改名",
            "未知重叠",
            "不给出虚假的累计总数",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

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
