from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
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
USER_ENVIRONMENT_TEXT = (
    SKILL_ROOT / "references" / "user-environment-governance.md"
).read_text(encoding="utf-8")
HARD_DIAGNOSTIC_TEXT = (
    SKILL_ROOT / "references" / "hard-to-reproduce-diagnostics.md"
).read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT = (
    SKILL_ROOT / "references" / "project-audit.md"
).read_text(encoding="utf-8")
STRUCTURED_DATA_TEXT = (
    SKILL_ROOT / "references" / "structured-data-boundary.md"
).read_text(encoding="utf-8")
MODEL_OPERATION_TEXT = (
    SKILL_ROOT / "references" / "model-mediated-operation-governance.md"
).read_text(encoding="utf-8")
DURABLE_OPERATION_TEXT = (
    SKILL_ROOT / "references" / "durable-operation-governance.md"
).read_text(encoding="utf-8")
PROJECT_RESEARCH_TEXT = (
    SKILL_ROOT / "references" / "project-research.md"
).read_text(encoding="utf-8")
UX_DESIGN_TEXT = (
    SKILL_ROOT / "references" / "ux-design.md"
).read_text(encoding="utf-8")
LOCAL_WORKSPACE_TEXT = (
    SKILL_ROOT / "references" / "local-file-workspace-governance.md"
).read_text(encoding="utf-8")


