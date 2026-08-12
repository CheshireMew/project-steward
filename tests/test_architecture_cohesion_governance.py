from __future__ import annotations

import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_ROOT = SKILL_ROOT / "references"
ARCHITECTURE_TEXT = (REFERENCES_ROOT / "architecture-cohesion-governance.md").read_text(
    encoding="utf-8"
)


class ArchitectureCohesionGovernanceTests(unittest.TestCase):
    def test_read_only_verbs_are_a_hard_project_write_boundary(self) -> None:
        self.assertIn("按照主路由已经选定的模式执行", ARCHITECTURE_TEXT)
        self.assertIn("本方法不重新解释用户措辞", ARCHITECTURE_TEXT)
        self.assertNotIn("用户只说检查、审计、诊断", ARCHITECTURE_TEXT)

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

    def test_public_surface_liveness_is_not_inferred_from_repository_references(
        self,
    ) -> None:
        for fragment in (
            "仓内调用点为零只能作为有界内部符号的退出证据",
            "HTTP、WebSocket、IPC、CLI、插件入口、框架注册、公共导出",
            "机器可读发现或 schema",
            "版本与发布承诺",
            "已知外部消费者",
            "只能标为未知或受阻",
            "不能因仓内搜索无命中就删除、改名或宣告原功能已经迁移",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_architecture_residue_scans_close_semantic_invariants(self) -> None:
        for fragment in (
            "同一问题类型、关键词、目录位置或代码形态",
            "最早错误事实、最终所有者",
            "受影响的生产者到消费者链",
            "只记录为独立问题并停在原授权边界",
            "语义闭合条件",
            "禁止存在的所有权或依赖方向",
            "允许存在的最终边界",
            "自然语言误报或范围外独立问题",
            "零匹配只有在扫描器成功覆盖预期输入",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_architecture_guards_separate_rules_from_target_inputs(self) -> None:
        for fragment in (
            "规则定义控制面与被检查的活动对象分开",
            "活动源码、脚本、验证器和公共合同等目标根",
            "规则定义中的哨兵文本不能被当成活动调用",
            "不能为了消除自命中而排除整个测试目录或脚本目录",
            "区分声明文本与活动语义的结构化扫描",
            "用另一个表面不同的代表性目标注入同类残留",
            "准确语义单元和语言作用域",
            "模块顶层绑定、类型成员、函数局部变量、导入、调用或字符串绑定",
            "一个真实违规夹具和一个文本相近但语义合法的夹具成对验证",
            "不会漏报",
            "不会误报",
            "与实际目标根使用同一解析和选择路径",
            "对应边界保持未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_adapter_families_separate_shared_policy_from_source_variants(
        self,
    ) -> None:
        section = ARCHITECTURE_TEXT.split(
            "### 适配器族先拆开共同政策与合法变体",
            1,
        )[1].split("### 测试专用影子实现不算生产覆盖", 1)[0]
        ordered = (
            "重复实现族与正式入口",
            "共同业务政策及顺序",
            "只有适配器知道的来源事实",
            "会改变生命周期或失败语义的真实例外",
            "最终族级所有者、窄适配器接口和正式消费者",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不在“全部合并”和“全部复制”之间二选一",
            "由一个族级流程、策略或组合所有者维护",
            "适配器接口只返回来源事实或执行平台专用动作",
            "标准适配器不得通过覆写重新复制",
            "输入职责、生命周期或失败语义不同",
            "不要为了复用建立只有一层转发的基类",
            "分别运行一个标准适配器和每类真实例外",
            "新增来源无需复制共同流程",
            "架构门禁阻止标准适配器重新覆写不变量",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_migration_test_failures_stay_bound_to_findings_and_target_behavior(
        self,
    ) -> None:
        for fragment in (
            "逐项映射到稳定发现身份和已冻结的目标行为基线",
            "同一测试文件、套件或目录不能证明多个失败属于同一迁移边界",
            "生产者、合同、边界或消费者的迁移确实改变了该断言或夹具",
            "无关断言、并发改动或目标仍未知的失败",
            "不能用脏工作树当前显示的文字",
            "反向改写目标行为",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

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

    def test_prior_audit_findings_close_architecture_contract(self) -> None:
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

    def test_repository_ownership_is_not_inferred_from_sql_location(self) -> None:
        ordered = (
            "repository 与公共接口",
            "拥有的聚合、稳定身份和写入不变量",
            "直接读写的表、集合、文件或索引",
            "明确拥有的只读投影及其一致性语义",
            "事务、重启恢复、批处理和释放生命周期",
            "允许和禁止的跨聚合依赖",
        )
        positions = [ARCHITECTURE_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "只证明物理位置改变，不证明领域已经解耦",
            "隐藏查询另一个聚合并据此决定其领域规则",
            "不能把自身 `.repository`",
            "窄公共接口、注入的 resolver、明确命名的查询服务或应用服务",
            "不能为了消除依赖而丢掉合法语义",
            "显式只读投影可以组合多个聚合或表",
            "不成为任何聚合的第二业务真源",
            "不能按“一张表一个 repository”机械判断",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_test_only_shadow_implementation_is_not_production_coverage(
        self,
    ) -> None:
        for fragment in (
            "测试专用影子实现不算生产覆盖",
            "生产入口实际到达的实现",
            "测试入口实际到达的实现",
            "只被测试、样例或验证器引用的实现",
            "测试数据构造器",
            "生产入口与测试共同消费正式唯一所有者",
            "从生产公共入口或其真实上游到达该所有者",
            "退出影子 helper",
            "残留检查同时比较生产引用集合和测试引用集合",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_first_party_operation_entries_share_binding_and_request_finalizer(
        self,
    ) -> None:
        ordered = (
            "稳定操作身份",
            "同步或长任务属性",
            "阶段或 handler 所有者",
            "请求 schema 与默认值",
            "必要的请求身份和关联信息",
            "幂等或恢复语义",
            "全部第一方入口",
        )
        section = ARCHITECTURE_TEXT.split(
            "### 多入口操作共享一份绑定与请求收口",
            1,
        )[1]
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "绑定只有一个可执行真源",
            "启动时集合相等检查",
            "同一个请求收口边界",
            "补齐和校验通用 envelope",
            "入口专用 preparer 只负责把用户输入转换为操作参数",
            "缺项、孤儿项和重复绑定立即失败",
            "至少从一个第一方简写或界面动作发起代表性操作",
            "只调用通用 execute",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_new_architecture_contracts_have_one_reference_owner(self) -> None:
        reference_texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in REFERENCES_ROOT.glob("*.md")
        }
        for heading in (
            "### 适配器族先拆开共同政策与合法变体",
            "### 测试专用影子实现不算生产覆盖",
            "### Repository 边界按聚合所有权验收",
            "### 多入口操作共享一份绑定与请求收口",
        ):
            owners = [name for name, text in reference_texts.items() if heading in text]
            with self.subTest(heading=heading):
                self.assertEqual(
                    owners,
                    ["architecture-cohesion-governance.md"],
                )


if __name__ == "__main__":
    unittest.main()
