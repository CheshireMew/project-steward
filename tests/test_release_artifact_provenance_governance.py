from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT_TEXT = (
    SKILL_ROOT / "references" / "project-audit-release-and-evidence.md"
).read_text(encoding="utf-8")
LICENSE_TEXT = (
    SKILL_ROOT / "references" / "license-governance.md"
).read_text(encoding="utf-8")
DESKTOP_TEXT = (
    SKILL_ROOT / "references" / "desktop-app-governance.md"
).read_text(encoding="utf-8")


class ReleaseArtifactProvenanceGovernanceTests(unittest.TestCase):
    def test_actual_artifact_inventory_precedes_component_and_rights_closure(self) -> None:
        section = AUDIT_TEXT.split("实际制品组件溯源账本", 1)[1].split(
            "### GitHub 仓库必须审计实际上传边界", 1
        )[0]
        ordered = (
            "打包器对当前候选生成的分析、目录表或等价成员清单",
            "最终提取或展开后的制品重新枚举实际文件",
            "逐个把实际文件、模块、原生库、插件、数据文件、runtime hook 和 bootloader",
            "拥有它的发行包、运行时、构建工具或项目组件",
            "版本、取得来源、引入路径、许可证与再分发义务",
            "发布条件失败关闭",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "应用导入、运行依赖锁、打包 spec、include/exclude 规则或人工组件表",
            "打包工具注入的启动器和运行时载荷",
            "实际成员没有唯一所有者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_build_graph_is_distinct_from_runtime_dependencies(self) -> None:
        for owner, text in (("audit", AUDIT_TEXT), ("desktop", DESKTOP_TEXT)):
            with self.subTest(owner=owner):
                self.assertIn("构建依赖锁", text)
                self.assertIn("运行依赖锁", text)
                self.assertIn("打包器", text)
                self.assertIn("hooks", text)
                self.assertIn("传递依赖", text)

    def test_license_consumer_maps_injected_members_and_fails_closed(self) -> None:
        section = LICENSE_TEXT.split("### 下载、安装与再分发分别成立", 1)[1].split(
            "## 4. 重新授权", 1
        )[0]
        for fragment in (
            "消费 `project-audit-release-and-evidence.md` 的实际制品组件溯源账本",
            "每个实际文件、模块、原生库、runtime hook、bootloader 和数据文件",
            "唯一映射到所属发行包、运行时、构建工具或项目组件",
            "构建工具注入的 bootloader、启动器和运行时载荷",
            "所有者未知或映射含糊时",
            "权利闭包失败关闭",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_no_package_authority_keeps_current_artifact_unverified(self) -> None:
        section = AUDIT_TEXT.split("用户未授权生成或打包时", 1)[1].split(
            "### GitHub 仓库必须审计实际上传边界", 1
        )[0]
        for fragment in (
            "不为了补齐账本启动打包",
            "已有制品和旧打包分析可以发现候选组件与审计缺口",
            "不能证明它们对应当前源码、配置和构建环境",
            "当前包层保持未验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


if __name__ == "__main__":
    unittest.main()
