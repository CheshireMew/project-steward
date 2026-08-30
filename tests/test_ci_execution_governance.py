from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
CI_TEXT = (
    SKILL_ROOT / "references" / "ci-execution-governance.md"
).read_text(encoding="utf-8")
USER_ENVIRONMENT_TEXT = (
    SKILL_ROOT / "references" / "user-environment-governance.md"
).read_text(encoding="utf-8")
SELF_EVOLUTION_TEXT = (
    SKILL_ROOT / "references" / "skill-self-evolution-governance.md"
).read_text(encoding="utf-8")
AUDIT_RELEASE_TEXT = (
    SKILL_ROOT / "references" / "project-audit-release-and-evidence.md"
).read_text(encoding="utf-8")


class CiExecutionGovernanceTests(unittest.TestCase):
    def test_project_level_ci_method_is_reachable_from_both_change_paths(
        self,
    ) -> None:
        route = "references/ci-execution-governance.md"
        prevention = SKILL_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理", 1
        )[0]
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        remediation = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性", 1
        )[0]

        self.assertIn(route, prevention)
        self.assertIn("遵循共同验证门槛", remediation)
        self.assertIn(route, shared)
        self.assertIn("普通单个 CI 报错仍按当前开发任务处理", CI_TEXT)

    def test_shared_validation_gate_is_renewed_before_full_runs_and_reruns(self) -> None:
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        ordered = (
            "references/ci-execution-governance.md",
            "每次完整运行或重跑前按该方法重新核对",
            "候选、实际范围、已耗次数与确认有效性",
            "旧计划不能代替确认",
            "首测前固定正式 runner",
            "运行资格",
            "累计预算",
            "套件次数账本",
        )
        positions = [shared.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_custom_user_chains_and_long_batches_enter_execution_owners(
        self,
    ) -> None:
        shared = SKILL_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化", 1
        )[0]
        environment_route = SKILL_TEXT.split("## 用户环境档案与执行环境", 1)[1].split(
            "## 项目综合审计", 1
        )[0]

        for fragment in (
            "自写浏览器、视觉、用户链验证器首次运行前",
            "references/ci-execution-governance.md",
        ):
            with self.subTest(shared_fragment=fragment):
                self.assertIn(fragment, shared)

        gate = next(line for line in shared.splitlines() if line.startswith("- Windows "))
        for fragment in (
            "后台或跨观察窗口任务、路径、执行环境及并行验证",
            "首次执行前进入“用户环境档案与执行环境”",
            "门槛未满足不启动",
        ):
            with self.subTest(gate_fragment=fragment):
                self.assertIn(fragment, gate)
        self.assertIn("references/user-environment-governance.md", environment_route)

        for fragment in (
            "可回读的进程身份、增量输出和退出状态",
            "不能通过一个超时后无法恢复生产者身份的前台入口启动",
        ):
            with self.subTest(owner_fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

    def test_umbrella_commands_are_reconciled_with_validation_obligations(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 完整入口必须与验收义务对账",
            1,
        )[1].split("### 本地测试前只消费已经完成的远端失败", 1)[0]
        ordered = (
            "形成不依赖命令名称的验收义务集合",
            "展开名为 `full`、`all`、“完整”或类似总入口的机器可读阶段与实际子命令",
            "由总入口覆盖 / 必须单独运行 / 范围外",
            "计算合并后的关键路径预算、阶段顺序及完整套件次数",
            "不能在用户确认预算或完整运行结束后静默追加",
            "从同一验收义务集合重新展开和对账",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "用户、项目规则、发布合同或公开验证器清单",
            "真实用户链、性能、视觉、交接、目标平台或其它独立验证族",
            "覆盖关系标为未知并停在计划阶段",
            "总入口实际覆盖的义务和仍需单独运行的义务",
            "旧的覆盖映射与预算确认随之失效",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_parent_wrapper_subsumes_duplicate_final_child_runs(self) -> None:
        section = CI_TEXT.split(
            "### 完整入口必须与验收义务对账",
            1,
        )[1].split("### 本地测试前只消费已经完成的远端失败", 1)[0]
        ordered = (
            "父入口在同一候选上完整运行子入口",
            "保留同等退出状态和证据",
            "最终只运行父入口",
            "子入口只用于冻结前聚焦诊断",
            "不再重复取得最终资格",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_local_validation_consumes_one_completed_remote_failure_without_polling(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 本地测试前只消费已经完成的远端失败",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        for fragment in (
            "启动第一条本地测试前",
            "至多一次读取",
            "最近一项已经完成的失败运行",
            "不在每个 spec、分片或内部轮次前重新访问远端",
            "产品、测试驱动或夹具、基础设施或外部环境、最终断言",
            "排队、运行、取消和跳过状态不进入本地完成门槛",
            "远端查询本身变成测试前置阻塞",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_current_host_and_development_stage_limit_expensive_checks(self) -> None:
        section = CI_TEXT.split(
            "### 本地测试前只消费已经完成的远端失败",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        for fragment in (
            "默认只验证当前机器和当前操作系统",
            "只有用户明确要求另一平台",
            "不轮询、不等待",
            "完整覆盖率、完整端到端矩阵、性能与视觉矩阵、打包、签名和发布检查",
            "经权威来源确认的代码冻结或发布候选",
            "累计预计超过十五分钟",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_stage_authority_and_cumulative_budget_gate_precede_tests(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 阶段资格、累计预算与全量验证上限",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        ordered = (
            "项目阶段默认是活跃开发",
            "只有用户明确确认，或项目正式发布真源",
            "不能因为局部检查通过",
            "冻结资格和依赖它取得的昂贵验证授权立即失效",
            "启动本阶段第一条测试前",
            "按关键路径累计全部计划检查的预计墙钟时间",
            "累计预计超过十五分钟",
            "多条各自短于十五分钟的命令不能绕过累计门槛",
            "旧确认立即失效",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "环境准备、数据生成、启动、关闭、清理",
            "计划允许的一次重跑",
            "并行项按关键路径计算",
            "候选命令、目的、范围、历史耗时依据和累计预计",
            "新增动作开始前重新确认",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_mid_run_budget_reduction_preserves_completion_contract(self) -> None:
        section = CI_TEXT.split(
            "### 阶段资格、累计预算与全量验证上限",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        ordered = (
            "用户在执行中要求简单收口、缩短耗时或降低成本",
            "冻结原完成条件和已消耗预算",
            "必需、辅助和范围外",
            "只裁减辅助项",
            "剩余必需检查超出新边界",
            "标为未验证、开放或受阻",
            "不能删除原义务",
            "追认“全部完成”",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_full_suite_has_an_authoritative_two_run_ceiling(self) -> None:
        section = CI_TEXT.split(
            "### 阶段资格、累计预算与全量验证上限",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        ordered = (
            "最多先运行一次获准的完整仓库套件",
            "只做聚焦诊断、获准修复和受影响检查",
            "再次由权威来源冻结",
            "用户重新确认完整验证的命令与累计预算",
            "最后一次完整套件复跑",
            "不启动第三次完整套件",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "不能反向让原本不适用的全量验证取得运行资格",
            section,
        )

    def test_audit_remediation_hands_validation_control_to_ci_governance(
        self,
    ) -> None:
        remediation = SKILL_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        self.assertIn("审计修复或验证控制面变化：遵循共同验证门槛", remediation)

        for fragment in (
            "交给 `ci-execution-governance.md`",
            "准确候选内容身份",
            "必需验证族",
            "冻结资格的权威来源",
            "预计累计墙钟时间",
            "已经消耗的完整套件次数",
            "不授予运行资格",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, AUDIT_RELEASE_TEXT)

    def test_candidate_changes_invalidate_active_runs_without_bypassing_gates(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 阶段资格、累计预算与全量验证上限",
            1,
        )[1].split("计划的机器可读输出", 1)[0]
        for fragment in (
            "绑定启动时的准确候选内容身份",
            "从变化发生时起，该运行只能作为诊断证据",
            "尚未开始的阶段立即停止",
            "不得关闭当前候选",
            "不能把变化前后的输出拼成同一次通过",
            "只收口能够证明由旧运行拥有的进程与资源",
            "建立新的运行身份",
            "只证明该验证族适用于最终候选",
            "不会绕过阶段资格、累计预算、候选冻结",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_equivalent_remote_events_share_one_expensive_run_identity(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "远端运行身份由候选 SHA",
            1,
        )[1].split("用户或项目规则明确要求最终完整套件", 1)[0]
        for fragment in (
            "验证计划、基准或 merge-ref、权限与信任边界、正式消费者",
            "`push` 与同仓 PR 的身份等价时",
            "昂贵验证只保留一个规范运行",
            "fork 权限、secrets、merge-ref 或消费者不同则分别运行",
            "不能取消不同信任或基准合同",
            "required check 名称指向规范结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_remote_failures_use_machine_readable_identity(self) -> None:
        section = CI_TEXT.split("## 7. 失败后只重跑有证据的范围", 1)[1]
        for fragment in (
            "状态页与 watcher 只是可能截断名称的展示投影",
            "机器可读接口还原准确 SHA、run、attempt、job、check",
            "日志和产物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_default_branch_result_waits_only_for_its_required_gate(self) -> None:
        section = CI_TEXT.split("## 9. 完成与停止", 1)[1]
        self.assertIn("停止位置只是普通提交或候选分支推送时", section)
        self.assertIn(
            "普通的提交和推送动作仍在触发远端运行后释放当前任务",
            section,
        )
        self.assertIn("停止位置明确是候选进入默认分支时", section)
        self.assertIn("required checks 是该已授权结果的前置门", section)

    def test_test_command_scope_is_expanded_before_execution(self) -> None:
        section = CI_TEXT.split(
            "### 测试命令先展开再取得运行资格",
            1,
        )[1].split("## 2. 按成本和信息量排列阶段", 1)[0]
        for fragment in (
            "在启动测试进程前",
            "实际会收集的唯一测试身份",
            "外部 CLI、真实子进程、浏览器、桌面运行时",
            "预检不得执行测试正文",
            "不能代替实际展开结果",
            "必需、辅助或范围外",
            "完全落入获准的必需与辅助范围",
            "改用测试框架正式支持的文件、节点、资源档位或分片过滤",
            "不得先执行整库命令再事后解释哪些测试无关",
            "只能降低执行风险",
            "不能让与本轮受影响链无关的外部集成取得运行资格",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_test_seam_is_compatible_with_the_formal_runner(self) -> None:
        section = CI_TEXT.split(
            "### 测试命令先展开再取得运行资格",
            1,
        )[1].split("### 昂贵验证器先证明自己的适用合同", 1)[0]
        ordered = (
            "新增测试缝前",
            "不执行正文的短探针",
            "runner 的转译方式、模块解析、支持语法和运行时全局",
            "新模块必须能被正式入口实际加载",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_surprising_external_resources_are_explained_before_launch(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "候选检查会启动外部 CLI",
            1,
        )[1].split("修改测试执行器、共享配置", 1)[0]
        ordered = (
            "在启动前向用户说明",
            "本轮变化事实",
            "取得运行资格的具体测试身份",
            "资源类型和预计耗时",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "只说明风险控制",
            "不能代替为什么该检查直接覆盖本轮改动",
            "已经启动后再解释警告也不能追认运行资格",
            "无法在启动前完成这份映射就不运行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_test_control_plane_change_uses_representative_nodes_first(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 测试命令先展开再取得运行资格",
            1,
        )[1].split("## 2. 按成本和信息量排列阶段", 1)[0]
        for fragment in (
            "不自动让全部产品测试变成相关测试",
            "先运行控制面自己的规则测试",
            "选择能够区分新旧行为的代表性节点",
            "影响无法按正式身份和资源档位界定",
            "才扩大到受影响的完整验证族",
            "完整仓库套件仍须满足",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_expensive_validator_preflights_and_stops_after_second_drift(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 昂贵验证器先证明自己的适用合同",
            1,
        )[1].split("## 2. 按成本和信息量排列阶段", 1)[0]
        ordered = (
            "不执行昂贵正文的预检",
            "实际非空收集身份",
            "当前夹具与数据 schema",
            "最小样本跑一次短探针",
            "不得先构造代表性大规模输入",
            "先取得测试基础设施写入权限",
            "一次精确短探针复跑",
            "第二个不同的过时假设",
            "形成独立的测试基础设施发现",
            "停止当前昂贵验证循环",
            "产品结论保持未验证",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不能边修验证器边反复生成大数据", section)

    def test_runner_side_effects_require_authorized_retention_semantics(
        self,
    ) -> None:
        section = CI_TEXT.split(
            "### 正式 runner 的副作用与证据保留先满足授权",
            1,
        )[1].split("### 昂贵验证器先证明自己的适用合同", 1)[0]
        ordered = (
            "创建、移动、覆盖、删除和保留规则",
            "没有删除授权或完成合同要求保留",
            "不具备正式运行资格",
            "项目提供正式保留模式",
            "同一测试身份、正式生产者、结果判定和退出语义",
            "只改变证据保留",
            "不得绕过 runner 的正常完成路径后手工改写 manifest、状态或成功标记",
            "最多是诊断证据",
            "不能报告为正式 runner 已完成",
            "停在运行前",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_skill_evolution_validation_is_isolated_from_governed_projects(
        self,
    ) -> None:
        section = SELF_EVOLUTION_TEXT.split(
            "Project Steward 自我进化的验证只消费",
            1,
        )[1].split("写入方案和最终差异按所有者组织", 1)[0]
        for fragment in (
            "准确 Skill Git 根内",
            "被治理项目可以提供学习证据",
            "都不是 Skill 改动的验证消费者",
            "不得为证明 Project Steward 已经进化而启动",
            "为两个结果分别建立验证计划",
            "目标项目只运行自身改动所需的最小检查",
            "Project Steward 只运行自身检查",
            "不能替另一方背书或扩大另一方的测试范围",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_ordinary_implementation_stops_after_push(self) -> None:
        section = CI_TEXT.split("## 9. 完成与停止", 1)[1]
        for fragment in (
            "当前机器的必需目标检查通过",
            "非强制推送完成时停止",
            "不主动取得 run 后持续轮询",
            "它们尚未结束不会阻止本地实施结果交付",
            "只有用户明确要求监控或完成 CI",
            "提交和推送动作仍在触发远端运行后释放当前任务",
            "异步运行且本任务没有等待的远端检查",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_one_validation_plan_drives_cost_ordered_execution(self) -> None:
        stage_text = CI_TEXT.split("## 2. 按成本和信息量排列阶段", 1)[1].split(
            "## 3. 缓存执行环境，不混入产品缓存",
            1,
        )[0]
        ordered = (
            "工作流预检",
            "便宜的确定性检查",
            "目标平台冷启动冒烟",
            "受影响测试与资源分片",
            "昂贵合同与真实用户链",
            "质量门",
        )
        positions = [stage_text.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(
            CI_TEXT.index("先生成一份验证计划"),
            CI_TEXT.index("## 2. 按成本和信息量排列阶段"),
        )
        self.assertIn("全部 CI 作业消费它", CI_TEXT)
        self.assertIn("文档、许可证、致谢和纯仓库元数据", CI_TEXT)

    def test_generated_artifact_producer_precedes_clean_runner_consumer(
        self,
    ) -> None:
        artifact_order = CI_TEXT.split(
            "### 生成产物的生产者必须先于消费者",
            1,
        )[1].split("本地最终入口与 CI 消费同一验证计划", 1)[0]

        for fragment in (
            "干净 runner 上必须已经存在",
            "未被仓库跟踪、由构建生成、通常被忽略或来自另一作业",
            "正式生产者步骤及其前置输入",
            "上游 artifact 传递边界",
            "第一个安装、打包、测试或运行消费者",
            "不能依赖本机残留、未声明的缓存",
            "预先生成一次后消费者成功",
            "不包含这些输出的新鲜检出或等价隔离状态",
            "消费者不会在生产者之前进入",
            "实际跨过生产、传递和消费边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, artifact_order)

        self.assertIn("derived-artifact-governance.md", artifact_order)
        self.assertIn("本节只拥有 CI 中的生产顺序和传递事实", artifact_order)

    def test_workspace_package_runners_resolve_the_current_contract_identity(
        self,
    ) -> None:
        artifact_order = CI_TEXT.split(
            "### 生成产物的生产者必须先于消费者",
            1,
        )[1].split("本地最终入口与 CI 消费同一验证计划", 1)[0]

        for fragment in (
            "多包或工作区仓库",
            "根级测试入口、包级 test script、局部测试配置与 alias",
            "实际加载的包与测试配置",
            "最终解析到的绝对目标和内容身份",
            "应读取本轮源码还是由本轮生产者生成的输出",
            "根级测试通过、构建步骤已经运行或目标路径存在",
            "旧 `dist`、另一份副本或错误层级",
            "从实际包入口启动",
            "验证计划声明的当前合同身份",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, artifact_order)

    def test_independent_expensive_boundaries_and_control_plane_fail_closed(
        self,
    ) -> None:
        for fragment in (
            "每个能够独立适用、失败、缓存或重跑的昂贵验证族",
            "不能为了少写条件",
            "质量门也逐项读取同一计划输出",
            "控制面变化必须失败关闭",
            "代表性路径矩阵",
            "每个独立昂贵边界",
            "不能让正在被修改的旧规则决定自己无需接受某个分支",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_local_entry_consumes_the_plan_without_claiming_ci_boundaries(
        self,
    ) -> None:
        for fragment in (
            "本地最终入口与 CI 消费同一验证计划",
            "本地唯一入口",
            "无资源边界的整库命令",
            "隔离目录、耗时和证据位置",
            "明确报告为异步或待证明",
            "本地完整通过不能被写成这些边界已经通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_environment_cache_is_reproducible_and_separate_from_products(
        self,
    ) -> None:
        for fragment in (
            "缓存完整语言或依赖环境",
            "操作系统与架构",
            "解释器或运行时的准确版本和 ABI",
            "依赖锁文件内容身份",
            "刷新当前候选源码的 editable 或等价安装",
            "执行依赖一致性检查",
            "语言依赖环境与原生 SDK、浏览器、媒体运行时",
            "首次冷运行与后续热运行分别记录",
            "精确命中",
            "状态清单也通过恢复校验",
            "当前候选提交的正式测试、冒烟和消费者验证仍然执行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

        self.assertIn("derived-artifact-governance.md", CI_TEXT)
        self.assertIn("产品派生产物及其语义缓存", CI_TEXT)

    def test_resource_partition_is_complete_without_marker_churn(self) -> None:
        for fragment in (
            "测试框架实际收集的唯一节点身份",
            "不要为了形式给大量测试机械添加多套 marker",
            "分区完整且互斥",
            "轻量档位不安装、启动或暴露重型能力",
            "测试意外请求它们时明确失败",
            "参数化和生成测试按实际节点计入",
            "大迁移后以最新收集与真实调用重新建立基线",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_shards_use_timing_and_report_wall_and_compute_cost(self) -> None:
        for fragment in (
            "历史耗时",
            "测试文件字节数、测试函数数量和一次偶然运行不能代表耗时",
            "新节点没有历史时使用公开的保守默认权重",
            "最慢分片的墙钟时间",
            "全部分片的总计算量",
            "冷启动成本",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_exact_shard_identity_and_timeout_inference_are_bounded(self) -> None:
        section = CI_TEXT.split("## 5. 按历史耗时分片", 1)[1].split(
            "## 6. 在昂贵阶段前验证工作流边界",
            1,
        )[0]
        for fragment in (
            "精确分片身份由候选内容、收集输入、按序节点清单",
            "分片编号与总数不是身份",
            "同编号分片已经是新分片",
            "分别运行旧候选的疑似失败节点和当前候选重新计算的实际分片",
            "执行器确定串行",
            "逐节点日志刷新语义已知",
            "当前节点保持未知",
            "节点开始标记或心跳",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_parallel_commands_have_short_roots_and_exact_serial_exceptions(
        self,
    ) -> None:
        for fragment in (
            "每条可能并发执行的命令拥有独立的测试、项目、媒体、服务状态",
            "最长合法后缀反推执行根长度",
            "日志与报告证据根和尽量短的执行根分开",
            "产品并发合同",
            "最窄节点身份移入显式串行通道",
            "参数化测试使用稳定的节点前缀",
            "不能扩大到整个文件或套件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_process_cleanup_requires_exact_command_ownership(self) -> None:
        for fragment in (
            "状态根、发现记录、进程身份和启动时间",
            "只审计并收口由该命令正式登记的实例",
            "不能证明它由测试拥有",
            "用户默认状态根或身份不匹配的进程保持不动",
            "已退出",
            "身份不属于本轮",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_parallelism_uses_the_tightest_resource_headroom(self) -> None:
        for fragment in (
            "并发数由最紧瓶颈余量决定",
            "物理内存",
            "虚拟或提交内存及其系统上限",
            "进程和句柄",
            "显存或设备会话",
            "共享基线",
            "系统与用户保留量",
            "单个并发单元的保守峰值",
            "全部有限资源结果中的最小值",
            "当前命令的资源收口门槛仍然失败",
            "不能继续提高并发",
            "同一节点隔离运行通过",
            "不能用全局串行长期遮住生命周期缺口",
            "限制并发的资源、容量来源、保留量、代表性峰值、最终工作数",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

        bottleneck = CI_TEXT.split("### 并发数由最紧瓶颈余量决定", 1)[1].split(
            "## 5. 按历史耗时分片", 1
        )[0]
        self.assertLess(bottleneck.index("物理内存"), bottleneck.index("不能证明"))
        self.assertIn("CPU 和物理内存充足但另一项资源余量不足时降低并发", bottleneck)

    def test_preflight_and_failed_scope_rerun_preserve_failure_evidence(
        self,
    ) -> None:
        for fragment in (
            "输出的缺失、空字符串、真假值和错误值语义",
            "以与 CI 相同的 shell、模块或包入口启动",
            "测试收集实际非空",
            "只有存在真实瞬态依据时",
            "允许在相同提交、输入、runner 和命令下做一次原样重跑",
            "限于失败作业及依赖其结果的质量门",
            "不重新运行完整工作流",
            "不能用通用 retry",
            "不能把失败归咎于“冒烟太早”后移除它",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

    def test_method_reports_real_bottlenecks_and_stays_cross_project(self) -> None:
        for fragment in (
            "排队与启动",
            "依赖恢复、下载与安装",
            "各分片耗时、最长关键路径与总计算量",
            "冷运行、热运行及失败范围重跑",
            "只有阶段计时和关键路径能够证明瓶颈",
            "本地已执行与明确交给 CI 的验证族",
            "本轮登记、退出和仍存的后台实例",
            "不为每条说明制作镜像断言",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)

        for forbidden in (
            "MediaFlow",
            "Qt",
            "MLT",
            "Chromium",
            "524",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, CI_TEXT)

        self.assertNotRegex(CI_TEXT, r"[A-Za-z]:\\")
        self.assertLessEqual(len(SKILL_TEXT.splitlines()), 220)
        self.assertLessEqual(len(SKILL_TEXT), 14_000)

        direct_references = set(
            re.findall(r"references/[A-Za-z0-9._/-]+\.md", SKILL_TEXT)
        )
        self.assertIn("references/ci-execution-governance.md", direct_references)
        for reference in direct_references:
            with self.subTest(reference=reference):
                self.assertTrue((SKILL_ROOT / reference).is_file())

    def test_repeated_lifecycle_costs_use_multiplicative_phase_evidence(
        self,
    ) -> None:
        for fragment in (
            "应用构造、资源发现、缓存或清理扫描",
            "执行次数 × 代表性阶段成本",
            "启动或构造、核心操作、关闭或清理",
            "普通用户也会承担该成本",
            "修复产品所有权、受管理命名空间或生命周期边界",
            "不能靠跨命令共享实例、复用污染状态、跳过关闭或删除覆盖",
            "刷新历史耗时权重后再重新分片",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CI_TEXT)


if __name__ == "__main__":
    unittest.main()
