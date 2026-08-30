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
DESKTOP_TEXT += (
    SKILL_ROOT
    / "references"
    / "desktop-window-lifecycle-and-verification.md"
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

    def test_authorization_is_attributable_and_bound_to_exact_request(self) -> None:
        boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        ordered = (
            "对应请求之后",
            "可归因于用户",
            "准确对象、范围与代次",
            "更早确认",
            "宿主注入",
            "不能补造授权",
            "变更前",
            "commentary",
            "明列证据、允许动作与停止位置",
            "对象待确认",
            "只继续不依赖它的已授权工作",
        )
        positions = [boundaries.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_final_is_terminal_and_known_work_stays_out_of_final(self) -> None:
        boundaries = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        ordered = (
            "同一结果仍未交付",
            "final 只在真实交付时发送",
            "自动续跑不得重开",
            "不能补造新结果或写入权限",
        )
        positions = [boundaries.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_failure_evidence_precedes_the_first_production_write(self) -> None:
        section = REMEDIATION_TEXT.split(
            "### 首次生产写入前固定失败证据", 1
        )[1].split("按层验证：", 1)[0]
        ordered = (
            "稳定发现 ID",
            "当前候选内容身份",
            "正式复现或关键测试身份",
            "实际失败结果",
            "最早错误边界",
            "正式消费者",
            "正式发现或收集入口核对为唯一",
            "停在诊断",
            "不开始生产写入",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能把准备新增测试写成已经取得失败证据", section)
        self.assertIn("使用同一发现 ID 和复现身份取得新结果", section)

    def test_compaction_or_goal_reset_rehydrates_audit_identity_before_status(
        self,
    ) -> None:
        section = REMEDIATION_TEXT.split(
            "### 结项状态先重建原账本",
            1,
        )[1].split("### 结项前消费最终验证计划", 1)[0]
        ordered = (
            "上下文压缩、恢复、目标状态丢失或重建",
            "最强稳定真源",
            "稳定发现 ID、语义标题、原完成条件和最后一次有效证据",
            "摘要、计划和近期修改文件只是投影",
            "同一 ID 对应不同语义标题",
            "目标或任务的权威状态缺失",
            "保持未知或开放",
            "不得输出数字比例、`还剩 N 项`或全称完成",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_administrative_metrics_cannot_be_created_retroactively_for_completion(
        self,
    ) -> None:
        section = REMEDIATION_TEXT.split(
            "### 结项状态先重建原账本",
            1,
        )[1].split("### 结项前消费最终验证计划", 1)[0]
        ordered = (
            "Goal、计划、任务计时器和用量记录",
            "实际创建或绑定到当前结果之后持续覆盖的区间",
            "不存在与当前用户结果、范围和代次匹配的活动记录",
            "直接依据原账本与正式证据结项",
            "不得在实现或验证结束后补建、重置或重新绑定记录",
            "制造完成状态、总耗时或总用量",
            "只处理确实覆盖当前结果的记录",
            "标明为该记录的实际覆盖区间",
            "从用户结果被接受到最终交付连续覆盖全程",
            "才可称为本结果总量",
        )
        positions = [section.index(fragment) for fragment in ordered]
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

    def test_protection_rejection_cannot_be_bypassed_by_changing_tools(
        self,
    ) -> None:
        section = USER_ENVIRONMENT_TEXT.split(
            "### 命令构造或解析失败后切换执行边界",
            1,
        )[1].split("### PowerShell 调用原生搜索时显式传递文件范围和正则", 1)[0]
        ordered = (
            "与 Shell 构造或解析失败分开记录",
            "结果没有说明、可能部分执行或状态查询失败时保持未知",
            "不能把拒绝称为“误判”",
            "也不能只为让同一状态改变通过而更换 Shell、语言、API、工具或执行宿主",
            "已确认的命令形态歧义、明确策略禁止，还是原因未知",
            "原动作仍处于同一份准确授权内",
            "改写不得扩大对象、权限或副作用",
            "明确策略禁止或原因未知时停止并报告",
            "不从另一执行表面完成相同状态改变",
            "披露原拒绝、改写依据、替代入口与后验验证",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

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

    def test_discovered_project_paths_are_reused_by_later_commands(self) -> None:
        ordered = (
            "首次项目盘点",
            "建立本任务的路径清单",
            "后续读取、搜索、补丁、测试和结项证据必须消费这份清单",
            "不得重新按框架惯例、常见仓库布局或相似文件名猜测路径",
            "立即停止依赖它的批次",
            "从同一正式发现来源更新清单后只补跑受影响项",
            "不能证明项目中没有对应对象",
            "与当前清单重新对账",
        )
        positions = [USER_ENVIRONMENT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

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

        acceptance = DESKTOP_TEXT.split("## 3. 实机验收", 1)[1]
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

    def test_non_git_manifests_and_actual_tool_actions_bound_writes(self) -> None:
        for fragment in (
            "非 Git 项目级写入先冻结变更身份",
            "相对路径、类型、字节数、内容哈希",
            "已修改、新增、缺失或未知",
            "它不是备份",
            "清单不会授予删除权限",
            "删除后同路径新建仍包含删除与创建",
            "移动后移回仍包含移动",
            "覆盖后恢复仍包含覆盖",
            "只能原位更新",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

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

    def test_new_root_evidence_invalidates_only_dependent_conclusions(
        self,
    ) -> None:
        section = REMEDIATION_TEXT.split(
            "同一现象链可以同时存在多个独立缺陷或根因",
            1,
        )[1].split("错误最后显示在界面", 1)[0]
        ordered = (
            "新证据只使依赖被推翻前提的结论失效",
            "不能自动撤销已经由另一份有效夹具独立复现的故障",
            "准备回退较早修复前",
            "未包含该修复的基线实现或等价不变实现",
            "重新取得原失败证据",
            "只撤销该次实验的证明力",
            "独立证据仍成立就保留对应修复与验证",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_completion_consumes_the_final_ci_validation_plan(self) -> None:
        section = REMEDIATION_TEXT.split(
            "### 结项前消费最终验证计划",
            1,
        )[1].split("完成摘要必须", 1)[0]
        for fragment in (
            "最后一次实际差异、候选内容身份、原发现账本和当前用户承诺",
            "重新生成并消费 `ci-execution-governance.md` 拥有的唯一验证计划",
            "不复制 CI 的适用性、预算或运行资格规则",
            "公开架构、源码质量、合同、测试收集、正式用户链",
            "真实用户链通过只能关闭它实际覆盖的承诺",
            "不能替代计划遗漏的公开控制项",
            "全称结论保持未验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_closure_preflight_precedes_candidate_and_final_suite(self) -> None:
        section = REMEDIATION_TEXT.split(
            "### 候选冻结前完成结项预检",
            1,
        )[1].split("### 结项前消费最终验证计划", 1)[0]
        ordered = (
            "原发现账本",
            "`root-cause-remediation.md` 的“同源变体收口”",
            "冻结候选或启动最终完整套件前",
            "原完成条件和已取得证据",
            "正式生产者 → 传输或存储边界 → 全部正式消费者",
            "替代入口、构建或测试目标及实际运行产物",
            "生命周期终结",
            "直接诊断、落盘或持久化消费者",
            "唯一测试或检查身份及实际收集结果",
            "开放或未知",
            "不得冻结候选、启动最终完整套件或准备全称结论",
            "其它平台、远端、实机或外部条件继续单列证据平面",
            "交给下一节的唯一验证计划",
            "候选与既有完整套件证据失效",
            "重新生成预检",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
