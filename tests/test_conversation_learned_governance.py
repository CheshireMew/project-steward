from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
AGENT_TEXT = (
    SKILL_ROOT / "agents" / "openai.yaml"
).read_text(encoding="utf-8")
LEARNING_TEXT = (
    SKILL_ROOT
    / "references"
    / "conversation-learning-and-self-evolution.md"
).read_text(encoding="utf-8")
ARCHITECTURE_TEXT = (
    SKILL_ROOT
    / "references"
    / "architecture-cohesion-governance.md"
).read_text(encoding="utf-8")
PUBLICATION_TEXT = (
    SKILL_ROOT / "references" / "repository-publication.md"
).read_text(encoding="utf-8")
PREVENTION_TEXT = (
    SKILL_ROOT / "references" / "change-prevention.md"
).read_text(encoding="utf-8")
REMEDIATION_TEXT = (
    SKILL_ROOT / "references" / "root-cause-remediation.md"
).read_text(encoding="utf-8")
DESKTOP_TEXT = (
    SKILL_ROOT / "references" / "desktop-app-governance.md"
).read_text(encoding="utf-8")
IMPLEMENTATION_TEXT = (
    SKILL_ROOT / "references" / "implementation-review.md"
).read_text(encoding="utf-8")
PRODUCT_EXPERIENCE_TEXT = (
    SKILL_ROOT / "references" / "product-experience-governance.md"
).read_text(encoding="utf-8")
DESIGN_METHOD_TEXT = (
    SKILL_ROOT / "references" / "design-method.md"
).read_text(encoding="utf-8")
INTERACTION_MOTION_TEXT = (
    SKILL_ROOT / "references" / "interaction-motion.md"
).read_text(encoding="utf-8")
LAYOUT_RESPONSIVE_TEXT = (
    SKILL_ROOT / "references" / "layout-responsive.md"
).read_text(encoding="utf-8")
INTERFACE_PROBLEM_TEXT = (
    SKILL_ROOT / "references" / "interface-problem-patterns.md"
).read_text(encoding="utf-8")
LOG_TEXT = (
    SKILL_ROOT / "references" / "log-audit-standard.md"
).read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT = (
    SKILL_ROOT / "references" / "project-audit.md"
).read_text(encoding="utf-8")
LOCAL_WORKSPACE_TEXT = (
    SKILL_ROOT / "references" / "local-file-workspace-governance.md"
).read_text(encoding="utf-8")


