from __future__ import annotations

from governance_text_fixtures import *


class ConversationLearnedGovernanceTests(unittest.TestCase):
    def test_continuation_cannot_promote_a_completed_read_only_result(self) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        ordered = (
            "每个用户回合、内部轮次、自动续跑和上下文压缩恢复开始时",
            "任何工具调用或状态改变前",
            "最近一次明确用户动作",
            "尚未完成的结果、范围、权限和停止位置",
        )
        positions = [shared.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "同一结果仍未交付",
            "只读结果已经交付、没有新的明确动作",
            "审计发现、助手建议、内部计划、目标名称、待办清单和自动提示",
            "都不能补造新结果或写入权限",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, shared)


    def test_shared_boundaries_remain_on_every_project_steward_route(self) -> None:
        shared = MAIN_TEXT.split("## 共同边界", 1)[1].split(
            "## 对话学习与自我进化",
            1,
        )[0]
        for fragment in (
            "普通业务功能仍由当前开发任务负责",
            "联网、下载、安装、运行、生成、写入、移动、归档、删除、提交、推送和发布分别授权",
            "任何工具调用或状态改变前",
            "工作从短动作扩展为多阶段",
            "新的独立请求替换尚未完成的结果",
            "逐项保留输出、错误和退出状态",
            "Shell 后句可能遮蔽前序失败时先进入“用户环境档案与执行环境”",
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

        learning_route = MAIN_TEXT.split(
            "## 对话学习与自我进化", 1
        )[1].split("## 改动前预防", 1)[0]
        for fragment in (
            "方法缺失",
            "已有方法没有被路由、执行或验收",
            "只修最早失效的主路由、动作门槛、正式消费者或验证",
            "不在其它文件增加同义规则",
            "方案按所有者和消费链组织",
        ):
            with self.subTest(route_fragment=fragment):
                self.assertIn(fragment, learning_route)

    def test_self_evolution_maps_consumption_before_adding_capability(self) -> None:
        consumption = LEARNING_TEXT.split(
            "再为每项候选画出一条活动消费链", 1
        )[1].split("模板只接收某类项目", 1)[0]
        ordered = (
            "用户最终结果与语义触发",
            "主路径",
            "固定必读方法所有者",
            "有适用证据才叠加的条件专项",
            "动作门槛",
            "正式消费者与输出",
            "验收和停止位置",
        )
        positions = [consumption.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "方法完整，但主路径没有固定加载",
            "路由已经加载，但动作绕过方法",
            "正式消费者或验收没有覆盖",
            "同一机制只能有一个方法所有者",
            "没有正式消费者、没有主路由入口",
            "复杂度结算：新增 / 原位强化 / 合并 / 退出 / 保持不变",
            "不能再用全局 `assertIn` 代替路由位置和消费关系",
        ):
            with self.subTest(ownership_fragment=fragment):
                self.assertIn(fragment, consumption + LEARNING_TEXT.split(
                    "写入方案和最终差异按所有者组织", 1
                )[1].split("### 自我进化同时治理主文件体积", 1)[0])

        self.assertEqual(
            1,
            LEARNING_TEXT.count("同一机制只能有一个方法所有者"),
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

    def test_baseline_correction_is_not_reported_as_scope_expansion(self) -> None:
        section = LEARNING_TEXT.split(
            "用户在原结果尚未完成时补充",
            1,
        )[1].split("警告、等待和超时必须恢复", 1)[0]
        ordered = (
            "基线纠正",
            "同一结果增项",
            "独立新结果",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "已经存在但先前误读的产品身份、环境事实、限制或目标",
            "不是新增范围",
            "相关返工归入假设或基线调查不足",
            "不得把基线纠正造成的返工归因于用户扩项",
            "不得把独立结果藏进原结果的实现时间",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

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
            "职能边界",
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

    def test_comprehensive_audit_covers_every_applicable_project_dimension(
        self,
    ) -> None:
        coverage_fragments = (
            "先建立维度覆盖账本",
            "不能从已经发现的问题反推审查范围",
            "产品定位与用户结果",
            "功能与缺陷",
            "代码质量",
            "架构、内聚与重复",
            "数据、持久化与生命周期",
            "界面视觉",
            "交互与完整用户旅程",
            "无障碍、键盘与国际化",
            "性能、资源与规模",
            "兼容性与环境",
            "构建、测试与 CI",
            "安装、升级与发布",
            "日志与诊断",
            "文档、示例与许可证",
            "外部集成、隐私与安全边界",
            "覆盖状态：已审查 / 部分审查 / 未审查 / 不适用",
            "验证深度：静态审查 / 既有运行证据 / 本机目标验证 / 待运行验证",
            "缺少全量测试、远端 CI 或非本机平台运行本身不会",
            "覆盖账本、问题账本和验证深度是三个结果",
        )
        for fragment in coverage_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        coverage = PROJECT_AUDIT_TEXT.index("## 0. 先建立维度覆盖账本")
        findings = PROJECT_AUDIT_TEXT.index("综合审计必须交付修复交接账本")
        self.assertLess(coverage, findings)
        self.assertNotIn("做轻量健康检查", PROJECT_AUDIT_TEXT)

        audit_route = MAIN_TEXT.split("## 项目综合审计", 1)[1].split(
            "## 平台模板资源",
            1,
        )[0]
        for fragment in (
            "全部适用维度的覆盖账本",
            "不得只根据已经发现的问题回填审查范围",
        ):
            with self.subTest(route_fragment=fragment):
                self.assertIn(fragment, audit_route)

    def test_active_development_audit_does_not_run_release_candidate_gates(
        self,
    ) -> None:
        for fragment in (
            "项目阶段：活跃开发 / 集成冻结 / 发布候选 / 已发布维护",
            "“全面”修饰审查维度",
            "测试不是覆盖维度的计数器",
            "当前机器上最小的目标检查",
            "全量覆盖率、完整端到端与视觉或性能矩阵、打包、签名、发布、远端 CI 和非本机平台",
            "不为填满审计账本运行",
            "不把“没跑全量测试”改写成“没有全面审查”",
            "不把这些入口组成一份必须在综合审计中全部执行的命令清单",
            "全面审查可以在盘点全部适用入口并分析其保证关系后完成本维度覆盖",
            "选中的最小目标验证器",
            "不为证明检查过它而代替 CI 运行全部入口",
            "不能把整份审计账本自动变成实施范围",
            "默认只在当前机器实际运行验证",
            "不会自动启动跨平台矩阵",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

    def test_ambiguous_followup_cannot_expand_audit_into_all_fixes(
        self,
    ) -> None:
        section = PROJECT_AUDIT_TEXT.split(
            "综合审计同时存在两个以上开放发现时",
            1,
        )[1].split("## 实施计划符合性审计", 1)[0]
        ordered = (
            "不等于修复全部",
            "展示开放发现的稳定身份、结论、依赖关系和预计影响",
            "让用户明确选择",
            "在选择成立前保持只读",
            "只包含冻结问题账本中已经确认且仍开放的发现",
            "不包含改进建议、未来成熟度方向、非问题、证据未知项",
            "新的独立问题必须单独登记",
            "重新取得范围与写入确认",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for ambiguous_request in ("“修复”", "“继续”", "“开始吧”", "“处理一下”"):
            with self.subTest(ambiguous_request=ambiguous_request):
                self.assertIn(ambiguous_request, section)
        self.assertIn("不能借原来的“全部”持续扩张实现", section)


    def test_comprehensive_ui_audit_uses_surface_and_journey_inventories(
        self,
    ) -> None:
        ui_section = PROJECT_AUDIT_TEXT.split(
            "## 7. 审计用户界面与完整体验",
            1,
        )[1].split("## 8. 审计性能、资源与规模", 1)[0]
        for fragment in (
            "product-experience-governance.md",
            "ux-design.md",
            "interface-experience-quality.md",
            "implementation-review.md",
            "后端、CLI 和库项目不检查不存在的 GUI",
            "仍审计各自真实入口的可发现性、反馈、错误理解和完整用户旅程",
            "全部窗口、页面、延迟面板、菜单、对话框、覆盖层",
            "逐项绑定到顶层窗口创建者",
            "外壳证据身份",
            "只有 `content-only` 截图",
            "界面维度最多标为部分审查",
            "不能由其它窗口或测试代为背书",
            "从首次启动到核心结果建立用户旅程清单",
            "初始、空、加载、进行中、成功、失败、禁用、离线、取消和恢复状态",
            "鼠标、触摸、键盘、快捷键和焦点顺序",
            "截图必须实际打开并按目标显示比例检查",
            "审查覆盖仍可完成",
            "视觉高级感、真实交互和运行状态只能标为待运行验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ui_section)

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

    def test_emphasis_preserves_full_result_coverage_and_additive_closure(
        self,
    ) -> None:
        for fragment in (
            "先区分范围词和优先级词",
            "“尤其”“重点”“特别关注”只改变检查顺序",
            "只有“只”“仅”“排除”“不要看”等明确收窄表达",
            "每项结果都必须进入这份覆盖账本",
            "现有能力已完整覆盖 / 现有能力未被消费 / 值得吸收的新缺口 / 项目事实 / 不持久化",
            "新增验收项进入同一闭环账本",
            "全部仍有效请求重新生成完成清单",
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


    def test_real_producer_assertions_follow_identity_and_fact_category(
        self,
    ) -> None:
        for text in (PREVENTION_TEXT, REMEDIATION_TEXT):
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

    def test_native_model_and_host_capabilities_are_not_reimplemented(self) -> None:
        ordered = (
            "先排除模型与宿主已经拥有的职责",
            "当前原生边界已经能完成同一用户结果时",
            "结论是**不吸收**",
            "只有当前原生能力无法表达一项已经证明必要的持久项目合同",
        )
        positions = [LEARNING_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "上下文选择、方案比较、步骤规划和工具选择",
            "工具协议、Agent 编排、任务连续性和产品适配",
            "业务事实、稳定身份、schema、权限、原子写入与恢复",
            "第二套编排器、集成注册表、扩展市场、持久工作流",
            "模型偶尔犯错",
            "都不能单独证明需要新的持久机制",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)


if __name__ == "__main__":
    unittest.main()