class ConversationLearnedGovernanceTests(unittest.TestCase):
    def test_read_only_verbs_are_a_hard_project_write_boundary(self) -> None:
        self.assertIn("按照主路由已经选定的模式执行", ARCHITECTURE_TEXT)
        self.assertIn("本方法不重新解释用户措辞", ARCHITECTURE_TEXT)
        self.assertNotIn("用户只说检查、审计、诊断", ARCHITECTURE_TEXT)
        self.assertIn("检查是硬只读边界", README_TEXT)

    def test_every_turn_rechecks_frozen_authority_before_state_change(self) -> None:
        self.assertIn("第一次改变状态前都会重新核对", README_TEXT)
        self.assertIn("不会进入项目写入", README_TEXT)

    def test_continuation_cannot_promote_a_completed_read_only_result(self) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "只从用户最近一次明确动作及其尚未完成的结果恢复合同",
            "审计发现、助手建议、内部计划、目标名称、待办清单和自动提示",
            "都不能补造新结果或写入权限",
            "原结果已经交付",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, shared)

        for fragment in (
            "都只从最近一次用户明确动作及其尚未完成的结果恢复合同",
            "都不会变成新的实施授权",
            "只读结果已经交付",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_shared_boundaries_remain_on_every_project_steward_route(self) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "普通业务功能仍由当前开发任务负责",
            "联网、下载、安装、运行、生成、写入、移动、归档、删除、提交、推送和发布分别授权",
            "内部轮次、自动续跑和上下文压缩不是新的授权边界",
            "工作从短动作扩展为多阶段",
            "新的独立请求替换尚未完成的结果",
            "逐项保留输出、错误和退出状态",
            "任何一项会让整批提前中止时改为独立执行",
            "只把被遮蔽、未执行或状态未知的项目单独补跑",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, shared)

    def test_failed_execution_of_an_existing_rule_changes_consumers(self) -> None:
        for fragment in (
            "已有能力没有被执行",
            "最早没有消费该规则的路由或动作门槛",
            "表层不同的代表性请求",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn(
            "不会再堆一条同义原则",
            README_TEXT,
        )

    def test_learning_attribution_requires_the_skill_to_have_been_active(
        self,
    ) -> None:
        for fragment in (
            "最后判断历史责任归属",
            "目标 Skill 在历史任务中的活动身份",
            "宿主与项目规则允许自动路由且实际选中",
            "因用户约束、触发条件或任务边界从未启用",
            "不能归因于目标 Skill",
            "候选仍按当前职能、能力差距和价值决定是否迭代",
            "项目规则、模板采用或触发策略作为独立结果确认",
            "不能从“当前 Skill 现在已经有规则”反推",
            "不能因为当时未启用就拒绝一个已经证明的当前能力缺口",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        causal = LEARNING_TEXT.index("## 3. 对异常结果先做因果排序")
        details = LEARNING_TEXT.index("### 因果主题确定后，先恢复构成性细节")
        comparison = LEARNING_TEXT.index("### 抽象前逐项比较当前具体能力")
        abstraction = LEARNING_TEXT.index(
            "### 比较完成后再提炼共同路径与特殊维度"
        )
        value = LEARNING_TEXT.index("候选能力只有同时满足以下条件")
        attribution = LEARNING_TEXT.index("### 最后判断历史责任归属")
        self.assertLess(causal, details)
        self.assertLess(details, comparison)
        self.assertLess(comparison, abstraction)
        self.assertLess(abstraction, value)
        self.assertLess(value, attribution)

    def test_learning_compares_applicability_and_consumer_scope(self) -> None:
        for fragment in (
            "修改前适用请求、入口和消费者",
            "修改后适用请求、入口和消费者",
            "共享规则被缩窄",
            "相似文字、reference 可达或结构测试通过",
            "只有上位方法或相似术语",
            "具体细节已经存在",
            "只有大方向",
            "值得吸收的新细节",
            "不吸收",
            "现象、失败绕行、残留、项目专名和偶然参数",
            "绕行或残留本身只有在形成独立、反复可识别的用户结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_learning_audits_role_scope_from_positive_and_corrective_evidence(
        self,
    ) -> None:
        for fragment in (
            "目标 Skill 当前承担什么：",
            "历史中反复出现的用户最终结果：",
            "哪些相邻能力构成同一个上层角色：",
            "当前职能过窄、过宽还是适当：",
            "默认能力与按需能力：",
            "操作权限是否变化：",
            "用户没有继续纠正、没有回复或没有修改",
            "历史中没有出现某项能力",
            "重新建立整体行为合同",
            "一次整体确认",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        for fragment in (
            "不会只在纠偏时学习",
            "不会把沉默误当成认可",
            "不能因为历史里没有出现某项能力就自动删除它",
            "不要求用户逐项补全",
            "职能范围和操作权限始终分开",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

        self.assertIn("判断职能边界", AGENT_TEXT)

    def test_self_evolution_reports_the_actual_validation_level(self) -> None:
        ordered = (
            "结构受保护",
            "当前任务行为核对",
            "独立冷启动调用",
        )
        skill_positions = [LEARNING_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(skill_positions, sorted(skill_positions))

        for fragment in (
            "不能互相冒充的等级",
            "不依赖当前纠偏上下文的新鲜调用真实触发目标 Skill",
            "最终只报告实际达到的最高等级",
            "文件校验通过不能写成行为已经核对",
            "当前任务中的规则推演也不能写成已经独立证明未来调用稳定",
            "否则准确停在当前任务行为核对",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_run_or_build_permission_does_not_expand_write_authority(
        self,
    ) -> None:
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
            "这不是分类时的二选一",
            "共同机制：去掉专项名称和表面症状后",
            "特殊条件改变什么：识别 / 观测 / 动作 / 验证 / 停止位置",
            "两层怎样共同消费",
            "各自唯一真源和消费者",
            "一个结果同时符合多个特殊条件时可以组合消费",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("再进入价值或归因门槛", LEARNING_TEXT)

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
            "开始读取前先冻结本次历史材料边界",
            "不能因为链接仍在历史里就自动打开",
            "不能为了显得完整而递归遍历所有引用",
            "历史材料边界：",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("“这个会话”只指当前任务", README_TEXT)

    def test_source_scope_changes_rebuild_the_active_evidence_boundary(
        self,
    ) -> None:
        for fragment in (
            "明确收窄、撤回或重新扩展材料范围",
            "立即停止尚未执行的读取",
            "以最新明确要求重新冻结边界",
            "已读取但不参与本轮结论",
            "不能继续影响当前台账、能力判断或方案",
            "只有在新边界中登记后才恢复为证据",
            "早先一次排除也不永久阻止用户重新纳入",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_evidence_acquisition_is_complete_and_failure_isolated(self) -> None:
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

    def test_sources_are_preflighted_before_unbounded_reads_or_git(self) -> None:
        for fragment in (
            "发起可能无界的读取前",
            "行数、字节数、分页能力或输出预算",
            "只有已经证明能够在一次返回中完整容纳的来源才整份读取",
            "准确项目根直接存在 `.git`",
            "不能先在任意当前目录运行 Git",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("只有能够一次完整容纳的来源才整份读取", README_TEXT)
        self.assertIn("不会先在任意目录运行再靠报错找仓库", README_TEXT)

    def test_diagnostics_separate_facts_hypotheses_and_root_causes(self) -> None:
        for fragment in (
            "观察到的事实、待验证假设或已确认根因",
            "进度说明和最终报告",
            "竞争解释和下一项判别证据",
            "定位第一处偏离并排除关键竞争解释",
            "新证据推翻原假设时明确更新状态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        self.assertIn(
            "观察到的事实、待验证假设或已确认根因",
            README_TEXT,
        )

    def test_real_producer_assertions_follow_identity_and_fact_category(
        self,
    ) -> None:
        for text in (PREVENTION_TEXT, REMEDIATION_TEXT, README_TEXT):
            for fragment in (
                "稳定语义身份",
                "对象总数、列表位置",
                "可编辑或持久事实",
                "派生或瞬态投影",
                "合法对象",
            ):
                with self.subTest(fragment=fragment, text=text[:20]):
                    self.assertIn(fragment, text)

        self.assertIn("正式生产者的本轮结果取得目标", PREVENTION_TEXT)
        self.assertIn("权威状态、持久化和重开", PREVENTION_TEXT)
        self.assertIn("正式计算或展示消费者", PREVENTION_TEXT)

    def test_verbose_commands_preserve_recoverable_evidence_before_launch(
        self,
    ) -> None:
        for fragment in (
            "本次执行尝试的稳定身份",
            "准确命令、工作目录、工具版本与输入身份",
            "工具原生报告 / 受控标准输出与错误日志 / 可回读结构化结果",
            "可能争用的端口、锁、缓存、设备或输出目录",
            "单独保存的退出状态",
            "查询工具自身失败、只返回部分进程或没有输出",
            "才允许启动新的执行尝试",
            "不增加日志仪式",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        for fragment in (
            "长而嘈杂或需要跨轮观察的命令",
            "等待或轮询自身失败只让相应证据保持未知",
            "不会启动新的执行尝试",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_windows_tool_probes_and_long_tasks_preserve_user_observation(
        self,
    ) -> None:
        for fragment in (
            "确认它是包装器还是原生目标",
            "控制台输出还是打开可见窗口",
            "也不能根据文件名猜测启动行为",
            "优先使用已经核验的原生控制台程序",
            "启动前先告诉用户会出现什么窗口、用途和停止方式",
            "不能让用于发现参数的探测意外弹窗",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        for fragment in (
            "不以单个前台阻塞调用启动",
            "能够让出控制权、继续等待或后台运行的执行方式",
            "可回读的进程身份、增量输出和退出状态",
            "阶段、证据或预计停止位置发生变化时向用户说明",
            "状态没有变化时不重复刷屏",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

    def test_validation_gates_prove_applicability_before_blocking(self) -> None:
        for fragment in (
            "先证明验收门槛适用",
            "同一个仓库、相邻模块、相似主题或任务规模较大",
            "验证器必须完成迁移",
            "没有剩余承诺单独依赖它时",
            "后续改动若重新命中触发条件",
            "门槛适用性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("规则的精确触发条件确实被本次变化命中", README_TEXT)

    def test_behavior_baseline_separates_intent_current_state_and_history(
        self,
    ) -> None:
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
            "独立行为、运行假设与授权边界",
            "整体采用 / 局部吸收 / 拒绝",
            "参考项目自己的基准只能说明它在自身条件下成立",
            "代表性工作负载矩阵",
            "参考项目中用户实际执行的动作",
            "操作过程中连续看到的反馈",
            "最终可见结果和减少的理解或操作成本",
            "随后才映射到字段、接口和内部模块",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT + PROJECT_RESEARCH_TEXT)

        self.assertIn("不会建立第二套状态、时间轴、缓存或恢复边界", PREVENTION_TEXT)
        self.assertIn("用当前项目的代表性负载决定", README_TEXT)

    def test_operational_invariants_gate_complexity_and_content_defaults(
        self,
    ) -> None:
        for fragment in (
            "用业务不变量限制架构复杂度与内容默认值",
            "尚无证据、不得进入核心路径的极端场景",
            "不能让一个未来可能发生的分支永久提高所有普通输入的成本",
            "内容资格合同",
            "空容器创建、预先分配的编号、渲染顺序或测试夹具",
            "后续内容到达、重新枚举或界面重建不得再次抢回默认值",
            "业务不变量与复杂度",
            "内容资格默认值",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("未经用户目标、产品合同或真实数据证明的最坏情况", README_TEXT)
        self.assertIn("空容器不会抢占默认值", README_TEXT)

    def test_new_protocol_surfaces_require_a_real_consumer_and_stay_thin(
        self,
    ) -> None:
        for fragment in (
            "自动化协议入口先证明消费需求",
            "CLI、API 或机器可读能力描述",
            "已经确定的消费者及其正式调用入口",
            "仅靠“以后可能有用”",
            "MCP、RPC 服务、daemon、插件桥接",
            "停在暂不采用",
            "唯一公共应用边界外侧的薄适配器",
            "不得复制业务任务、领域状态、持久化、恢复、参数语义或错误解释",
            "适配器和说明文档都是消费者",
            "同一业务请求分别经过原入口和新适配器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_partition_sensitive_differences_preserve_identity_before_merge(
        self,
    ) -> None:
        for fragment in (
            "分区语义先于全局聚合",
            "语义分区键及其正式来源",
            "每个分区的变更前与变更后状态",
            "先在每个语义分区内计算",
            "不能先把各分区状态做全局并集",
            "提前聚合会丢失归属",
            "一个分区仍存在的同值事实掩盖另一个分区已经发生的变化",
            "同一值、区间或资源在一个分区仍然存在",
            "正式结果必须保留后一个分区的差异及身份",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_mechanical_rewrites_stay_inside_the_authorized_semantic_scope(
        self,
    ) -> None:
        for fragment in (
            "只改变本次获准的路径和语义范围",
            "格式化器、行尾转换或批量改写运行前记录范围与基线",
            "运行后检查实际差异",
            "缩小工具范围或从最新基线重新应用本轮修改",
            "不能把机械噪声当成顺带整理",
            "机械改写范围",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_reference_capabilities_cross_a_formal_adoption_boundary(self) -> None:
        for fragment in (
            "来源能力台账",
            "名称与别名只负责发现",
            "同一可观察行为和执行合同只算一项能力",
            "一份目标规范记录",
            "由目标规范确定性生成",
            "公开采用或物化入口",
            "演示页、样例或画廊只证明预览",
            "制作期能力还是共享契约",
            "来源身份、内容哈希和适用授权说明",
            "工具拥有的生成文件",
            "用户拥有的清单",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT + PROJECT_RESEARCH_TEXT)

        for fragment in (
            "从一份新鲜目标状态执行公开发现与采用示例",
            "由正式消费者读取并形成最终结果",
            "重复行为应被拒绝或合并为别名",
            "不比较浏览器、序列化器或格式化器可能合法归一化的偶然字符串",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("演示或画廊只能证明预览", README_TEXT)
        self.assertIn("工具只整体重写自己拥有的生成文件", README_TEXT)

    def test_reference_features_require_target_object_and_entry_evidence(
        self,
    ) -> None:
        for fragment in (
            "核心对象、现有对象操作、获取渠道、视图或筛选、状态反馈还是可选集成",
            "与哪个现有对象共享创建后的保存、查找、编辑、删除、恢复和交付生命周期",
            "来源项目的入口层级是否有目标项目自己的用户任务或产品合同支持",
            "独立且反复发生的结果、关键决定、生命周期或恢复路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_RESEARCH_TEXT)

        for fragment in (
            "功能先归入用户对象，再决定入口层级",
            "获取渠道、文件格式、供应商、生成方式和外部协议",
            "通过现有统一入口、对象内行动或次级入口进入",
            "主导航、主要按钮和独立工作区只服务独立且反复发生的用户结果",
            "不由实现复杂度、来源功能数量或参考界面替用户决定",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, UX_DESIGN_TEXT)

        for fragment in (
            "候选职责：核心对象 / 现有对象操作 / 获取渠道 / 视图或筛选 / 状态反馈 / 可选集成",
            "结果进入目标项目后若与现有对象共享同一生命周期和主要行动",
            "停止在可选择的入口方案",
            "自动化能够定位控件、几何没有裁切、界面矩阵通过",
            "不能证明入口层级正确",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT + IMPLEMENTATION_TEXT)

        self.assertIn("参考产品里的功能不会因为有独立页面", README_TEXT)

    def test_long_ordered_content_separates_access_intents_before_replacement(
        self,
    ) -> None:
        for fragment in (
            "长期有序内容先拆分访问意图",
            "连续追溯、定点跳转、查询与筛选以及人为分组",
            "不能因为新增一种访问方式就静默退出另一种",
            "目标平台上的自然输入与即时反馈",
            "首次用户可发现的备用入口",
            "哪些入口共享同一结果，哪些必须并存",
            "现有入口的保留、移动或退出依据",
            "只有用户结果已经明确退出",
            "后台复用同一查询或新入口看起来更强",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, UX_DESIGN_TEXT)

        for fragment in (
            "连续追溯、定点跳转、查询筛选和人为分组",
            "不会静默删掉原有的连续浏览结果",
            "平台自然输入、可发现的备用入口",
            "都不能单独证明旧入口可以退出",
        ):
            with self.subTest(readme_fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_design_selects_the_object_presentation_archetype_before_styling(
        self,
    ) -> None:
        ordered = (
            "当前界面是否服务正确的用户结果与旅程阶段",
            "内容是否使用适合识别、比较和操作的基本形态",
            "排版、色彩、组件和互动是否加强前述关系",
        )
        positions = [DESIGN_METHOD_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "核心对象的主要识别线索与呈现原型",
            "进入比例、密度和视觉皮肤前",
            "文字、数值、状态、图像还是时间内容",
            "真实内容的正式生产者和消费者",
            "所选原型和不采用其它原型的理由",
            "状态行适合持续扫描状态",
            "缩略图或封面卡片适合依靠视觉内容识别、选择和重开对象",
            "这些原型是任务与内容关系",
            "先确认正式预览来源能够进入最终组件",
            "把旧行机械排进网格都没有解决结构问题",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

    def test_shared_contract_identity_and_extensible_fields_have_one_owner(
        self,
    ) -> None:
        for fragment in (
            "公共合同先核对身份",
            "合同名称与版本",
            "权威生产者及其来源身份",
            "正式 schema 或规范化内容身份",
            "合同身份碰撞",
            "可扩展字段由生产者的机器可读描述拥有",
            "稳定字段身份、默认值、范围、单位、建议控件和是否可动画",
            "消费者只把建议控件映射到自己的界面组件",
            "说明文档是契约消费者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "合同身份碰撞",
            "权威生产者分配新的协议版本",
            "唯一同步入口单向更新快照",
            "不能原地改写同一版本的多份副本",
            "实际操作集合与参数 schema",
            "不能让运行时代码迎合过期说明",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_cross_root_contracts_have_independent_delivery_evidence(
        self,
    ) -> None:
        for fragment in (
            "跨项目根共享合同与交付账本",
            "权威合同所有者",
            "唯一同步入口和单向同步方向",
            "带来源身份的派生快照",
            "相邻项目的绝对路径",
            "同步快照通过不等于跨项目互操作通过",
            "本地实现、各根正式验证、跨项目互操作和每个根的远程发布",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("跨项目根的发布状态分别成立", PUBLICATION_TEXT)

    def test_cross_project_adoption_and_runtime_binding_are_separate(self) -> None:
        for fragment in (
            "跨项目接入分开实现、互操作、采用和运行绑定",
            "能力实现：生产者或公共边界已经具备目标能力",
            "隔离互操作通过不等于当前实例已经正式采用",
            "违反任一参与系统的强制不变量",
            "不得写入持久配置",
            "使用会话级覆盖",
            "稳定运行入口和持久配置保持为未完成或受阻",
            "当前实例采用与运行绑定",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "持久配置只能绑定稳定运行入口",
            "项目构建输出、缓存、下载解压目录或临时目录",
            "文件存在且版本命令成功",
            "不把临时路径伪装成普通长期配置",
            "会话级参数、环境变量或调用入口",
            "安装或复制到持久工具根",
            "不能先持久绑定构建产物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        for fragment in (
            "能力实现、各根正式验证、隔离互操作、当前实例正式采用",
            "构建或临时入口只用于会话级验证",
            "不会把它伪装成长期工具路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_self_evolution_requires_a_second_stage_confirmation(self) -> None:
        section = MAIN_TEXT.split(
            "## 对话学习与自我进化",
            1,
        )[1].split("## 改动前预防", 1)[0]
        ordered = (
            "明确要求吸收、自我进化、更新、优化或迭代 Project Steward",
            "先交付未来行为、职能边界、代表性输出、影响文件和验证方式并停下",
            "用户确认该方案后才修改活动 Skill",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "references/conversation-learning-and-self-evolution.md",
            section,
        )

        self.assertIn("然后返回主路由并停止", LEARNING_TEXT)
        self.assertIn("写入权限由主路由的两阶段确认结果决定", LEARNING_TEXT)

    def test_self_evolution_router_stays_small_and_keeps_every_reference(self) -> None:
        self.assertLessEqual(len(MAIN_TEXT.splitlines()), 220)
        self.assertLessEqual(len(MAIN_TEXT), 14_000)

        routed = set(re.findall(r"`(references/[^`]+\.md)`", MAIN_TEXT))
        expected = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in (SKILL_ROOT / "references").glob("*.md")
        }
        self.assertEqual(routed, expected)

        for fragment in (
            "只拥有路由、触发条件、读取顺序、权限、输出和停止位置",
            "每条新增规则指定唯一活动所有者",
            "不得超过 220 行或 14,000 个字符",
            "无法在预算内保留既有能力",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MAIN_TEXT)

        for method_detail in (
            "观察到的现象或结果",
            "每层分别记录证据",
            "自我进化同时治理主文件体积",
        ):
            with self.subTest(method_detail=method_detail):
                self.assertIn(method_detail, LEARNING_TEXT)
                self.assertNotIn(method_detail, MAIN_TEXT)

    def test_anomalous_results_rank_root_cause_before_workaround_and_residue(
        self,
    ) -> None:
        ladder = (
            "观察到的现象或结果",
            "直接触发或直接原因",
            "合法保护或约束",
            "架构或根所有权原因",
            "临时绕行",
            "残留或放大因素",
        )
        causal_section = LEARNING_TEXT.split(
            "## 3. 对异常结果先做因果排序",
            1,
        )[1].split("## 4. 对每个结果同时提炼正反两面", 1)[0]
        ladder_text = causal_section.split("```text", 1)[1].split("```", 1)[0]
        positions = [ladder_text.index(fragment) for fragment in ladder]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "主要学习主题选择最早一个",
            "不能补造更深的架构解释",
            "不得覆盖更早的主要原因",
            "多个彼此独立的用户结果继续分组",
            "旧主要原因取得的确认随之失效",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        main_order = (
            "按结果恢复完整过程",
            "沿因果层级确定主要学习主题",
            "判断可迁移性、职能边界和正式所有者",
        )
        main_positions = [MAIN_TEXT.index(fragment) for fragment in main_order]
        self.assertEqual(main_positions, sorted(main_positions))
        self.assertIn("失败、纠正、保护拦截、临时绕行或残留", MAIN_TEXT)
        self.assertIn("只有成功结果且不存在这些信号时，不加载根因方法", MAIN_TEXT)

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
            "职能边界",
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
                self.assertIn(contract, PREVENTION_TEXT)
                self.assertIn(contract, REMEDIATION_TEXT)

        self.assertIn(
            "references/change-prevention.md",
            MAIN_TEXT,
        )
        self.assertIn(
            "references/root-cause-remediation.md",
            MAIN_TEXT,
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

    def test_architecture_metrics_preserve_audit_baseline_lineage(self) -> None:
        ordered = (
            "审计来源：当前工作树 / 指定提交 / 指定产物",
            "内容身份：取得时刻、版本或哈希",
            "聚合定义：单文件 / 类型 / 逻辑所有者",
            "既有未提交变化：",
        )
        positions = [ARCHITECTURE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "基线是审计当时磁盘上的实际内容",
            "不能用 Git HEAD 替代",
            "旧基线失效",
            "追溯到同一审计基线和同一聚合定义",
            "审计快照到当前状态",
            "本任务实际改动",
            "相对 Git 的差异",
            "不把它算成本任务减少的职责、代码或依赖",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

        for fragment in (
            "固定审计来源、内容身份和逻辑所有者的聚合定义",
            "脏工作树以审计当时的实际文件为基线",
            "旧基线失效",
            "区分审计快照到当前状态、本任务实际改动和相对 Git 的差异",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_facade_and_composition_root_migrations_preserve_contract_identity(
        self,
    ) -> None:
        for fragment in (
            "成员与协作者迁移账本",
            "旧方法、属性、信号、事件、回调、导出或构造参数",
            "必须保持同一实例的协作者及其身份约束",
            "消费者继续导入同一个根类型，却仍调用旧成员",
            "只搜索旧类型名、文件名或导入不能发现这类残留",
            "对象身份不变量",
            "不能根据其它调用点常见的局部变量名补造依赖",
            "来源缺失或身份关系不清楚的调用点必须单独迁移",
            "每种不同的调用点形态实际构造或运行",
            "动态绑定、通配导入、反射或跨语言绑定会削弱静态分析",
            "成员残留与身份检查用于证明接口迁移完成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

        for fragment in (
            "逐成员记录旧方法、属性、信号和跨语言绑定的最终所有者",
            "必须共享同一实例",
            "不会根据其它调用点常见的局部变量名补造依赖",
            "实际运行不同调用形态并核对协作者身份",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_protocol_surfaces_have_liveness_and_one_semantic_contract(
        self,
    ) -> None:
        ordered = (
            "事件或字段，包括线名称、类型和版本",
            "唯一语义所有者",
            "稳定操作身份与代次",
            "正式生产者",
            "传输或存储边界",
            "生产消费者及其用户可观察结果",
            "权威事实 / 必要投影 / 有明确消费者与保留期的诊断信息 / 死表面",
            "保留、统一或退出决定",
            "真实链验证和旧标识残留证据",
        )
        positions = [ARCHITECTURE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能单独证明一个运行时事件或字段有存活价值",
            "必要投影只能从权威事实生成",
            "同一个字段名称、类型、操作身份和版本含义",
            "两个字段互为别名",
            "新旧消费者各读一种名称",
            "退出旧字段、旧事件、旧别名、旧默认值和旧恢复分支",
            "不能由消费者测试手写 payload",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

        for public_behavior in (
            "事件、DTO 和公共字段会逐项建立存活账本",
            "只有测试或说明文档引用不能证明运行时表面值得保留",
            "同一语义在整个生命周期只保留一个名称和合同",
        ):
            with self.subTest(public_behavior=public_behavior):
                self.assertIn(public_behavior, README_TEXT)

    def test_async_workflows_close_by_stage_without_central_redispatch(
        self,
    ) -> None:
        ordered = (
            "阶段所有者校验输入并生成类型化命令",
            "任务边界持久化命令并交给对应执行器",
            "执行器只负责外部、平台或计算操作并产生类型化结果",
            "同一阶段所有者消费正式结果并提交领域状态",
            "展示投影从已提交状态生成可观察结果",
            "当前界面消费该投影",
        )
        positions = [ARCHITECTURE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "新增一个阶段需要同时修改启动任务的中央分支",
            "只包含一个简单异步调用",
            "组合根只装配阶段所有者、执行器、存储和投影",
            "通用分派器只按稳定类型找到所有者",
            "计算字段、展示字段和调度元数据不能混入",
            "新增一个阶段不应再修改多个中央业务分支",
            "架构守卫应阻止中央协调器重新出现阶段逻辑",
            "直接构造结果或让界面读取手写状态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

        for fragment in (
            "按阶段恢复职责闭环",
            "执行器只负责平台或计算操作",
            "让它经过正式序列化与存储、执行器、类型化结果、阶段结果应用和当前界面",
            "阻止中央业务分支、宽控制器和旧 facade 回归",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_prior_audit_findings_must_close_before_all_fixed_claim(self) -> None:
        for fragment in (
            "此前诊断或审计的“全部问题”或“上述问题”",
            "原诊断结论成为本轮结项合同",
            "已解决 / 经新证据重新分类 / 经用户明确同意退出范围 / 受阻",
            "仍然开放或证据未知",
            "不得宣告“全部问题已经解决”",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "稳定发现身份",
            "迁移顺序由唯一真源和依赖图决定",
            "不能为了让后续阶段暂时运行而留下内部兼容层",
            "最终所有者被活动消费者使用",
            "完整回归和真实用户链证明行为保持，不能替代结构收口",
            "原始发现逐项对应",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

        self.assertIn("不会让未结项的结构发现自动消失", README_TEXT)
        self.assertIn("不会宣称全部问题已经解决", README_TEXT)

    def test_comprehensive_audit_emits_a_remediation_handoff_ledger(self) -> None:
        ordered = (
            "综合审计必须交付修复交接账本",
            "稳定发现编号与简短标题",
            "根因及当前唯一责任边界",
            "受影响的生产者、传输或存储边界、正式消费者与用户结果",
            "逐项完成条件及必须取得的生产、边界、消费和可观察证据",
            "本地工作树、本地提交、实时远端、发布制品或其它适用证据平面的独立状态",
            "当前状态：开放 / 待确认 / 经新证据重新分类 / 经用户明确同意退出范围 / 受阻 / 已解决",
        )
        positions = [PROJECT_AUDIT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能把某一平面的完成折叠成整个发现已经解决",
            "不能替代该发现列出的逐项完成证据",
            "仍有开放或待确认项时不得宣称",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        for fragment in (
            "全面审计本身会输出可由后续普通修复任务直接消费的交接账本",
            "未更新的远端平面自动消失",
            "不会宣称全部问题已经解决、可合并或可发布",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_external_workspace_writers_are_gated_before_state_changes(
        self,
    ) -> None:
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

    def test_delegated_shared_worktree_writes_require_handoff_and_reverification(
        self,
    ) -> None:
        for fragment in (
            "把写任务委派给共享同一工作区的 Agent",
            "准确用户结果、允许修改的根与文件、禁止重叠的所有者",
            "实际变更、证据、未验证承诺、仍在运行的进程和残留",
            "未验证的部分交付",
            "重新清点实际变化和内容身份",
            "受影响检查的新鲜退出证据",
            "并发期间被观察到的中间状态不是产品失败证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("写入者结束却没有交接的改动", README_TEXT)
        self.assertIn("并发期间的半迁移状态不会被当作产品缺陷", README_TEXT)

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
            "文档、示例、schema、公共导出、验证与发布脚本、真实用户链工具和生成物来源也属于正式消费者",
            "审计实际暂存索引",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_mutation_receipts_are_not_final_state_evidence(self) -> None:
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
                self.assertIn(fragment, PREVENTION_TEXT + REMEDIATION_TEXT)

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

    def test_completion_requires_unique_collected_test_identities(self) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "预期关键测试身份",
            "测试框架实际收集的唯一身份",
            "缺失或非唯一身份",
            "未覆盖",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, shared)

        for fragment in (
            "测试收集身份",
            "正式发现或收集入口",
            "后定义覆盖前定义",
            "命名不符合发现规则",
            "参数化或生成身份碰撞",
            "测试源码存在、命令成功或总数看似合理",
            "先修复测试收集边界并重新收集、运行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "测试框架实际收集的唯一身份",
            "检查同名覆盖、发现命名、过滤、排除和生成身份碰撞",
            "缺失、重复或未执行的关键测试继续按未覆盖处理",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_activity_test_sources_match_unittest_collection(self) -> None:
        tests_root = SKILL_ROOT / "tests"
        expected: set[str] = set()
        shadowed: list[str] = []

        for path in sorted(tests_root.glob("test_*.py")):
            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )
            scopes = [(path.stem, tree.body)]
            scopes.extend(
                (f"{path.stem}.{node.name}", node.body)
                for node in tree.body
                if isinstance(node, ast.ClassDef)
            )
            for scope, body in scopes:
                seen: dict[str, int] = {}
                for node in body:
                    if not isinstance(
                        node,
                        (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                    ):
                        continue
                    previous = seen.get(node.name)
                    if previous is not None:
                        shadowed.append(
                            f"{scope}.{node.name}: lines {previous}, {node.lineno}"
                        )
                    else:
                        seen[node.name] = node.lineno

                    if isinstance(
                        node,
                        (ast.FunctionDef, ast.AsyncFunctionDef),
                    ) and node.name.startswith("test"):
                        expected.add(f"{scope}.{node.name}")

        def collected_ids(suite: unittest.TestSuite) -> list[str]:
            identities: list[str] = []
            for item in suite:
                if isinstance(item, unittest.TestSuite):
                    identities.extend(collected_ids(item))
                else:
                    identities.append(item.id())
            return identities

        collected = collected_ids(
            unittest.defaultTestLoader.discover(str(tests_root))
        )
        self.assertEqual(shadowed, [])
        self.assertEqual(len(collected), len(set(collected)))
        self.assertSetEqual(set(collected), expected)

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

        self.assertIn("不会直接推断同一个文件、分支、进程或任务", README_TEXT)

    def test_public_verifiers_must_execute_their_representative_path(
        self,
    ) -> None:
        for fragment in (
            "公开验证器必须实际进入保证链",
            "验证脚本、性能检查和真实用户链工具本身也是审计对象",
            "代表性输入真正执行",
            "lint 或成功导入只能证明脚本能够被解析",
            "保证链自身的缺陷",
            "明确把它标为人工且当前未覆盖",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        self.assertIn("验证与发布脚本、真实用户链工具", PREVENTION_TEXT)
        self.assertIn("公开验证器本身是否真的执行了代表性输入", README_TEXT)
        self.assertIn("语法检查、成功导入、帮助输出和脚本存在", README_TEXT)

    def test_public_validator_timeout_covers_required_child_and_cleanup(
        self,
    ) -> None:
        for fragment in (
            "公开包装器本身也是正式消费者",
            "必须实际执行",
            "必需子检查的实际稳定时长",
            "启动、报告落盘、关闭和清理余量",
            "子检查已经打印通过",
            "整条公开验证链仍是失败或待确认",
            "不靠任意放大掩盖挂起",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        self.assertIn("子检查已经显示通过但包装器超时", README_TEXT)

    def test_high_cardinality_ui_limits_consumer_fanout_and_stale_writes(
        self,
    ) -> None:
        for fragment in (
            "代表性规模、消费者扩散与编辑状态",
            "首个稳定画面、选择、编辑并持久化",
            "实际实例化的界面对象数",
            "尚未可见或尚未访问的面板、预览器和嵌入运行时",
            "不拿一个小夹具证明高基数路径",
            "首次访问的加载与错误反馈",
            "无参数的“某处变化”通知不能授权所有消费者重建全部投影",
            "草稿绑定到正式对象身份与基线版本",
            "只提交相对于当前权威状态的脏字段补丁",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "代表性对象规模、首屏 / 活动对象数与关键操作耗时",
            "打开到首个稳定画面、选择、编辑并持久化",
            "应用启动、第一次访问、离开后再次访问和关闭",
            "后台已经写入的其它字段保持不变",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        for public_behavior in (
            "一次通知引发的重算",
            "尚未访问的昂贵消费者不会默认随应用启动",
            "表单只提交脏字段",
        ):
            with self.subTest(public_behavior=public_behavior):
                self.assertIn(public_behavior, README_TEXT)

    def test_committed_state_reaches_the_current_live_projection(self) -> None:
        ordered = (
            "唯一提交边界、聚合身份与提交版本",
            "提交成功后发布的语义事件",
            "打开中的编辑器、缓存聚合与派生视图怎样共享、协调、失效或重载",
            "界面绑定实际订阅的框架可观察属性、模型信号或事件",
            "无需关闭、重开或手工刷新即可观察的最终结果",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "普通方法，只证明重新调用时返回正确",
            "空集合到首项、首项到更多项以及移除末项",
            "没有活动缓存、动态投影或多个变更入口的普通单入口状态修改不增加这份合同",
            "保持同一编辑器或界面打开",
            "立即完成一次依赖新状态的后续编辑",
            "快照必须携带读取时的聚合身份、基线版本或等价顺序边界",
            "较晚返回的旧快照只能更新它负责的基线分区",
            "无损缓存增量并在快照提交后重放",
            "用受控屏障暂停正式快照生产者",
            "最终同时包含基线内容和实时增量",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "权威状态正确但活动界面仍旧",
            "提交版本正确而没有事件",
            "事件正确但活动缓存仍是旧版本",
            "普通查询方法此刻能返回新值",
            "全局刷新、关闭重开、切换页面、固定延时",
            "**活动投影**",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "动态状态必须在不重开界面的情况下进入活动投影",
            "空集合 → 第一项 → 更多项 → 移除末项后重新为空",
            "界面更新后立即执行一次依赖新对象或新关系的后续编辑",
            "重新打开后状态正确只证明持久化",
            "动态状态与活动投影",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        for fragment in (
            "普通查询方法能够读到新值，不代表界面会自动重新求值",
            "存储写入成功，也不代表打开中的编辑器已经更新",
            "较晚返回的旧快照只能更新自己的基线分区",
            "不能整表替换掉已经显示的新状态",
            "不用关闭重开、手工刷新或固定延时冒充活动投影成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_verification_coverage_is_bound_to_real_build_targets(self) -> None:
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

    def test_desktop_blocking_work_preserves_event_loop_and_result_identity(
        self,
    ) -> None:
        for fragment in (
            "界面线程与后台工作",
            "文件遍历、复制与大文件读写、网络和 provider 调用",
            "只有用代表性数据测得明确上界",
            "不能用开发机上“通常很快”",
            "操作身份、generation、输入内容身份、目标对象",
            "取消发生在任务开始前时不能创建工作目录",
            "不能触碰其它任务或用户已有文件",
            "框架规定只能由界面线程创建、转换或释放",
            "不 mock 掉正在验证的慢生产者",
            "在后台任务终态之前已经被事件循环处理",
            "正常完成、被新 generation 替代、取消以及关闭目标",
            "只断言工作线程已创建、处理器很快返回",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        for fragment in (
            "外部 CLI 是否允许配置完整命令字符串或原始 argv",
            "界面事件处理器是否同步执行随输入增长的文件、网络、provider、媒体、进程或序列化工作",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        for fragment in (
            "事件处理器不会同步承担随输入增长的文件遍历与复制",
            "在任务完成前证明事件循环已经处理另一项无冲突操作",
            "覆盖完成、替代、取消和关闭排空",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_desktop_runtime_smoke_enumerates_lazy_surfaces_and_uses_fresh_process(
        self,
    ) -> None:
        for fragment in (
            "运行时表面清单与新鲜进程",
            "主窗口、其它主要窗口、首次访问才创建的页面或面板",
            "逐项首次打开、关闭或离开、再次进入",
            "`ReferenceError`、未定义组件、属性、信号、主题或翻译",
            "即使进程最终退出码为零",
            "`QApplication` 或等价应用单例、单实例锁、事件循环",
            "经过同一个生产 `main` 入口",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        self.assertIn("桌面 smoke 会先列出主窗口", README_TEXT)
        self.assertIn("测试套件残留的全局状态", README_TEXT)

    def test_desktop_visual_materials_are_adopted_only_when_runtime_fit_is_proven(
        self,
    ) -> None:
        for fragment in (
            "先把结构、信息层级和互动机制与视觉表面分开",
            "不是“更现代”的默认皮肤",
            "实际任务密度、背景变化、目标 Windows 合成能力、QML 渲染路径",
            "高密度编辑器、长时间阅读区、参数面板",
            "稳定不透明表面",
            "目标硬件的真实 Windows 合成与 QML 渲染链",
            "稳定不透明回退",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        self.assertIn("不会被直接当成 Windows/QML 应用的默认风格", README_TEXT)
        self.assertIn("高密度编辑工作区默认保持稳定不透明", README_TEXT)

    def test_desktop_validation_separates_offscreen_and_native_windows_evidence(
        self,
    ) -> None:
        for fragment in (
            "离屏或 headless 环境用于验证组件能够创建",
            "窗口管理器、系统标题栏、最大化与最小化",
            "DPI 与多显示器迁移、系统背景材质或 Windows 合成器行为",
            "真实 Windows 桌面会话和实际窗口",
            "不修改产品来迁就测试驱动",
            "两层分别建立证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        self.assertIn("分开离屏或 headless 与真实 Windows 会话", README_TEXT)
        self.assertIn("隔离实机检查", README_TEXT)

    def test_native_runtime_supply_and_process_isolation_are_governed(
        self,
    ) -> None:
        for fragment in (
            "原生依赖供应、ABI 与进程隔离",
            "源码存在不能证明目标平台存在可用的构建 SDK 和运行时二进制",
            "插件目录只包含插件",
            "进程级环境变量、DLL 搜索路径、插件搜索路径、全局工厂和注册表",
            "加载 → 打开 → 主界面消费真实数据",
            "后续导出或其它原生消费者继续完成用户结果",
            "重复创建和销毁",
            "用户明确要求不打包",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

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
                    LEARNING_TEXT + PREVENTION_TEXT + REMEDIATION_TEXT,
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

    def test_direct_manipulation_previews_then_commits_once_and_is_discoverable(
        self,
    ) -> None:
        ordered = (
            "按下时从正式生产者读取并冻结本次操作的持久基线",
            "当前正式消费者直接渲染这份预览",
            "释放时把最终值通过既有公共编辑边界提交一次",
            "取消、失去捕获或目标失效时恢复按下时的持久基线",
        )
        positions = [INTERACTION_MOTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不逐次写入持久化、历史或撤销栈",
            "不得建立第二套时钟、坐标映射、状态机或恢复逻辑",
            "真实指针取得至少一个中间画面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "新引入或提升为主操作的控件",
            "目标视口的自然初始任务路径",
            "实际滚动视口矩形以及两者的相交区域",
            "`visible = true`",
            "实际视口的截图或录屏",
            "先前相关的功能结果和截图同时失效",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_direct_manipulation_separates_selection_relation_and_cohort(
        self,
    ) -> None:
        for fragment in (
            "选择集合、持久关联、本次操作集合和操作入口作为四个不同事实",
            "选择本身不能让已解除的关联继续进入本次操作",
            "从任一等价成员发起都必须得到同一对象集合和成对目标映射",
            "一次原子发布",
            "空白或无目标区域点击",
            "父级滚动或手势容器实际参与命中竞争",
            "直接调用控制器、拖动 helper 或提交函数只能证明内部计算",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "直接操作按入口矩阵验收",
            "从每个合同内等价入口使用真实指针、键盘或触摸",
            "父级滚动、手势或拖拽容器保持活动",
            "直接调用内部处理器、控制器方法、拖动 helper 或提交函数",
            "不能让选中高亮成为角色身份的唯一载体",
            "选择集合、持久关联、本次操作集合、父级容器命中竞争",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("解除关联后选择状态不能让旧关系继续生效", README_TEXT)
        self.assertIn("不能只靠选中高亮表达", README_TEXT)

    def test_drag_create_preview_and_commit_share_one_placement_proposal(
        self,
    ) -> None:
        ordered = (
            "原始指针与拖拽热点",
            "对象锚点",
            "上下文放置不变量",
            "未锁定时的邻近吸附",
            "冲突与兼容性解析",
            "预期位置、目标容器、决策原因和目标状态版本",
        )
        positions = [INTERACTION_MOTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "所有预览与提交共同调用唯一放置决策边界",
            "命中即锁定，例如空目标首项必须落在原点或中心",
            "临时拖影、落点指示、读数和提示文字只消费这份放置方案",
            "不能显示原始指针位置却提交另一位置",
            "不能在界面和提交层分别实现一套放置规则",
            "释放时通过同一公共放置边界重新核对",
            "真实来源对象和真实指针",
            "远离普通吸附阈值但会触发上下文规则的位置",
            "目标非空或上下文规则不成立的分支",
            "原有自由放置与邻近吸附行为仍成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

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

    def test_visual_evidence_is_opened_and_reviewed_at_target_scale(
        self,
    ) -> None:
        for fragment in (
            "实际打开、解码并在目标显示比例下查看",
            "文件存在、路径可读、数量正确、尺寸符合或捕获命令成功",
            "信息层级、内容密度、裁切、对比度、焦点与状态表达",
            "可见结论保持未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("不会停在“截图文件已经生成”", README_TEXT)
        self.assertIn("没有看到目标画面时，视觉结论保持未知", README_TEXT)

    def test_editable_visual_deliverables_and_scene_graph_transforms_are_governed(
        self,
    ) -> None:
        for fragment in (
            "最终可交付产物合同",
            "既有可编辑基线",
            "中间参考物",
            "不能因为生成成功或看起来接近就替代最终交付物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "层级可视对象变换合同",
            "父级或挂载点",
            "局部坐标系与轴向",
            "基础位置、旋转与缩放",
            "动画增量",
            "不能同时保留世界坐标硬编码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "空间对象按视角与状态矩阵验收",
            "关键摄像机或观察方向",
            "姿态、交互与动画状态",
            "结构身份和最终画面不能互相代替",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("可视层级、变换或动效所有权", MAIN_TEXT)
        self.assertIn("中间参考", README_TEXT)
        self.assertIn("不能替代最终可编辑交付物", README_TEXT)
        self.assertIn("运行时变换链和最终画面", README_TEXT)

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
            "把它视为过程透明度证据",
            "不是增加无意义播报",
            "不能用“流程需要”掩盖范围扩张",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("不会用“还在处理”反复占位", README_TEXT)

    def test_technical_migration_does_not_authorize_visual_redesign(self) -> None:
        for fragment in (
            "不能把“迁移后更容易维护”和“迁移后应该换一种设计”合并成一个结果",
            "技术迁移与呈现变化分开授权",
            "实现迁移合同",
            "呈现保护合同",
            "设计改造入口",
            "保护区不能借改版被替换",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

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
            "为用户可见承诺建立证据覆盖表",
            "必须经过的实际分支",
            "当前状态和允许交付措辞",
            "不能证明默认启动器确实打开了网页",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("承诺覆盖", REMEDIATION_TEXT)
        self.assertIn("不会用一条成功链代替整个交付", README_TEXT)
    def test_confirmed_plan_is_revalidated_against_current_targets(self) -> None:
        for fragment in (
            "用户确认后、开始写入前",
            "与方案快照比较",
            "行为合同、影响文件、直接消费者、验证方法或用户可见结果",
            "重新确认",
            "非冲突变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        self.assertIn("确认只覆盖用户看到的那份方案", README_TEXT)

    def test_task_replacement_preserves_partial_delivery_state(self) -> None:
        for text in (LEARNING_TEXT, README_TEXT):
            for fragment in (
                "新的独立请求",
                "已经写入但尚未完成验证",
                "已经成立的证据",
                "尚未验证的",
            ):
                with self.subTest(fragment=fragment, text=text[:20]):
                    self.assertIn(fragment, text)

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

    def test_structured_json_has_one_strict_boundary_and_direct_routes(
        self,
    ) -> None:
        prevention_route = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理",
            1,
        )[0]
        remediation_route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        for route in (prevention_route, remediation_route):
            self.assertIn("references/structured-data-boundary.md", route)

        for fragment in (
            "唯一结构化入口",
            "按原始字节计算的最大输入",
            "最大嵌套深度",
            "重复键在映射覆盖前直接拒绝",
            "拒绝 `NaN`、正负无穷",
            "限制数字 token 长度、整数位数和指数",
            "目标类型范围转换",
            "类型化结果或结构化错误",
            "维护脚本不能因为“只给开发者使用”而复制生产合同",
            "原始解析、重复限制、第二套错误映射、宽松回退和旧 helper",
            "正常样例由正式生产者产生",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, STRUCTURED_DATA_TEXT)

        self.assertIn("外部、持久化、模型和进程 JSON", README_TEXT)
        self.assertIn("生产代码、迁移器、验证器和维护脚本", README_TEXT)

    def test_model_operations_preserve_wire_inputs_runtime_truth_and_consumers(
        self,
    ) -> None:
        prevention_route = MAIN_TEXT.split("## 改动前预防", 1)[1].split(
            "## 根因治理",
            1,
        )[0]
        remediation_route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        for route in (prevention_route, remediation_route):
            self.assertIn(
                "references/model-mediated-operation-governance.md",
                route,
            )

        for fragment in (
            "普通提示词创作、语气润色和一次性内容生成不进入本方法",
            "只有真实的新用户输入才能新增当前用户消息",
            "运行时事件",
            "不能冒充一条新的 `user` 消息",
            "任务原始约束",
            "最终线请求",
            "provider 适配器完成默认值、角色折叠、历史裁剪和请求序列化",
            "路由专属输出示例",
            "`response_format`",
            "任务生命周期所有者已经提交的状态",
            "模型生成一句完成式文案不能反向推进状态",
            "由宿主确定性展示的元数据",
            "不能为了修补某个消费者的重复内容",
            "推理内容合理不能证明正式回答存在",
            "不新增用户消息、不重新接受任务",
            "实际请求构造和 provider 序列化",
            "记录线协议的本地测试端点",
            "接收阶段正式产物尚不存在",
            "完成事件出现时，正式产物已经由生产者生成",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MODEL_OPERATION_TEXT)

        self.assertIn("structured-data-boundary.md", MODEL_OPERATION_TEXT)
        self.assertIn("task-progress-governance.md", MODEL_OPERATION_TEXT)
        self.assertIn(
            "模型请求语义",
            STRUCTURED_DATA_TEXT,
        )
        for fragment in (
            "真正发送到 provider 的线请求",
            "强制 route、schema、输出示例和 `response_format`",
            "模型不能用一句完成式文案推进状态",
            "接收阶段证明产物尚未完成",
            "结果阶段证明产物已经可用",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_full_record_and_bounded_model_context_have_distinct_owners(
        self,
    ) -> None:
        for fragment in (
            "完整记录与模型上下文是两个边界",
            "完整持久记录、界面查看投影、模型上下文组装结果和 provider 最终线请求",
            "不能因为模型窗口有限就先截断持久记录",
            "上下文组装策略与输入预算",
            "近期原始回合、可追溯的连续性摘要和相关召回",
            "每项上下文片段的来源身份、原始角色、顺序、覆盖范围与版本",
            "摘要必须保留来源或覆盖范围",
            "界面滚动、跳转、搜索或筛选默认只改变查看位置",
            "裁剪、摘要、召回或组装失败",
            "不能删除、覆盖或重新解释完整记录",
            "正式记录生产者提交超过单次输入预算的有序记录",
            "不能手写已经裁剪好的 context pack",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MODEL_OPERATION_TEXT)

        for fragment in (
            "长期记录可以完整保存",
            "界面查看位置、上下文组装策略和 provider 最终线请求",
            "不会暗中裁剪下一次模型输入",
            "不会删除、覆盖或重新解释完整记录",
            "provider 实际只收到符合预算的可追溯投影",
        ):
            with self.subTest(readme_fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_editable_settings_prove_real_capability_to_runtime_effect(self) -> None:
        for fragment in (
            "可编辑设置必须连到真实能力和运行结果",
            "稳定设置身份",
            "能力、设备或 provider 真源",
            "当前运行时应用或重建",
            "重启恢复",
            "显示名称只用于呈现",
            "首次运行向导与正式设置页消费同一能力目录",
            "从正常设置入口读取真实能力列表",
            "没有办法证明最终消费者使用该值",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "从真实能力到最终消费者的效用账本",
            "没有消费者的字段不会继续伪装成可用设置",
            "首次向导和日常设置会复用同一能力目录",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_model_call_graph_is_minimal_and_executor_context_isolated(
        self,
    ) -> None:
        for fragment in (
            "先冻结模型调用图，再决定是否拆分",
            "由一次类型化响应共同返回",
            "不能靠给同一轮换上 `chat`、`recall`、`repair`",
            "中间没有外部执行、人工授权、已提交运行时状态",
            "确定性执行资格先于模型路由",
            "本轮允许出现的 route 集合",
            "不调用模型判断一个不可能采用的任务 route",
            "只决定哪些能力当前可用",
            "任务生命周期所有者正式接受并登记任务后",
            "关键词捷径留作第二套隐形判断",
            "生产对话上下文与执行任务上下文分开",
            "失败回复、反例清单、历史纠正原文和离线评分规则留在评测材料中",
            "结构化 `task brief`",
            "角色性格、关系培养、表达风格",
            "不会进入 CLI 或其它任务执行器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MODEL_OPERATION_TEXT)

        self.assertIn("由一次类型化响应返回", README_TEXT)
        self.assertIn("CLI 只收到目标、相关上下文、约束", README_TEXT)
        self.assertIn("执行 route 被当前产品模式禁用时", README_TEXT)
        self.assertIn("任务正式登记后才能向用户表达", README_TEXT)

    def test_memory_evidence_roles_and_profiles_are_not_duplicate_truths(
        self,
    ) -> None:
        for fragment in (
            "长期记忆写入前还要按记忆类别建立证据资格",
            "用户事实、偏好与经历",
            "角色自身特质与习惯",
            "双方实际互动、纠正、冲突、和解与共同经历",
            "运行时已提交事件、真实产物和正式验收",
            "角色回复可以证明角色当时怎样表达或选择，不能据此新增用户事实",
            "用户评价可以成为关系事件，不能直接改写角色特质",
            "是从仍有效的原子记忆确定性派生的视图",
            "阈值由产品合同和真实评测决定",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

        self.assertIn("旧回复或一次讨好被写成永久事实", README_TEXT)

    def test_semantic_memory_curation_batches_and_restart_recovery_share_one_cursor(
        self,
    ) -> None:
        for fragment in (
            "记忆整理批次与恢复",
            "对话写入和记忆整理是两个提交边界",
            "关键词命中不能代替跨轮语义判断",
            "任务状态、CLI 输出、测试日志和系统诊断",
            "字符数和 token 上限只负责输入预算",
            "具体门槛属于项目配置和真实成本评测",
            "正常调度只接收达到业务批量门槛的完整批次",
            "启动恢复必须检查持久游标后的全部积压",
            "先原子提交全部记忆变更与必要索引，再推进最后处理游标",
            "失败、解析失败、证据失效、部分写入或关闭中断都不能推进游标",
            "稳定批次身份",
            "真实请求构造与 provider serializer",
            "直接替换 provider、手写整理结果或只检查存储文件不能证明完整链路",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

        for reference in (
            "model-mediated-operation-governance.md",
            "structured-data-boundary.md",
            "durable-operation-governance.md",
            "hard-to-reproduce-diagnostics.md",
            "runtime-generation-governance.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, LOG_TEXT)

        for fragment in (
            "对话会先独立提交",
            "重启则从持久游标补齐全部积压",
            "失败保留原游标",
            "真实 provider 序列化、解析、存储、重启、检索和记忆界面",
            "不会固化成 Project Steward 的通用数字",
        ):
            with self.subTest(readme_fragment=fragment):
                self.assertIn(fragment, README_TEXT)

        self.assertNotIn("20 轮", LOG_TEXT)

    def test_recovery_actions_join_or_reject_duplicate_attempts(self) -> None:
        for fragment in (
            "稳定的动作身份、当前执行批次或 generation",
            "加入同一活动尝试",
            "在同一原子边界被确定性拒绝",
            "不得启动第二个恢复生产者",
            "取消请求必须携带恢复动作身份和目标 generation",
            "只允许取消匹配且仍在运行的尝试",
            "不能取消、回滚或覆盖已经完成的替代结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DURABLE_OPERATION_TEXT)

        self.assertIn("重复点击、多个窗口触发或消息重放", README_TEXT)
        self.assertIn("旧界面或超时回调留下的取消不能影响新尝试", README_TEXT)

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

    def test_migrations_preflight_identities_before_expensive_full_regression(
        self,
    ) -> None:
        for fragment in (
            "迁移先预检，再进入昂贵全量回归",
            "在第一次昂贵全量测试前",
            "硬编码旧版本或旧操作身份",
            "模型或列表角色",
            "国际化生成输出",
            "测试框架实际收集的唯一身份",
            "架构或静态预算",
            "合同、迁移器、生成链和直接消费者",
            "冻结相关代码、配置和测试驱动",
            "只有影响全局、触及其它消费者，或项目规则明确要求时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("第一次昂贵全量回归前先预检", README_TEXT)
        self.assertIn("只有影响全局或项目规则要求时", README_TEXT)

    def test_diagnostic_alternatives_do_not_complete_the_normal_entry(self) -> None:
        for fragment in (
            "手工复制产物、跳过正式任务",
            "只让该条件对应的旧失败证据失效",
            "重新运行同一个正常入口",
            "实际选择目标分支",
            "不能把较早替代分支的产物拼接成正常入口通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HARD_DIAGNOSTIC_TEXT + PREVENTION_TEXT)

        for fragment in (
            "手工复制生产物、跳过正式构建任务",
            "从新鲜状态重新运行同一个正常入口",
            "不会把较早替代路径的成功拼成标准入口已经恢复",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

        ordered = (
            "建立从父入口到正式消费者的多层工具链执行闭包",
            "逐层记录实际可执行文件与版本",
            "工具在当前终端能够单独运行",
            "与正式入口相同的启动器和交接语义",
            "每次只改变一个能够排除竞争解释的变量",
            "最早出现身份或语义偏离的边界取证",
        )
        positions = [HARD_DIAGNOSTIC_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "不能把替代路径留下的产物与新运行拼成一次通过",
            HARD_DIAGNOSTIC_TEXT,
        )

    def test_canonical_path_budget_assigns_the_root_to_the_file_producer(
        self,
    ) -> None:
        for fragment in (
            "规范化真实路径预算与工程根所有权",
            "共同链中最窄的已证明预算",
            "工程根由持续创建和维护工程状态的系统拥有",
            "公开创建 API 接受逻辑名称和必要业务选项",
            "源素材可以留在生产者原目录",
            "不计入预算收益",
            "接近限制和超过限制三类输入",
            "不扩张成工程根迁移",
            "不会改变正式消费者的最深真实路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "当前路径确实超过预算是直接原因",
            "保护规则在共同消费者不能保证更长路径时是合法边界",
            "最早架构根因是工程根所有权错误",
            "公开创建入口接受逻辑名称与必要业务选项",
            "移除调用者注入物理根、深层项目内嵌、临时复制与回写同步、路径别名回退",
            "不能只提高阈值、启用系统长路径或放宽保护",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "不是新分区",
            "不进入项目的路径预算收益",
            "清理不能只依赖创建命令中的 `finally`",
            "别名已经消失、真实目标仍存在",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        self.assertIn("会继续生成工程状态、缓存、恢复文件或导出层级的系统", README_TEXT)
        self.assertIn("不会用分区工具处理 `SUBST`", README_TEXT)

    def test_large_content_roots_consume_the_user_environment_policy(self) -> None:
        for fragment in (
            "大型应用内容、项目、媒体和生成文件",
            "resolve-storage --category media",
            "大型内容根的正式消费入口",
            "不接管项目内部目录结构",
            "没有记录可用根、系统盘身份未知或所有候选失效时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        for fragment in (
            "大型内容默认根先消费用户环境策略",
            "resolve-storage --category <application-content|project|media|generated-output>",
            "默认配置、初始化器、CLI、桌面入口、后台任务和测试 fixture",
            "所有后续调用点消费该项目路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_parent_and_child_builds_share_a_target_effective_identity(self) -> None:
        ordered = (
            "跨启动器构建先统一目标有效身份",
            "源码与锁定依赖的内容身份",
            "目标三元组",
            "构建 profile",
            "feature 集",
            "目标实际选择的编译器、链接器、归档器、平台 SDK 或 API",
            "父入口、包装器和实际构建子进程分别记录规范化后的身份清单",
            "目标名称相同、输出目录相同、缓存已经存在",
            "后续子进程选择同一目标有效身份",
            "正式消费者读取与该身份绑定的同一产物内容",
        )
        positions = [USER_ENVIRONMENT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "在再次启动昂贵构建前定位第一个分歧的交接边界",
            "同一身份已复用 / 不同身份独立构建 / 状态未知",
            "项目专属值继续由项目配置或本轮执行合同保存",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, USER_ENVIRONMENT_TEXT)

        for fragment in (
            "目标名称相同或缓存存在不是复用证据",
            "后续子进程选择同一身份并让最终消费者读取对应产物才是",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, README_TEXT)

    def test_product_successor_identity_separates_public_and_technical_names(
        self,
    ) -> None:
        for fragment in (
            "产品升级先核对公开身份",
            "当前公开产品名称",
            "稳定技术标识",
            "旧公开名称",
            "全部面向用户的活动消费者",
            "不能为了让所有字符串相同而破坏兼容身份",
            "真实界面、公开 CLI 或其它正式入口显示当前名称",
            "不触发公开产品身份迁移",
            "继续按相应公共合同、协议或数据迁移边界治理",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "公开身份迁移不完整",
            "旧名称只允许留在明确标为历史的非活动材料",
            "不能把公开更名扩大成破坏兼容性的全面字符串替换",
            "至少一个真实界面、CLI 或公开能力入口显示当前名称",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        self.assertIn("产品升级或更名则分开治理", README_TEXT)
        self.assertIn("旧名称可以留在明确的历史材料中", README_TEXT)

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
