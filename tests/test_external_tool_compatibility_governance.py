from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


SKILL_TEXT = read("SKILL.md")
COMPATIBILITY_TEXT = read("references/external-tool-compatibility.md")


class ExternalToolCompatibilityGovernanceTests(unittest.TestCase):
    def test_external_compatibility_has_a_direct_route_and_owner(self) -> None:
        reference = SKILL_ROOT / "references" / "external-tool-compatibility.md"
        self.assertTrue(reference.is_file())
        self.assertIn("外部工具兼容性", SKILL_TEXT)
        self.assertIn("references/external-tool-compatibility.md", SKILL_TEXT)
        self.assertIn(
            "inspect external-tool compatibility",
            SKILL_TEXT,
        )
        self.assertNotIn("references/", COMPATIBILITY_TEXT)

    def test_cross_root_compound_packages_load_shared_contract_governance(
        self,
    ) -> None:
        route = SKILL_TEXT.split("## 外部工具兼容性", 1)[1].split("##", 1)[0]
        for fragment in (
            "跨项目根的公共合同、派生快照或复合交付包",
            "references/external-tool-compatibility.md",
            "references/change-prevention.md",
            "公共合同、合同采用闭包与跨根交付边界",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, route)


    def test_compatibility_claim_is_closed_and_adapter_specific(self) -> None:
        for fragment in (
            "明确支持的适配器集合",
            "不能由“其它 CLI”“OpenAI-compatible”",
            "只有具体适配器通过本方法的全部必需层",
            "不能把尚未实现和验证的具体工具写成已经兼容",
            "一个适配器通过也不能替同系列",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_evidence_matrix_covers_every_compatibility_boundary(self) -> None:
        for fragment in (
            "可执行产物",
            "能力合同",
            "调用与隔离",
            "临时输入",
            "上游线协议",
            "业务结果与生命周期",
            "正式消费与用户结果",
            "已验证 / 仅诊断 / 未验证 / 受阻",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

        ordered = (
            "可执行产物",
            "能力合同",
            "调用与隔离",
            "临时输入",
            "上游线协议",
            "业务结果与生命周期",
            "正式消费与用户结果",
        )
        matrix_start = COMPATIBILITY_TEXT.index("| 证据层 | 必须证明什么 |")
        matrix = COMPATIBILITY_TEXT[matrix_start:]
        positions = [matrix.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_installed_tool_and_test_doubles_have_distinct_proof_scope(
        self,
    ) -> None:
        for fragment in (
            "项目自己编写的假 CLI",
            "不能证明外部工具当前版本的真实行为",
            "准确安装版工具经过它的正式启动和配置入口",
            "它能证明安装版工具的线协议",
            "不自动证明真实云服务、账号策略或另一个隔离环境",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_orthogonal_evidence_is_not_rewritten_as_one_end_to_end_run(
        self,
    ) -> None:
        for fragment in (
            "正式隔离启动 → 临时输入到达受限进程",
            "准确安装版工具 → 实际上游请求被协议端点记录",
            "两条证据分别填入矩阵对应单元格",
            "仍未由任何一条经过的层保持未验证或受阻",
            "不能把两段拼写成一次实际运行过的端到端链",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_install_success_is_distinct_from_capability_readiness(self) -> None:
        for fragment in (
            "取得制品、已安装、能力就绪和连续用户链完成分开记录",
            "包管理器退出码为零",
            "代表性最小输入的真实功能冒烟",
            "安装器、设置页、能力检查器和正常运行时必须消费同一个正式路径解析器",
            "上游包元数据、示例环境或锁文件",
            "只有功能冒烟通过后",
            "不能替连续用户链背书",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_adapter_contract_owns_protocol_credentials_and_results(self) -> None:
        for fragment in (
            "每个适配器由一份正式配置或类型化描述拥有",
            "上游协议选择、结果 schema 和生命周期语义",
            "不兼容的模型、协议或版本应在外部进程启动前",
            "在真实隔离边界内已经证明可达的单一通道",
            "不能因为当前终端能读取某个环境变量",
            "退出旧协议版本、旧 provider 选择、旧提示词兜底",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_adapter_owns_the_complete_argument_vector(self) -> None:
        for fragment in (
            "启动参数由适配器完整拥有",
            "完整命令字符串和原始参数数组不属于用户配置",
            "不能在这份参数之后继续拼接自由文本",
            "不能借“高级参数”恢复第二个命令行真源",
            "重复参数、位置敏感参数、短长别名",
            "只检查安全参数“曾经出现”不能证明",
            "无法可靠计算或拒绝覆盖关系时，不启动进程",
            "设置界面、运行时调用、文档、示例和测试",
            "退出旧字段、字符串解析器、参数清洗器和兼容恢复",
            "操作系统实际收到的参数顺序",
            "用重复或后置覆盖参数证明产品会在启动前拒绝",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)


    def test_capabilities_require_enforceable_isolation_and_default_closed(
        self,
    ) -> None:
        for fragment in (
            "能力必须由可强制执行的边界支撑",
            "工作目录、提示词、授权回调、命令字符串扫描",
            "无法证明原生工作区隔离的适配器不得暴露 Shell",
            "公共构造器、协议 helper 和测试入口中都默认关闭",
            "依赖旧隐式默认的测试必须明确声明所需能力",
            "目录符号链接、联接、大小写、别名",
            "不能继续增加正则规则来猜测路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_permission_modes_and_approval_requests_use_one_formal_loop(
        self,
    ) -> None:
        for fragment in (
            "权限模式和授权请求必须形成正式闭环",
            "适配器能力目录同时拥有该工具实际支持的权限模式",
            "面向用户的名称与即时解释",
            "选择、持久化、启动和运行时事件都传递同一稳定身份",
            "执行身份、任务身份、授权请求身份、工具调用身份",
            "交互模式投影为可操作界面",
            "自动允许或拒绝模式也经过同一策略入口",
            "普通输出中的 `tool_use`、终端提示、日志文字",
            "向标准输入发送一条无身份的 `yes`",
            "只有操作系统沙箱或等价强制边界",
            "两个交错授权请求",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)


    def test_declared_executor_owns_task_interpretation_and_tool_choice(
        self,
    ) -> None:
        for fragment in (
            "任务解释与工具选择由声明的执行者拥有",
            "执行者拥有任务解释、步骤规划和工具选择",
            "不能只因自然语言中出现“删除文件”“移动目录”",
            "就先把任务改判成宿主本地操作并绕过已经选择的适配器",
            "“谁决定做什么”与“谁确认结果是真的”是两个边界",
            "宿主允许某次工具调用，只证明该调用符合当前授权",
            "宿主原生快速路径只有在产品合同事先明确",
            "不能作为外部 Agent 路线内部不可见的优化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_host_independently_verifies_external_result_claims(self) -> None:
        for fragment in (
            "结构化结果是声明，宿主拥有验收事实",
            "执行前根据用户任务和正式消费者建立验收合同",
            "存在状态、内容身份或哈希",
            "工具不能自行生成验收项再为自己作证",
            "执行前已经存在且本轮没有改变的目标不能满足",
            "预期输出还要证明变化属于本次执行身份",
            "分别谎报错误内容已经写入",
            "复用执行前已存在且未改变的输出",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_external_agent_plan_truth_is_distinct_from_host_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "任务计划、宿主阶段和追加要求必须分别陈述",
            "执行者任务计划",
            "宿主执行生命周期",
            "追加要求或 steer 请求",
            "宿主验收事实",
            "带稳定任务身份和版本的机器可读计划",
            "正式的接受、拒绝或修订合同",
            "不能称为任务特定计划",
            "只能证明要求已经提交给准确任务",
            "不能证明执行者已经生成、接受或持久化修订后的计划",
            "把该验收子项标为受阻或重新分类",
            "重新取得确认",
            "只有追加要求入口、没有计划合同的适配器",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_tool_event_ledger_preserves_failures_and_explicit_recovery(
        self,
    ) -> None:
        for fragment in (
            "为每次工具调用分配稳定调用身份",
            "请求、授权或拒绝、工具结果、错误以及后续恢复关系",
            "都不能抹去未配对、被拒绝或失败后仍未解决的工具调用",
            "明确关联被替代的失败尝试",
            "仍由宿主逐项验证全部必需结果谓词",
            "在已经证明恢复后不单独强迫最终任务失败",
            "未恢复的顶层成功声明",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)

    def test_all_required_acceptance_predicates_are_evaluated(self) -> None:
        for fragment in (
            "为每个必需谓词分配稳定身份、对象身份、谓词类型和证据来源",
            "全部必需谓词必须逐项求值并共同成立",
            "代码提前返回，都不能跳过剩余必需谓词",
            "任何必需谓词没有被求值时",
            "预期对象身份与结果谓词分开建模",
            "不自动把谓词解释为“路径必须存在”",
            "删除则要求准确对象不存在",
            "正确谓词是对象不存在而不是统一要求路径存在",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, COMPATIBILITY_TEXT)



if __name__ == "__main__":
    unittest.main()
