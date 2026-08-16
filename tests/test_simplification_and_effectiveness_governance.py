from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_ROOT = SKILL_ROOT / "references"


def read_reference(name: str) -> str:
    return (REFERENCES_ROOT / name).read_text(encoding="utf-8")


PREVENTION_TEXT = read_reference("change-prevention.md")
CAPABILITY_TEXT = read_reference("change-prevention-state-and-capability.md")
ARCHITECTURE_TEXT = read_reference("architecture-cohesion-governance.md")
EFFECTIVENESS_TEXT = read_reference("project-effectiveness-review.md")
AUDIT_TEXT = read_reference("project-audit.md")
README_DELIVERY_TEXT = read_reference("readme-delivery.md")


class SimplificationAndEffectivenessGovernanceTests(unittest.TestCase):
    def test_capability_sources_stop_only_after_the_final_contract_is_closed(self) -> None:
        ordered = (
            "项目已有责任所有者",
            "语言、运行时、数据库、浏览器或操作系统原生能力",
            "已安装依赖",
            "新依赖或自建实现",
        )
        positions = [CAPABILITY_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "最终用户结果",
            "输入输出、失败语义、生命周期、正式平台和消费者",
            "完整覆盖这份最终合同才停止查找并复用",
            "不能因代码更短、名称相近或常见场景能跑就提前结束",
            "未覆盖的准确缺口",
            "安装、版本、更新、运行和退出成本",
            "一个较低层能力足以闭合合同的正例",
            "一个表面相邻但缺少必要失败语义、生命周期或平台保证的反例",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CAPABILITY_TEXT)

    def test_overengineering_candidates_require_contract_equivalence(self) -> None:
        for fragment in (
            "只有一个正式实现和一个消费者的接口或工厂",
            "只做转发且不拥有策略、状态、失败收口或生命周期",
            "没有活动消费者的 flag、配置、扩展点和兼容分支",
            "重复语言、运行时、数据库、浏览器或操作系统原生能力",
            "与现有依赖或原生能力重叠的新依赖",
            "它们只是筛选信号",
            "必须保持的输入输出、错误、生命周期、平台与消费者合同",
            "当前层又没有独立责任或已证明消费者",
            "净删除行数不能充当等价证明",
            "诊断授权只交付发现与最终迁移方案",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ARCHITECTURE_TEXT)

    def test_bounded_simplifications_have_observable_revisit_conditions(self) -> None:
        ordered = (
            "有意简化或偏离：",
            "成立假设与适用输入：",
            "能力上限或失效边界：",
            "受影响的用户结果、失败风险和正式消费者：",
            "可观察复查触发器：",
            "决定所有者与现有真源位置：",
            "触发后的升级或退出路径：",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "实现者明知省略一个已经识别的能力、规模或边界",
            "普通实现选择不逐项登记",
            "项目原有且会被真实开发流程读取的决定真源",
            "不另建一份平行“技术债”清单",
            "不能写“以后需要时”或只靠维护者记忆",
            "没有明确升级路径时",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("有意简化的成立假设、能力上限、可观察触发器和升级路径", AUDIT_TEXT)
        self.assertIn("消费 `change-prevention.md`", AUDIT_TEXT)

    def test_agent_and_skill_trials_isolate_global_experimental_variables(self) -> None:
        for fragment in (
            "宿主运行时与版本",
            "继承的系统提示与用户规则",
            "仓库规则或 `AGENTS.md`",
            "已启用的 Skill、插件、hook、MCP 与扩展",
            "会话历史和缓存",
            "工作区内容",
            "工具与权限",
            "只注入某个候选臂的内容",
            "每个候选使用全新会话、工作区和副作用目标",
            "该轮结果失效并重跑",
            "“不加载该能力”的基线",
            "只含必要方法的紧凑提示对照",
            "实际最终差异、产物或用户结果",
            "用户结果变弱时不算胜出",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, EFFECTIVENESS_TEXT)

    def test_counterfactual_claims_and_derived_consumers_share_active_identity(self) -> None:
        for fragment in (
            "同期反事实对照",
            "只能报告当前观测事实",
            "报告名称与版本、日期、模型与参数",
            "任务集与版本、样本数、指标和聚合方式",
            "原始输入输出或内容哈希",
            "README、能力卡、命令说明、图表和发布说明",
            "新报告取代旧报告时",
            "多份过期副本彼此一致不能证明有效",
            "确定性检查证明消费者声明的身份和关键数值与当前报告相等",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, EFFECTIVENESS_TEXT)

        self.assertIn("消费 `project-effectiveness-review.md`", AUDIT_TEXT)
        self.assertIn("没有对照的当前计数不得写成节省量", AUDIT_TEXT)
        self.assertIn("只发布当前有效评测身份", README_DELIVERY_TEXT)
        self.assertIn("同步更新或撤下旧数字", README_DELIVERY_TEXT)

    def test_new_method_contracts_have_one_reference_owner(self) -> None:
        reference_texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in REFERENCES_ROOT.glob("*.md")
        }
        expected_owners = {
            "## 实现机制先按能力来源收敛": "change-prevention-state-and-capability.md",
            "### 有界简化必须留下复查条件": "change-prevention.md",
            "### 过度设计候选必须用等价合同证明": "architecture-cohesion-governance.md",
            "### Agent、Skill 与提示包装的隔离实验": "project-effectiveness-review.md",
            "## 反事实节省与评测身份": "project-effectiveness-review.md",
        }
        for heading, expected_owner in expected_owners.items():
            owners = [name for name, text in reference_texts.items() if heading in text]
            with self.subTest(heading=heading):
                self.assertEqual(owners, [expected_owner])


if __name__ == "__main__":
    unittest.main()
