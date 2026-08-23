from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
LICENSE_TEXT = (
    SKILL_ROOT / "references" / "license-governance.md"
).read_text(encoding="utf-8")
ROLLOUT_TEXT = (
    SKILL_ROOT / "references" / "license-rollout.md"
).read_text(encoding="utf-8")
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
AUDIT_RELEASE_TEXT = (
    SKILL_ROOT / "references" / "project-audit-release-and-evidence.md"
).read_text(encoding="utf-8")


class LicenseGovernanceTests(unittest.TestCase):
    def test_stable_defaults_do_not_require_a_license_choice_prompt(self) -> None:
        for fragment in (
            "默认 `AGPL-3.0-or-later`",
            "默认 `MPL-2.0`",
            "稳定默认本身就是已经选定的许可证",
            "不再停下来询问用户选择",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LICENSE_TEXT)

        self.assertIn("命中稳定默认时不再询问许可证", SKILL_TEXT)
        self.assertIn("无需另问一次许可证偏好", ROLLOUT_TEXT)

    def test_skill_repository_classification_uses_the_primary_product(self) -> None:
        for fragment in (
            "主产品是一个 Agent Skill 或正式的 Agent Skill 集合",
            "根目录 `SKILL.md`",
            "嵌套适配器、测试夹具、示例、vendored 或第三方 Skill 文件",
            "不会把宿主仓库改判为 Skill 仓库",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LICENSE_TEXT)

    def test_existing_rights_boundaries_override_automatic_relicensing(self) -> None:
        for fragment in (
            "内容、数据、角色、品牌和媒体",
            "已有许可证、Fork、外部贡献者或第三方冲突仍先保留现状",
            "不能把稳定默认当成静默重新授权的依据",
            "权利冲突可以阻塞实施",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LICENSE_TEXT)

    def test_audit_routes_composite_runtime_rights_to_license_governance(
        self,
    ) -> None:
        for fragment in (
            "项目有权再分发",
            "复合交付包的逐项权利闭包",
            "不能单独关闭发布授权发现",
            "`license-governance.md`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, AUDIT_RELEASE_TEXT)

    def test_acquisition_install_cache_and_redistribution_are_independent(
        self,
    ) -> None:
        section = LICENSE_TEXT.split("### 下载、安装与再分发分别成立", 1)[1].split(
            "## 4. 重新授权",
            1,
        )[0]
        for fragment in (
            "取得入口存在",
            "上游允许用户安装、项目允许缓存",
            "再分发授权",
            "不能用“官方下载”“本机已安装”或包管理器可用替代再分发依据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_composite_delivery_fails_closed_on_unknown_member_rights(
        self,
    ) -> None:
        section = LICENSE_TEXT.split("### 下载、安装与再分发分别成立", 1)[1].split(
            "## 4. 重新授权",
            1,
        )[0]
        for fragment in (
            "复合交付闭包",
            "成员身份与版本、准确上游",
            "绑定最终归档的内容身份",
            "只覆盖它实际授权的内容",
            "权利或义务仍未知时",
            "再分发资格失败关闭",
            "由用户从已验证上游自行取得",
            "把取得与再分发状态分开保存",
            "打包器和发布验证器消费同一份逐项账本",
            "不会创造许可证没有授予的权利",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


if __name__ == "__main__":
    unittest.main()
