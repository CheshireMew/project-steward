from __future__ import annotations

from governance_text_fixtures import *


class FirstUseAndReleaseFreezeGovernanceTests(unittest.TestCase):
    def test_first_use_detects_before_consenting_to_install(self) -> None:
        ordered = (
            "只读自动检测与下载、安装、写配置",
            "完整能力已被可靠发现时直接进入核心任务",
            "只缺少部分时只提出精确修复项",
            "完全缺失时提供一次完整安装决定",
            "无法可靠判断时说明未知",
        )
        positions = [UX_DESIGN_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不得成为主路径中的手工输入",
            "预计大小、目标位置和取消结果",
            "由用户在当前产品表面明确确认",
            "用户取消时不产生安装副作用",
            "重复启动不再把首次完整诊断当作必经页面",
            "只返回到对应缺失项的修复路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, UX_DESIGN_TEXT)

    def test_downloadable_catalog_uses_one_identity_and_current_locale(self) -> None:
        for fragment in (
            "同一稳定资源身份的不同状态和投影",
            "不依靠显示名或列表位置匹配",
            "当前语言的本地化元数据",
            "回退到稳定技术名并明确标记尚未本地化",
            "目标用户、当前语言、当前产品已有目录和真实用途",
            "原行动位置直接消费正式任务进度",
            "列表不在界面中再算一份百分比",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, UX_DESIGN_TEXT)

    def test_desktop_runtime_snapshot_separates_portable_and_installed_modes(
        self,
    ) -> None:
        for fragment in (
            "便携或安装模式与组件就绪快照",
            "应用控制且实际可写的明确目录",
            "不能静默回退到开发机绝对路径",
            "可以自动发现并复用",
            "不在应用预设根就强制安装第二份",
            "不得写入可分发包、仓库默认值或新机器配置",
            "第一次完整验证成功后",
            "有界快速检查",
            "正式消费者真实启动失败",
            "不能每次启动都把首次全量诊断重演给用户",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

    def test_public_release_freezes_checks_smoke_tag_and_asset_identity(
        self,
    ) -> None:
        ordered = (
            "冻结准确提交 SHA、目标分支、版本和发布合同",
            "同一 SHA 上全部必需本地检查与远程 CI 完成并成功",
            "构建最终资产",
            "在一次性副本执行 smoke",
            "计算最终资产摘要",
            "创建指向该 SHA 的标签和 Release",
            "回读远程标签、资产摘要、默认分支与公开安装入口",
        )
        positions = [PUBLICATION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "候选分支、PR 和默认分支是三个可分别成立的远程表面",
            "不在正式资产根上直接 smoke",
            "原候选清单和内容身份没有变化",
            "不创建面向用户的正式标签、Release 或上传资产",
            "已公开标签和同名资产默认保持不变",
            "不因下载数量为零",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_cached_validator_result_must_cover_the_final_candidate(self) -> None:
        for fragment in (
            "验证器自身的结果缓存",
            "不能让过去输入上的 lint、扫描、编译或测试结果",
            "字面输入及其内容身份",
            "这次命中只证明“没有重新执行”",
            "优先关闭结果缓存",
            "已登记的空缓存根",
            "必须取得新鲜退出状态后才能继续",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)


if __name__ == "__main__":
    unittest.main()