class ConversationLearnedGovernanceTests(unittest.TestCase):
    def test_read_only_verbs_are_a_hard_project_write_boundary(self) -> None:
        for fragment in (
            "检查、审计、诊断、评估、分析或报告",
            "不得以验证根因、顺手治理或提高结论可信度为由修改项目",
            "不追溯授权这些改动原本是否可以产生",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        self.assertIn("按照主路由已经选定的模式执行", ARCHITECTURE_TEXT)
        self.assertIn("本方法不重新解释用户措辞", ARCHITECTURE_TEXT)
        self.assertNotIn("用户只说检查、审计、诊断", ARCHITECTURE_TEXT)
        self.assertIn("检查是硬只读边界", README_TEXT)

    def test_failed_execution_of_an_existing_rule_changes_consumers(self) -> None:
        for fragment in (
            "已有能力没有被执行",
            "最早没有消费该规则的路由或动作门槛",
            "表层不同的代表性请求",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn(
            "已有正确规则却仍发生越界时",
            SKILL_TEXT,
        )
        self.assertIn(
            "不会再堆一条同义原则",
            README_TEXT,
        )

    def test_run_or_build_permission_does_not_expand_write_authority(
        self,
    ) -> None:
        for fragment in (
            "“允许运行 build”",
            "不改变已经冻结的项目写入权限",
            "修改源码、配置、测试或工作流来修复失败",
            "自动续跑、目标恢复和后续进度轮次",
            "后续只开放其中一项时，其它权限保持原状",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "只授权执行构建及生成它正常产生的产物",
            "不把只读审计改成项目修复",
            "构建失败形成审计证据",
            "仍需已有修复授权或另行确认",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

    def test_comprehensive_audit_has_a_bounded_coverage_contract(self) -> None:
        for fragment in (
            "实际可覆盖的项目边界",
            "完整性结论只对这份覆盖合同成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "用户要求“全部问题”“所有问题”或“全面检查”",
            "审计根、版本或工作树状态",
            "当前明确无法取得的证据",
            "只表示在这份冻结范围内",
            "负面结论也需要范围证据",
            "不为了形式完整建议新增架构",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

    def test_learning_layers_common_paths_and_special_dimensions(self) -> None:
        for fragment in (
            "同一项经验和同一个用户结果可以同时进入两层",
            "共同机制负责一类请求共享的最早判断和共同路径",
            "一个结果可以同时命中多个特殊维度",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "这不是分类时的二选一",
            "共同机制：去掉专项名称和表面症状后",
            "特殊条件改变什么：识别 / 观测 / 动作 / 验证 / 停止位置",
            "两层怎样共同消费",
            "各自唯一真源和消费者",
            "一个结果同时符合多个特殊条件时可以组合消费",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("共同路径和特殊维度，两者不是二选一", README_TEXT)
        self.assertIn("同一个问题可以先进入跨项目共用的方法", README_TEXT)

    def test_rejected_content_cannot_become_active_defaults_or_examples(self) -> None:
        for fragment in (
            "被否定内容只作为证据，不进入活动能力",
            "不得以案例、默认方法、候选模板、创作参考、few-shot 示例",
            "不能把失败内容本身升级成默认答案",
            "不复刻被否定内容",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_current_conversation_scope_does_not_expand_through_links(self) -> None:
        for fragment in (
            "“这个会话”或“当前任务”只指承载本次请求的当前任务",
            "不自动递归展开",
            "用户曾为更早结果提供过参考链接",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "开始读取前先冻结本次历史材料边界",
            "不能因为链接仍在历史里就自动打开",
            "不能为了显得完整而递归遍历所有引用",
            "历史材料边界：",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("“这个会话”只指当前任务", README_TEXT)

    def test_evidence_acquisition_is_complete_and_failure_isolated(self) -> None:
        for fragment in (
            "来源范围、完整性和执行状态",
            "只有继续读取到明确末尾才算完整",
            "一项异常不得让其它成功证据消失",
            "只补齐未取得的证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "预期范围、取得方式和完整性标记",
            "EOF 或明确末尾",
            "证据编排本身失败",
            "只单独补跑未返回或状态未知的项目",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        for fragment in (
            "前置条件、相互依赖、是否必需",
            "会整体失败的批次",
            "逐项保留输出、错误和退出状态",
            "已经成功且证据仍新鲜的检查继续保留",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("来源只有读到明确末尾才算完整", README_TEXT)
        self.assertIn("一个可选检查失败不会吞掉其它成功证据", README_TEXT)

    def test_behavior_baseline_separates_intent_current_state_and_history(
        self,
    ) -> None:
        for fragment in (
            "用户现在要什么",
            "当前实现是什么",
            "过去发生过什么",
            "历史提交只证明该提交时发生过什么",
            "可人工核对的行为合同",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "完整性不等于当前权威性",
            "目标意图、当前实现还是历史原因",
            "Git 提交、旧截图和旧方案只证明其历史时点",
            "不能从旧 Git、过期测试或一次稳定截图补造产品意图",
            "目标行为基线、来源角色与适用状态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        for fragment in (
            "本轮正在回答：目标意图 / 当前实现 / 历史原因",
            "不能先按旧 Git 或过期测试实施",
            "禁止闪现、空白、重叠、回跳或重放的中间状态",
            "最终画面正确不能证明启动过程",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("当前运行结果与目标冲突时", REMEDIATION_TEXT)
        self.assertIn(
            "不在产品体验路径另建一套来源真源",
            PRODUCT_EXPERIENCE_TEXT,
        )
        self.assertIn("旧 Git 只证明对应提交的历史", README_TEXT)

    def test_reference_implementations_are_adopted_at_mechanism_level(self) -> None:
        for fragment in (
            "整体依赖、可迁移机制、运行假设与不适用部分",
            "整体采用、局部吸收或拒绝",
            "参考项目自己的性能数字",
            "代表性工作负载矩阵",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT + SKILL_TEXT)

        self.assertIn("不会建立第二套状态、时间轴、缓存或恢复边界", PREVENTION_TEXT)
        self.assertIn("用当前项目的代表性负载决定", README_TEXT)

    def test_self_evolution_requires_a_second_stage_confirmation(self) -> None:
        section = SKILL_TEXT.split(
            "### 3. 对话学习与自我进化",
            1,
        )[1].split("### 4. 改动前预防", 1)[0]
        ordered = (
            "这项请求授权分析并准备变更方案",
            "随后交付并停止",
            "用户看到这些内容后另行明确确认",
            "才开始修改",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("跳过方案确认并立即实施", section)
        self.assertIn("只更新本轮行为实际影响", section)
        self.assertIn("确定性测试保护稳定结构", section)
        self.assertNotIn(
            "修改本 Skill 的主路由、方法、资源、README、元数据和行为测试",
            section,
        )

        self.assertIn("然后返回主路由并停止", LEARNING_TEXT)
        self.assertIn("写入权限由主路由的两阶段确认结果决定", LEARNING_TEXT)

    def test_default_prompt_is_a_short_confirmation_first_entry(self) -> None:
        prompt_line = next(
            line
            for line in AGENT_TEXT.splitlines()
            if line.strip().startswith("default_prompt:")
        )
        prompt = prompt_line.split(":", 1)[1].strip().strip('"')
        self.assertLessEqual(len(prompt), 140)
        for fragment in (
            "$project-steward",
            "先展示",
            "并停下",
            "确认后",
            "自我进化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, prompt)

        for unrelated_specialty in (
            "持久意图",
            "跨重启",
            "用户环境",
        ):
            with self.subTest(unrelated_specialty=unrelated_specialty):
                self.assertNotIn(unrelated_specialty, prompt)

    def test_boundary_invariants_are_consumed_before_and_after_failures(self) -> None:
        self.assertIn("派生维度", LEARNING_TEXT)
        self.assertIn("## 3. 派生边界不变量", PREVENTION_TEXT)
        self.assertIn("## 4. 同源变体收口", REMEDIATION_TEXT)

        for contract in (
            "权限归属",
            "状态生命周期",
            "数据表示",
            "边界转向",
            "实际运行入口",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, SKILL_TEXT)
                self.assertIn(contract, PREVENTION_TEXT)
                self.assertIn(contract, REMEDIATION_TEXT)

        self.assertIn(
            "references/change-prevention.md",
            SKILL_TEXT,
        )
        self.assertIn(
            "references/root-cause-remediation.md",
            SKILL_TEXT,
        )
        self.assertIn("用户入口实际选择", PREVENTION_TEXT)
        self.assertIn("用户入口实际选择", REMEDIATION_TEXT)
        self.assertIn(
            "源码正确、普通构建通过和用户入口实际选中当前产物",
            README_TEXT,
        )

    def test_worker_results_streams_and_runtime_bundles_have_exact_boundaries(
        self,
    ) -> None:
        for fragment in (
            "业务结果使用唯一结构化通道",
            "日志、退出码和传输结束各自保留原语义",
            "子进程解析和依赖或资源的精确闭包",
            "清单允许集合与运行目录实际集合是否完全一致",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "任意改变 chunk 边界",
            "必须 flush 尚未输出的安全尾部",
            "完整事件和原文由无损持久真源保存",
            "加入一个未声明陈旧文件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "结果帧至多一次",
            "有界摘要只能是可追溯到完整记录的投影",
            "允许文件集合与运行目录实际集合必须完全一致",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "至多一次的结构化结果帧",
            "完整日志落盘",
            "缺失或重复结果帧形成明确失败",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        for fragment in (
            "完整记录和有界投影是两个不同合同",
            "结构化结果帧是业务状态的唯一来源",
            "分片不变量与最终 flush",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

        for fragment in (
            "运行目录实际集合完全相等",
            "未来 CI 计划不能冒充当前已经生成和消费的证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        for fragment in (
            "普通日志、退出码和 EOF 不负责猜测结论",
            "依赖与资源清单还要和运行目录实际文件集合完全一致",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_architecture_screening_aggregates_logical_owners(self) -> None:
        for fragment in (
            "逻辑所有者",
            "`partial class`",
            "头文件与实现文件",
            "聚合后的逻辑所有者",
            "声明与定义",
            "自动化文本扫描只生成候选",
            "按逻辑所有者重新聚合指标",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_external_workspace_writers_are_gated_before_state_changes(
        self,
    ) -> None:
        for fragment in (
            "视为潜在并发生产者",
            "写入前保存受影响路径的基线",
            "不得被恢复、覆盖、混入暂存",
            "只停止与这些路径冲突的动作",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "工作区存在其它写入者时",
            "状态在本轮没有执行对应动作时自行变化",
            "外部或来源未知",
            "不能为了得到干净状态使用恢复或删除",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("不能解释的变化不得用 `git restore` 消掉", PUBLICATION_TEXT)
        self.assertIn("来源不明的变化不会被恢复、覆盖或顺手纳入", README_TEXT)

    def test_local_workspace_has_one_multidimensional_path_policy(self) -> None:
        for fragment in (
            "一套路径身份，多项内容策略",
            "是否在树中可见、是否进入搜索或索引",
            "是否允许普通内容命令修改",
            "是否进入版本变化、是否必须被监听和通知",
            "都消费同一个路径身份与策略",
            "先按稳定路径身份识别并发出变化事实，再解析其内容",
            "测试必须经过同一生产者形态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOCAL_WORKSPACE_TEXT)

        self.assertIn("统一内容路径策略", README_TEXT)
        self.assertIn("即使损坏或无法解析", README_TEXT)

    def test_deployable_repository_scope_comes_from_a_clean_checkout(self) -> None:
        for fragment in (
            "以干净克隆合同确定必须跟踪",
            "当前差异、跟踪状态或忽略规则都不能单独决定仓库边界",
            "读取失败结果属于验证",
            "修改项目修复失败仍需",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        self.assertIn("用干净克隆确定仓库边界", PUBLICATION_TEXT)
        self.assertIn("若目标包含异机运行或服务器部署", README_TEXT)

    def test_publication_reuses_only_fresh_verified_evidence(self) -> None:
        for fragment in (
            "检查证据新鲜度",
            "证据仍新鲜时复用已有验证",
            "不重新运行整套开发流程",
            "不追溯授权此前产生项目修改",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_contract_closure_and_publication_rules_are_active(self) -> None:
        for fragment in (
            "验证工具、扫描器或审计命令自身失败时只能标为未知",
            "验证与发布脚本、真实用户链工具",
            "由谁登记这些工作",
            "确定确切实例",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    LEARNING_TEXT + PREVENTION_TEXT + REMEDIATION_TEXT,
                )

        for fragment in (
            "审计对象是 Git 实际索引",
            "推送请求不会自动授权创建仓库",
            "不能根据同一账号的其它仓库可见性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

        for fragment in (
            "公共契约变化时把文档、示例、schema、生成物来源和维护工具也作为正式消费者",
            "派生的异步工作必须有生命周期所有者",
            "提交前审计 Git 实际暂存索引",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "文档、示例、schema、公共导出、验证与发布脚本、真实用户链工具和生成物来源也属于正式消费者",
            "审计实际暂存索引",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_mutation_receipts_are_not_final_state_evidence(self) -> None:
        for fragment in (
            "改变状态的工具回执只证明调用已经返回",
            "在下一项依赖动作开始前",
            "直接从目标文件、存储、远程状态或正式消费者回读",
            "预期的零发现与执行失败分开",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "写入工具返回成功只表示调用已经结束",
            "按各自的退出语义区分通过、零发现与执行失败",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_verifier_success_requires_expected_input_coverage(self) -> None:
        for fragment in (
            "预期覆盖对象及内容身份",
            "工具实际选择的输入、版本、过滤和排除项",
            "输入为空、过期或不完整",
            "未覆盖或未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT + REMEDIATION_TEXT)

        for fragment in (
            "验证器成功退出也不等于已覆盖预期对象",
            "被过滤与排除规则遗漏",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        for fragment in (
            "每项验证还要建立输入覆盖合同",
            "允许的结论：通过 / 零发现 / 未覆盖 / 未知 / 失败",
            "不由验证器碰巧看到的内容反推",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn(
            "命令成功但输入为空、过期或漏掉候选内容",
            README_TEXT,
        )

    def test_verification_coverage_is_bound_to_real_build_targets(self) -> None:
        for fragment in (
            "不同平台、编译目标、构建 profile、feature 或条件编译分支",
            "宿主侧通过不能证明未被编译的目标专属代码",
            "每个必需目标取得自己的新鲜退出状态和消费证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "建立目标覆盖矩阵",
            "被目标条件排除的导入、类型、资源、权限和生命周期代码",
            "任何一项通过都不能替代另一项",
            "不能与修改前的其它层拼成一次完整通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("目标专属代码", PROJECT_AUDIT_TEXT)
        self.assertIn("宿主侧通过不会替", README_TEXT)

    def test_public_audit_uses_live_remote_and_external_capability_evidence(
        self,
    ) -> None:
        for fragment in (
            "分开本地与实时远端事实",
            "本地缓存的远端跟踪引用",
            "实时远端默认分支与 HEAD",
            "不能把“没有读到”写成“远端不存在”",
            "验证外部默认能力的现实可用性",
            "项目自己的有界连接测试",
            "不能从一次 `401`、`402`、超时或官方资料冲突扩大成服务永久关闭",
            "未获运行授权时只报告合同证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        self.assertIn("缓存远端引用、实时远端检查和发布制品", README_TEXT)
        self.assertIn("正式入口验证现实可用性", README_TEXT)

    def test_new_file_writers_activate_construction_sites_and_residue_checks(
        self,
    ) -> None:
        for fragment in (
            "新增写入能力先建立副作用激活图",
            "原本只负责构造对象的调用点也可能成为新的生产者",
            "正式入口、CLI、后台任务、桌面窗口、smoke、测试 fixture 和共享 helper",
            "不得静默创建工作区",
            "实际测试必须消费副作用激活图",
            "不能为了得到干净结果直接删除来源不明的文件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("潜在写入生产者", README_TEXT)
        self.assertIn("删除未获授权时", README_TEXT)

    def test_deferred_desktop_ui_work_survives_only_its_owned_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "延迟界面工作与对象生命周期",
            "`callLater`、排队信号",
            "生命周期足以覆盖实际执行期",
            "只服务当前页面或面板的工作随该对象销毁并停止",
            "继续排空事件循环",
            "即使没有改变退出码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        self.assertIn("销毁后访问、过期回调和延迟写入", README_TEXT)

    def test_autonomous_closure_and_terminal_lifecycle_are_active(self) -> None:
        for fragment in (
            "内部轮次不是新的授权边界",
            "同一用户结果、同一受影响链和已冻结权限",
            "不能修改产品来迁就测试驱动或夹具",
            "新鲜运行证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    SKILL_TEXT + REMEDIATION_TEXT,
                )

        for fragment in (
            "终止原因、结果状态和传输收尾",
            "事件消费完成",
            "有界时间内以退出码 0 正常退出",
            "标准输出和标准错误的编码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        for fragment in (
            "当前活动窗口或表面",
            "非离屏且具有非零几何",
            "确认、已读或不再重放",
            "重新取得当前活动元素",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn(
            "发起者、终止原因、结果状态、传输收尾",
            LOG_TEXT,
        )
        self.assertIn(
            "内部轮次不是新的授权边界",
            README_TEXT,
        )
        self.assertNotIn("执行节奏与停止判断", AGENT_TEXT)
        self.assertNotIn("持久意图", AGENT_TEXT)

    def test_media_led_sections_preserve_content_value_and_scroll_ownership(
        self,
    ) -> None:
        for fragment in (
            "逐章建立内容价值合同",
            "不能替代名称、说明、过程、结果与有效入口",
            "说不清职责、关系和移除后果的素材不生成、不拆分、不进入页面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "章节推进合同",
            "有效滚动距离与真实内容视口高度之比",
            "不能用通用卡片、角色立绘或装饰素材替代项目本身",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

        for fragment in (
            "不能用“统一删除位移和视差，只保留透明度与颜色”",
            "有效滚动屏数 = 该章实际消费的滚动距离",
            "进入构图和舞台完整就位后的内部推进使用独立进度边界",
            "后续普通章节恢复浏览器或平台的原生滚动所有权",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "取得开始、一个或多个有信息增量的中段、结束释放",
            "内部动画没有在舞台完整就位前结束",
            "文件存在、资源加载成功和风格相近不能证明",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_restricted_execution_alternatives_have_a_complete_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "受限执行路径合同",
            "清理动作与清理权限",
            "借用无关项目",
            "策略或安全边界已经明确拒绝",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "### 受限执行路径与临时产物",
            "最小只读探测或无副作用预演",
            "准确目标根与临时根",
            "预期体积",
            "正式消费者",
            "清理授权",
            "等价写入",
            "写回前重新读取目标",
            "清理结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_page_order_and_scroll_performance_are_preventive_contracts(
        self,
    ) -> None:
        for fragment in (
            "先建立正式页面与状态顺序",
            "滚动性能责任合同",
            "脚本执行、样式与布局、绘制、合成、媒体解码与上传、资源加载与并发",
            "全部顺序消费者读取同一真源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "### 滚动性能先区分成本",
            "输入与主线程中的监听、脚本和时间线",
            "过场只消费目标解析结果",
            "不保存第二份目的地",
            "组件或文档顺序",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "全部顺序消费者",
            "媒体解码与上传",
            "恢复完整内容和正常用户路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_layered_scroll_experience_selects_architecture_before_tuning(
        self,
    ) -> None:
        for fragment in (
            "全局页面推进、章节内部演出、局部步进、媒体完成或导航恢复",
            "唯一主架构",
            "不能继续只调阈值、冷却时间或动画速度",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "体验保证与取舍合同",
            "相邻内容何时允许可见",
            "不能同时硬性保证完全原生的连续手感",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "多层滚动先选唯一主架构",
            "原生内容流",
            "连续驻留舞台",
            "固定全屏换场",
            "分页落页",
            "有限局部步进",
            "低频媒体门",
            "进入构图",
            "完整就位",
            "内部演出",
            "终态释放",
            "再次进入",
            "自然反向",
            "保持终态",
            "明确重播",
            "按钮可以主动查看上一项，而反向滚轮可以直接交还页面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "多个跨页面症状",
            "方向性输入所有权",
            "旧控制器退出条件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "逐阶段对照所选主架构的硬保证",
            "第一下有效反向输入",
            "单项切换延迟、最终落点或一张稳定截图通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("先选择每个区域的唯一主架构", README_TEXT)

    def test_existing_objects_use_explicit_relation_changes_and_accepted_variances(
        self,
    ) -> None:
        for fragment in (
            "已有对象使用一份关系变更合同",
            "目标所有者、相邻锚点与顺序",
            "“新增”只创建点名对象",
            "其余已经确认的关系继续保持",
            "把已接受差异从阻塞项中分开",
            "不得阻塞本轮交付的现有差异",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "直接消费改动前预防中的对象关系变更表",
            "不能把截图像素坐标保存为第二套布局真源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "读取已经冻结的接受差异台账",
            "不能在验收层自行改写合同",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("避免把“新增”做成替换", README_TEXT)
        self.assertIn("不会借通用最佳实践重新扩大范围", README_TEXT)

    def test_visual_references_and_asset_batches_keep_source_specific_evidence(
        self,
    ) -> None:
        for fragment in (
            "每项输入分别建立素材证据合同",
            "不得从其它素材迁入的称号、符号、道具和设定",
            "每项交付必须能够独立使用",
            "视觉参考还要拆开结构、互动机制、运动关系、构图、内容密度与视觉皮肤",
            "不自动复制参考的配色、材质、容器、品牌元素和文案",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "参考图是用户明确点名关系的证据",
            "当前项目继续负责视觉皮肤的已接受表面或设计系统",
            "只有在当前内容确实需要分组、裁切、状态、命中或表面层级时才成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

        for fragment in (
            "面向后续动画的首帧建立运动空间合同",
            "各自的运动包络",
            "四周安全区与最终消费者可能遮挡的区域",
            "不是已经完成动作",
            "不能均匀围满主体并侵占运动包络",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LAYOUT_RESPONSIVE_TEXT)

        self.assertIn("只迁入用户实际点名的关系", README_TEXT)
        self.assertIn("不从同批其它图片或偶然生成结果补造设定", README_TEXT)

    def test_shared_visual_anchor_governs_surface_different_asset_batches(
        self,
    ) -> None:
        for fragment in (
            "共享视觉锚点与派生素材的依赖顺序",
            "全批次共享的视觉与构图变量",
            "只属于单项状态的动作、场景和特效变量",
            "直接依赖它的图片、视频、转场和界面消费者",
            "必须失效、重做或重新验收的派生物",
            "用户要求先判断共同锚点、再决定是否调整依赖状态时",
            "不受该变量影响的单项状态保持有效",
            "只消费已确认的共享锚点和仍然有效的派生物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "第一视觉焦点及其成立依据",
            "不得抢焦点的元素",
            "色相角色、面积、明度与饱和度关系",
            "尺度、透视、遮挡和虚实",
            "结构转折、材质响应、主辅光和接触关系",
            "不能由“3D、电影感、写实渲染”等标签代替",
            "用户纠正其中一个变量时只更新相应字段",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

        self.assertIn("锚点改变后，受影响的旧派生物会失效", README_TEXT)
        self.assertIn("不用“炫酷、梦幻、3D”替代", README_TEXT)

    def test_longer_than_expected_work_exposes_real_state_without_scope_drift(
        self,
    ) -> None:
        for fragment in (
            "一个表面上是短动作的任务",
            "扩展原因、已经完成的检查点与证据",
            "执行 / 等待 / 验证 / 决策",
            "下一项可观察结果",
            "不能把内部阅读、工具调用或技能步骤冒充用户结果",
            "与结果无关的审计也不能让简单动作无边界扩张",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "把它视为过程透明度证据",
            "不是增加无意义播报",
            "不能用“流程需要”掩盖范围扩张",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("不会用“还在处理”反复占位", README_TEXT)

    def test_technical_migration_does_not_authorize_visual_redesign(self) -> None:
        for fragment in (
            "把“实现怎样迁移”和“呈现是否改变”拆成两份授权与验收",
            "技术迁移与呈现变化分开授权",
            "实现迁移合同",
            "呈现保护合同",
            "设计改造入口",
            "保护区不能借改版被替换",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT + PREVENTION_TEXT)

        for fragment in (
            "技术迁移先证明呈现保护合同",
            "最早可见表面、加载过程、首个稳定页面",
            "不能用改版区的“更好看”抵消保护区回归",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("把实现责任迁移和界面呈现变化分开", README_TEXT)
        self.assertIn("不会被当成“更有设计感”的理由", README_TEXT)

    def test_external_media_production_uses_real_capabilities_and_lineage(
        self,
    ) -> None:
        for fragment in (
            "外部媒体生产能力与派生链",
            "过去经验和文件名不能补造不存在的选项",
            "时序来源再取帧",
            "可抠像源再合成",
            "批次源再拆分",
            "可直接使用 / 只使用已指明部分 / 需要重新生产 / 不进入项目",
            "完整不等于堆叠同义形容词",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "准确源身份、中间处理、派生物和最终消费者",
            "只查看生成任务成功、批次大图、导出目录或消费端临时路径不能证明正式素材成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("先冻结当前真实支持的参考输入", README_TEXT)
        self.assertIn("不会因为文件已经生成就替它补造用途", README_TEXT)

    def test_transparent_media_noise_is_governed_across_the_derivative_chain(
        self,
    ) -> None:
        for fragment in (
            "透明媒体的低 Alpha 画布噪点与派生产物分叉",
            "整幅低 Alpha 噪点、主体边缘污染和编码伪影",
            "固定阈值不能脱离素材证据成为默认值",
            "各交付编码与 poster",
            "至少一明一暗且与缺陷有反差的背景",
            "浏览器能播放、请求成功或单张透明网格预览都不能单独通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERFACE_PROBLEM_TEXT)

        for fragment in (
            "母版、Alpha 处理、交付编码、poster、正式清单和活动消费者",
            "Alpha 数值与空间分布",
            "只读“存在 Alpha”或 `alpha_mode`",
            "只修播放文件而不重新生成同源 poster",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("区分整幅低 Alpha 噪点、边缘污染和编码伪影", README_TEXT)
        self.assertIn("不用“带 Alpha”或“浏览器能播放”代替最终画面", README_TEXT)

    def test_user_visible_promises_require_branch_level_evidence(self) -> None:
        for fragment in (
            "每项用户可见承诺",
            "正常触发或入口",
            "实际执行分支",
            "只能证明未被绕过的部分",
            "已验证、仅诊断、未验证或受阻",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SKILL_TEXT)

        for fragment in (
            "为用户可见承诺建立证据覆盖表",
            "必须经过的实际分支",
            "当前状态和允许交付措辞",
            "不能证明默认启动器确实打开了网页",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("承诺覆盖", REMEDIATION_TEXT)
        self.assertIn("不会用一条成功链代替整个交付", README_TEXT)
        self.assertIn(
            "纯只读解释没有状态改变或运行承诺时",
            SKILL_TEXT,
        )

    def test_confirmed_plan_is_revalidated_against_current_targets(self) -> None:
        for text in (SKILL_TEXT, LEARNING_TEXT):
            for fragment in (
                "用户确认后、开始写入前",
                "与方案快照比较",
                "行为合同、影响文件、直接消费者、验证方法或用户可见结果",
                "重新确认",
                "非冲突变化",
            ):
                with self.subTest(fragment=fragment, text=text[:20]):
                    self.assertIn(fragment, text)

        self.assertIn("确认只覆盖用户看到的那份方案", README_TEXT)

    def test_task_replacement_preserves_partial_delivery_state(self) -> None:
        for text in (SKILL_TEXT, LEARNING_TEXT, README_TEXT):
            for fragment in (
                "新的独立请求",
                "已经写入但尚未完成验证",
                "已经成立的证据",
                "尚未验证的",
            ):
                with self.subTest(fragment=fragment, text=text[:20]):
                    self.assertIn(fragment, text)

        self.assertIn("新请求不授权继续、回退或补做上一结果", SKILL_TEXT)
        self.assertIn("新请求不授权继续或回退旧结果", LEARNING_TEXT)
        self.assertIn("新请求不会被解释成继续或回退旧结果的授权", README_TEXT)

    def test_protocol_migrations_use_real_history_and_serialized_contracts(
        self,
    ) -> None:
        for fragment in (
            "只验证当前版本新数据不能证明既有用户数据可用",
            "实际序列化文件、数据库记录或线上消息",
            "字段省略与显式 `null`",
            "内存模型有效不能替代落地表示有效",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        ordered = (
            "当前版本从零新建",
            "由旧版本正式生产或保存的真实历史状态",
            "正式序列化结果通过当前合同校验",
            "迁移失败时原状态和身份保持可恢复",
            "迁移后关闭并重新打开",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("协议、schema 或持久状态迁移的代表性链", PREVENTION_TEXT)
        self.assertIn("消费端直接手写旧对象或迁移后对象", PREVENTION_TEXT)

        for fragment in (
            "真实旧状态应来自旧版本生产者",
            "失败注入后原版本、原内容和原身份保持可恢复",
            "实际序列化结果通过当前合同校验",
            "当前消费者关闭并重新打开",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        self.assertIn("正式序列化器实际落下的文件", README_TEXT)
        self.assertIn("测试手写一份 JSON 不能替代", README_TEXT)

    def test_public_api_migrations_include_verifiers_and_public_release_state(
        self,
    ) -> None:
        for fragment in (
            "验证与发布脚本、真实用户链工具",
            "不能等昂贵的最终链首次运行时才发现",
            "私有状态或已经退出的 helper",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("验证与发布脚本、真实用户链工具", REMEDIATION_TEXT)

        for fragment in (
            "等待应用公开的释放完成或释放失败状态",
            "私有 Future、内部 Promise、对象暂时消失和固定睡眠",
            "不能继续调用打开入口制造第二条生命周期",
            "验证与发布脚本必须在旧入口退出前一起迁移",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        self.assertIn("等待公开的释放完成或失败状态", README_TEXT)

    def test_audit_separates_feature_merge_and_publication_readiness(
        self,
    ) -> None:
        ordered = (
            "**功能可用**",
            "**可合并**",
            "**可发布**",
        )
        positions = [PROJECT_AUDIT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不能用其中一项替代另一项",
            "验证与发布脚本",
            "干净检出能够重建并消费当前制品",
            "不能拼接成更高一层就绪结论",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        self.assertIn("把功能可用、可合并与可发布分别判断", README_TEXT)


if __name__ == "__main__":
    unittest.main()
