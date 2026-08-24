from __future__ import annotations

from governance_text_fixtures import MAIN_TEXT, PRODUCT_EXPERIENCE_TEXT, unittest


class ProductStateTruthGovernanceTests(unittest.TestCase):
    @staticmethod
    def state_contracts() -> str:
        return PRODUCT_EXPERIENCE_TEXT.split(
            "### 首次使用的数据身份与信任边界",
            1,
        )[1].split("## 4. 建立完整界面合同", 1)[0]

    def test_first_use_sample_data_never_silently_becomes_user_truth(self) -> None:
        section = self.state_contracts()
        ordered = (
            "尚未创建的用户状态、示例或演示数据、模板候选",
            "稳定来源身份、当前所有者、持久化资格和允许驱动的用户结果",
            "明确标注的演示模式、隔离命名空间或用户主动选择的模板采用流程",
            "不得静默写入用户权威存储",
            "余额、合计、告警、推荐、导出或真实业务行动",
            "真实空状态、可见的进入与退出、示例身份提示",
            "新鲜配置、空存储或新账号",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_derived_presentations_define_and_explain_data_eligibility(self) -> None:
        section = self.state_contracts()
        ordered = (
            "数据集合非空不等于趋势、比较、排名、图表或摘要已经具备表达资格",
            "最低有效输入、时间跨度、可比较对象、聚合条件",
            "数据合法但尚未达到资格时",
            "它不是加载、失败或真正的空状态",
            "不得留下没有解释的空白容器",
            "零数据、低于阈值、刚好达到阈值、超过阈值、数据撤回后再次不足和正式生产失败",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "内容、空、数据不足、加载、成功、失败、冲突和恢复",
            PRODUCT_EXPERIENCE_TEXT,
        )

    def test_product_experience_route_keeps_one_method_owner(self) -> None:
        route = MAIN_TEXT.split("## 改动前预防", 1)[1].split("## 根因治理", 1)[0]
        self.assertIn("references/product-experience-governance.md", route)
        self.assertNotIn("首次使用的数据身份与信任边界", MAIN_TEXT)
        self.assertEqual(
            1,
            PRODUCT_EXPERIENCE_TEXT.count("### 首次使用的数据身份与信任边界"),
        )
        self.assertEqual(
            1,
            PRODUCT_EXPERIENCE_TEXT.count("### 派生呈现先定义数据资格"),
        )


if __name__ == "__main__":
    unittest.main()
