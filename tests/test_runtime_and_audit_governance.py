from __future__ import annotations

from governance_text_fixtures import *


class RuntimeAndAuditGovernanceTests(unittest.TestCase):
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

    def test_realtime_remote_audit_requires_network_authority(self) -> None:
        section = PROJECT_AUDIT_TEXT.split(
            "### 分开本地与实时远端事实", 1
        )[1].split("写清：", 1)[0]
        ordered = (
            "当前请求已经单独授权联网",
            "网络可访问",
            "只读接口或正式客户端",
            "缺少当前请求对应的联网授权",
            "不调用托管方接口或客户端",
            "完整本地审计继续",
            "实时远端证据平面标为待确认",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_performance_audit_routes_causal_measurement_and_large_evidence(
        self,
    ) -> None:
        performance = PROJECT_AUDIT_TEXT.split(
            "## 8. 审计性能、资源与规模",
            1,
        )[1].split("## 9. 审计兼容性、安装与外部边界", 1)[0]
        for fragment in (
            "区分预热与稳态资源增长",
            "检查跨边界数据量或重复工作",
            "hard-to-reproduce-diagnostics.md",
            "阶段、竞争解释、工作放大和资源趋势的诊断合同",
            "首个大文件之前",
            "production-storage-governance.md",
            "准确根、预计体积、运行身份、保留方式和清理授权",
            "运行授权不能补造删除权限",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, performance)

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


    def test_task_replacement_preserves_partial_delivery_state(self) -> None:
        for text in (LEARNING_TEXT,):
            for fragment in (
                "新的独立请求",
                "已经写入但尚未完成验证",
                "已经成立的证据",
                "尚未验证的",
            ):
                with self.subTest(fragment=fragment, text=text[:20]):
                    self.assertIn(fragment, text)

        self.assertIn("新请求不授权继续或回退旧结果", LEARNING_TEXT)

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

    def test_relational_table_rebuild_owns_data_and_schema_closure(self) -> None:
        owner = PREVENTION_TEXT.split(
            "### 关系表重建先冻结数据与模式闭包",
            1,
        )[1].split("### 跨项目根共享合同与交付账本", 1)[0]
        ordered = (
            "数据闭包：正常行、孤儿行、可保留异常行与明确不可迁移行",
            "关系闭包：父表、子表、连接表、级联语义与迁移顺序",
            "目标模式闭包：表、列、主键、外键、唯一、检查、默认值、索引、触发器、视图、生成对象与依赖查询",
            "旧到新稳定身份映射",
            "失败、回滚、重试、幂等与关闭重开合同",
        )
        positions = [owner.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "先从旧表本身清点全部稳定行身份和模式对象",
            "不能用新外键、内连接",
            "需要保留的孤儿行",
            "旧版本正式生产者 → 正式迁移器 → 当前消费者关闭并重开",
            "用模式自省核对列、键、约束、索引、触发器、视图和依赖查询",
            "失败注入必须保留可恢复原状态",
            "重试得到同一目标身份与对象集合",
        ):
            with self.subTest(owner_fragment=fragment):
                self.assertIn(fragment, owner)

        persistence = REMEDIATION_TEXT.split(
            "## 5. 持久化和临时状态迁移",
            1,
        )[1].split("## 6. 真实验收矩阵", 1)[0]
        self.assertIn(
            "直接消费 `change-prevention.md` 的“关系表重建先冻结数据与模式闭包”唯一合同",
            persistence,
        )
        self.assertIn("只定位第一次遗漏", persistence)
        self.assertNotIn("旧到新稳定身份映射，以及每类排除行的处置证据：", persistence)
        self.assertEqual(
            1,
            PREVENTION_TEXT.count("### 关系表重建先冻结数据与模式闭包"),
        )


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

    def test_model_gates_preserve_error_precedence_and_stable_test_dispatch(
        self,
    ) -> None:
        response_gate = MODEL_OPERATION_TEXT.split(
            "## 5. 正式响应通道和恢复语义",
            1,
        )[1].split("## 6. 迁移到一条活动调用链", 1)[0]
        for fragment in (
            "冻结 route 内部的语义校验优先级",
            "引用对象是否存在及其固有类型或所有者",
            "本轮候选集或权限中的资格",
            "只返回合同中优先级最高且最具体的稳定类别、字段路径和恢复动作",
            "不能遮蔽已经成立的错误类型、对象种类或引用身份",
            "重叠无效输入矩阵",
            "一组只违反新规则，一组只违反既有规则，至少一组同时违反两者",
        ):
            with self.subTest(gate_fragment=fragment):
                self.assertIn(fragment, response_gate)

        verification = MODEL_OPERATION_TEXT.split(
            "## 7. 从实际线请求验证到用户结果",
            1,
        )[1].split("## 8. 输出与停止位置", 1)[0]
        for fragment in (
            "结构化的 request purpose、route、schema 版本、工具身份或显式调用序号",
            "不能搜索 system prompt、用户文案或示例中的自然语言短语",
            "prompt 快照只验证生产提示的内容与边界，不拥有测试分流",
            "只改提示词措辞而请求合同不变时",
            "provider 序列化后的正式字段",
            "提示词等义改写不会改变分流",
        ):
            with self.subTest(verification_fragment=fragment):
                self.assertIn(fragment, verification)

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

    def test_resource_readiness_has_one_projection_and_root_cause_route(self) -> None:
        for fragment in (
            "必需资源闭包",
            "不能越级为就绪",
            "唯一状态投影",
            "能力已满足才成功无操作",
            "未满足则明确不可用或不完整",
            "不显示空名称、零大小入口",
            "只有共同能力缺失才阻塞",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("登记、安装或选择被误报为可用", MAIN_TEXT)
        self.assertIn("第一处把弱事实提升为就绪的边界", REMEDIATION_TEXT)
        self.assertIn("空动作集合本身不能证明就绪", REMEDIATION_TEXT)


    def test_settings_have_scoped_targets_and_one_atomic_commit(self) -> None:
        for fragment in (
            "从用户点名的稳定设置身份推导准确目标集合",
            "未选中的同级路由、provider 或设备设置基线",
            "不能通过遍历全部同级项来猜测修改范围",
            "兄弟路由必须保持逐字段不变",
            "一个配置事务或一次持久提交",
            "旧的持久状态和活动状态都保持可用",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("设置或维护工具越过唯一写入边界", REMEDIATION_TEXT)

    def test_multistage_settings_separate_connection_application_and_effect(
        self,
    ) -> None:
        for fragment in (
            "阶段效用图",
            "所属决策阶段与精确效果",
            "已经接通",
            "活动运行时已经应用",
            "对用户所说的结果有效",
            "每个阶段实际读取的参数、默认值或硬编码值",
            "没有更早的门控主导输入",
            "没有更后的阶段重新产生或覆盖同一结果",
            "一个稳定身份一次迁移能力描述",
            "同一份由正式生产者取得或按正式输入合同记录的受控输入",
            "不能手写已经分类、识别或过滤完成的下游结果",
            "多阶段链路中各设置属于哪个决策阶段",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "沿全部决策阶段定位最早主导结果的参数、默认值或硬编码值",
            "在最终输出增加后置特判",
            "形成独立产品合同和验收",
        ):
            with self.subTest(remediation_fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)


    def test_realtime_sessions_wait_for_authority_and_publish_truthful_capabilities(
        self,
    ) -> None:
        for fragment in (
            "实时连接先建立权威身份与可调用状态",
            "传输已经连接与领域已经就绪的不同里程碑",
            "首次连接、重新连接与显式 reset",
            "configured、process online、endpoint reachable、callable",
            "客户端默认值、`0`、缓存身份",
            "队列清空只能消费已确认的当前身份",
            "隐藏这些活动入口",
            "旧 generation 迟到消息",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "连接已经打开但交互尚未就绪",
            "握手前清空队列",
            "哪个生产者提前发布了更强状态",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)


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


        self.assertNotIn("20 轮", LOG_TEXT)

    def test_memory_recall_and_maintenance_share_formal_domain_boundaries(
        self,
    ) -> None:
        for fragment in (
            "召回触发与维护写入边界",
            "不能以短期对话历史非空作为前置条件",
            "应用首次连接后的第一轮",
            "显式 reset 后的第一轮",
            "重新连接后的第一轮",
            "不是第二个写入者",
            "与正常整理器相同的类型化领域命令",
            "不能直接调用存储 driver、写表、改索引",
            "维护表面保持只读",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LOG_TEXT)

        self.assertIn(
            "长期记忆的首轮召回、检查器和维护写入",
            REMEDIATION_TEXT,
        )

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

    def test_project_config_and_verification_stay_portable_and_proportional(
        self,
    ) -> None:
        for fragment in (
            "机器和部署事实先进入项目运行配置边界",
            "`.env` 不是所有项目的统一答案",
            "同一个加载器、schema、校验、优先级和规范化结果",
            "本机值 fallback",
            "不含开发机配置与相邻项目的干净检出",
            "不表示使用最多的抽象、服务、缓存、兼容层",
            "已证明用户结果、失败风险或正式消费者",
            "不从实现步骤、源码行数或调用点数量反推测试数量",
            "README、许可证、致谢、仓库可见性和普通元数据修改不创建产品测试",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "仓库反复出现本机值先检查项目配置所有权",
            "最早根因是项目运行配置没有唯一所有者和消费边界",
            "只把路径移进 `.env`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        root_cause_route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        self.assertIn("硬编码本机与部署事实", root_cause_route)
        self.assertIn("references/change-prevention.md", root_cause_route)
        self.assertIn("references/user-environment-governance.md", root_cause_route)


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

    def test_implementation_plan_audit_rebuilds_a_fresh_requirement_ledger(
        self,
    ) -> None:
        for fragment in (
            "按实施计划审计完成度",
            "audit a plan or repository",
            "按实施计划逐项核对完成度",
            "诊断读取设置、运行报告、结构化制品或日志时",
        ):
            with self.subTest(main_fragment=fragment):
                self.assertIn(fragment, MAIN_TEXT)

        ordered = (
            "冻结计划内容身份、项目状态、明确排除项和证据平面",
            "每一项规范性要求、验收标准、公开方法或事件、schema 字段、平台目标",
            "稳定计划条目身份和原文定位",
            "预期关键测试身份与实际收集身份",
            "状态：已实现且已验证 / 已实现但未验证 / 缺失 / 明确排除 / 受阻",
            "从原始计划和当前已接受合同重新生成全新符合性账本",
        )
        positions = [PROJECT_AUDIT_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不能从现有源码、测试名称或已经发现的问题反推计划范围",
            "完整测试通过不能替没有映射关系的计划条目背书",
            "语义残留扫描、正式调用点退出和真实消费者证据",
            "本地代码与运行、CI、目标平台实机和外部服务分别成立",
            "不得复制上一轮的完成标记",
            "实施计划审计只覆盖计划范围",
        ):
            with self.subTest(audit_fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

        self.assertIn("治理项目变更", AGENT_TEXT)


if __name__ == "__main__":
    unittest.main()
