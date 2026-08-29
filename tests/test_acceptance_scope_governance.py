from __future__ import annotations

from governance_text_fixtures import (
    PROJECT_AUDIT_TEXT,
    PROJECT_RESEARCH_TEXT,
    unittest,
)


class AcceptanceScopeGovernanceTests(unittest.TestCase):
    def test_group_approval_does_not_promote_independent_agent_extras(self) -> None:
        absorption = PROJECT_RESEARCH_TEXT.split(
            "### 完整能力吸收研究",
            1,
        )[1].split("## 6. 用人话完成解释", 1)[0]
        ordered = (
            "同一组回复内部还要先按来源和作用拆分",
            "不能与 Agent 自行补充的理想成熟度、可选风险矩阵、额外测试或未来方向共用一个接受状态",
            "只接受前文能够准确识别的用户结果或候选及其直接依赖与证明闭包",
            "只有在用户按稳定身份逐项确认，或当前项目规则、正式合同被本次变化准确触发时",
            "条目写在同一消息、标题或清单中，不是接受证据",
            "不包含所有可以设想的失败场景",
        )
        positions = [absorption.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_plan_audit_proves_authority_before_using_a_completion_gate(
        self,
    ) -> None:
        audit = PROJECT_AUDIT_TEXT.split(
            "## 实施计划符合性审计",
            1,
        )[1].split("## 0. 先建立维度覆盖账本", 1)[0]
        ordered = (
            "计划是材料容器，不自动成为要求权威",
            "先证明验收门槛适用",
            "只有用户原始要求、当前项目规则或正式合同，以及用户按稳定身份准确确认的建议",
            "不能自行升级成阻塞项",
            "都不能证明其中独立补充的条目已经被接受",
            "标为待确认，不替用户扩大解释",
            "符合性账本和完成结论立即失效",
            "要求来源角色与原始证据",
            "是否进入完成条件及理由",
        )
        positions = [audit.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for role in (
            "用户原始要求",
            "项目规则或正式合同",
            "经稳定身份准确确认的建议",
            "Agent 建议",
            "实现细节或证据",
            "已拒绝或撤回",
        ):
            with self.subTest(role=role):
                self.assertIn(role, audit)


if __name__ == "__main__":
    unittest.main()
