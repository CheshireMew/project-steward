from __future__ import annotations

from governance_text_fixtures import *


class BoundaryAndVerificationGovernanceTests(unittest.TestCase):
    def assertContains(self, text: str, fragments: tuple[str, ...]) -> None:
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

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
            "算法名称与版本",
            "叶载荷使用原始字节还是叶摘要",
            "固定测试向量",
            "双方都使用 SHA-256",
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

    def test_compound_packages_close_contract_adoption_and_output_chain(
        self,
    ) -> None:
        for fragment in (
            "复合交付包先证明合同与采用闭包",
            "顶层清单、伴随 schema、素材或资源账本、运行时接口",
            "这些节点及其引用关系形成的闭包",
            "可用性声明与正式采用关系必须分开",
            "资源进入账本只证明它可被发现",
            "消费者再把这项采用编译成自己的执行计划",
            "对可见、可听或可使用结果作出可辨认贡献",
            "消费者自行迁移或手写的样例只证明消费者内部链路",
            "只使依赖这些身份的证据失效",
            "不能把变化前后的局部通过拼成一个完整兼容结论",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_compound_packages_verify_every_integrity_layer_before_commit(
        self,
    ) -> None:
        for fragment in (
            "文件与传输层",
            "结构合同层",
            "领域语义层",
            "引用谱系层",
            "状态提交层",
            "目标项目的唯一规范投影或领域构造器",
            "不能信任清单自报的哈希、行数或身份",
            "保持文件格式和必需元数据合法",
            "重新计算全部外层文件哈希与传输清单",
            "目标正式状态仍与验证前相同",
            "没有独立领域语义身份时停在它实际拥有的层",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

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


    def test_self_evolution_does_not_mirror_internal_rules_into_readme(self) -> None:
        for fragment in (
            "公开 README 不是每项内部能力的默认消费者",
            "也不是自我进化日志",
            "只有项目公开身份、第一采用读者、主要入口",
            "不能用 README 原文断言证明内部能力已经迁移",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

        readme_route = MAIN_TEXT.split("## README 与主页", 1)[1].split(
            "## 许可证治理",
            1,
        )[0]
        self.assertIn("references/readme-delivery.md", readme_route)
        self.assertIn("README 不作为每项内部治理规则", readme_route)

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
            "无法完整保留时停止写入、重新规划",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, MAIN_TEXT)

        for method_detail in (
            "观察到的现象或结果",
            "每层分别记录证据",
            "自我进化同时治理全部活动文本体积",
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

    def test_default_prompt_is_a_bounded_research_entry(self) -> None:
        prompt_line = next(
            line
            for line in AGENT_TEXT.splitlines()
            if line.strip().startswith("default_prompt:")
        )
        prompt = prompt_line.split(":", 1)[1].strip().strip('"')
        self.assertLessEqual(len(prompt), 140)
        for fragment in (
            "$project-steward",
            "研究我提供的代码项目",
            "如果我没有说明更具体目标",
            "项目价值、最小机制闭环和证据边界后停止",
            "只有我明确要求时",
            "能力吸收、原始上游、许可证和复用关系",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, prompt)

        self.assertNotIn("完整研究这个开源代码项目", prompt)
        self.assertNotIn("确认后实施", prompt)
        self.assertNotIn("自我进化", prompt)
        self.assertLess(
            prompt.index("如果我没有说明更具体目标"),
            prompt.index("只有我明确要求时"),
        )

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

    def test_desktop_remote_configuration_failures_require_the_affected_machine_chain(
        self,
    ) -> None:
        for fragment in (
            "桌面客户端远程配置获取失败",
            "发生失败的那台机器",
            "精确配置端点实际返回的是可消费配置",
            "当前运行的客户端二进制、版本、代理模式、回环端口和内核进程",
            "源机浏览器、另一个设备的 `curl` 或只访问同域首页的成功",
            "不把完整 URL、响应正文或令牌带入日志、命令输出和对话",
            "监听地址、监听进程身份和目标客户端实际连接的端口",
            "不能把“端口冲突”写成已确认根因",
            "源机文件哈希只证明快照内容",
            "目标机从实际启动入口确认程序加载了预期配置",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

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


    def test_prior_audit_findings_must_close_before_all_fixed_claim(self) -> None:
        for fragment in (
            "此前诊断或审计的“全部问题”或“上述问题”",
            "原诊断结论成为本轮结项合同",
            "已解决 / 经新证据重新分类 / 经用户明确同意退出范围 / 受阻",
            "仍然开放或证据未知",
            "不得宣告“全部问题已经解决”",
            "`稳定发现 ID → 最终状态 → 最后一次有效证据 → 未验证边界`",
            "分类汇总、测试总数或“均已解决”结论不能替代逐项映射",
            "显式标为未验证、受阻或开放",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

    def test_audit_derived_remediation_keeps_the_full_completion_chain(
        self,
    ) -> None:
        route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        ordered = (
            "修复先前综合审计的全部问题",
            "原交接账本仍为结项合同",
            "references/change-prevention.md",
            "末次相关修改后",
            "references/project-audit.md",
            "重建账本",
        )
        positions = [route.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "无关历史审计不扩张单点缺陷范围",
            route,
        )

        self.assertIn("原诊断结论成为本轮结项合同", REMEDIATION_TEXT)
        self.assertIn("修复后再回到本方法全新复查", PROJECT_AUDIT_TEXT)
        self.assertIn("新增写入能力先建立副作用激活图", PREVENTION_TEXT)

    def test_persisted_pass_claims_are_revalidated_after_semantic_change(
        self,
    ) -> None:
        for fragment in (
            "持久化的“已通过”“安全”“兼容”或“完成”状态属于派生结论",
            "生产者语义版本、输入身份和当前消费者",
            "当前正式验证器重新消费代表性历史产物",
            "运行时读取的是同一份当前规范化或有效结果",
            "状态保持未验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)

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


    def test_deployable_repository_scope_comes_from_a_clean_checkout(self) -> None:
        self.assertIn("用干净克隆确定仓库边界", PUBLICATION_TEXT)

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



    def test_verifier_success_requires_expected_input_coverage(self) -> None:
        self.assertContains(PREVENTION_TEXT + REMEDIATION_TEXT, (
            "预期覆盖对象及内容身份",
            "工具实际选择的输入、版本、过滤和排除项",
            "输入为空、过期或不完整",
            "未覆盖或未知",
        ))

        self.assertContains(LEARNING_TEXT, (
            "验证器成功退出也不等于已覆盖预期对象",
            "被过滤与排除规则遗漏",
        ))

        self.assertContains(PREVENTION_TEXT, (
            "每项验证还要建立输入覆盖合同",
            "允许的结论：通过 / 零发现 / 未覆盖 / 未知 / 失败",
            "不由验证器碰巧看到的内容反推",
            "首选内部表示",
            "另一条正式支持路径",
            "共同能力缺失才阻塞",
        ))


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

    def test_boundary_spies_assert_canonical_semantic_identity(self) -> None:
        for fragment in (
            "测试替身位于本次核心边界之外",
            "稳定语义身份和规范载荷",
            "规范路径、对象 ID、合同版本、generation 或结构化字段",
            "调用次数、参数数量、返回形状或“已经调用”不能证明生产者选择了正确对象",
            "不能在测试里建立第二个实现",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_framework_public_names_cross_a_semantic_namespace_contract(
        self,
    ) -> None:
        ordered = (
            "公共名称会暴露给反射、元对象、数据绑定、序列化映射或代码生成框架",
            "建立语义命名空间合同",
            "继承和 final 成员",
            "让正式应用或顶层消费者从新鲜进程装载这些公开名称",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "普通局部变量和不会离开语言作用域的内部名称不触发这份合同",
            PREVENTION_TEXT,
        )


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
        for fragment in ("只读命令入口不得激活写入", "未知参数必须明确非零退出", "不用 `--help` 试运行"):
            self.assertIn(fragment, PREVENTION_TEXT)
        self.assertIn("同时消费 `change-prevention-delivery-boundaries.md`", PROJECT_AUDIT_TEXT)

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

    def test_canvas_sampling_and_playback_have_separate_visual_evidence(
        self,
    ) -> None:
        self.assertContains(IMPLEMENTATION_TEXT, (
            "不能用任意固定像素证明内容存在",
            "产品合同明确保证该坐标始终由目标内容占据",
            "支撑区域或完整画布",
            "同一条受所有者控制的渲染与捕获边界",
            "透明或背景、内容存在、姿态或状态差异和自主连续播放",
            "不能代替运行时生命周期与连续播放证据",
            "模态遮罩、非模态提示和带行动通知",
            "卡片外的透明或布局范围不得遮住底层操作",
            "普通和窄视口",
        ))
        self.assertContains(PREVENTION_TEXT, (
            "顺序、乱序、重复和新鲜实例",
            "CSS transition",
            "不能用固定等待",
            "随机访问确定性不能替代播放体验",
        ))


    def test_high_cardinality_ui_limits_consumer_fanout_and_stale_writes(
        self,
    ) -> None:
        self.assertContains(PREVENTION_TEXT, (
            "代表性规模、消费者扩散与编辑状态",
            "首个稳定画面、选择、编辑并持久化",
            "实际实例化的界面对象数",
            "尚未可见或尚未访问的面板、预览器和嵌入运行时",
            "不拿一个小夹具证明高基数路径",
            "首次访问的加载与错误反馈",
            "不可见不等于未实例化",
            "绑定仍可能求值",
            "空选择、空集合、对象被移除以及切换过程",
            "显式条件物化或等价的加载边界",
            "普通轻量控件不为形式统一强制延迟创建",
            "显示、隐藏、再次显示和关闭",
            "无参数的“某处变化”通知不能授权所有消费者重建全部投影",
            "草稿绑定到正式对象身份与基线版本",
            "只提交相对于当前权威状态的脏字段补丁",
        ))

        self.assertContains(IMPLEMENTATION_TEXT, (
            "代表性对象规模、首屏 / 活动对象数与关键操作耗时",
            "打开到首个稳定画面、选择、编辑并持久化",
            "应用启动、第一次访问、离开后再次访问和关闭",
            "后台已经写入的其它字段保持不变",
        ))


if __name__ == "__main__":
    unittest.main()
