from __future__ import annotations

import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_TEXT = (
    SKILL_ROOT / "references" / "repository-publication.md"
).read_text(encoding="utf-8")
PUBLICATION_TEXT += (
    SKILL_ROOT / "references" / "repository-publication-execution.md"
).read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT = (
    SKILL_ROOT / "references" / "project-audit.md"
).read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT += (
    SKILL_ROOT / "references" / "project-audit-release-and-evidence.md"
).read_text(encoding="utf-8")


class RepositoryPublicationGovernanceTests(unittest.TestCase):
    def test_github_repository_initialization_is_one_ordered_transaction(
        self,
    ) -> None:
        ordered = (
            "审计本地物理文件和拟上传候选",
            "才运行 `git init`",
            "只把获准清单中的准确路径或内容片段加入索引",
            "让第 3 节的必要性与隐私检查消费这份真实索引",
            "才创建首次提交",
            "才创建空远端",
            "首次推送必须另有授权",
            "推送命令成功后记录提交身份并停止",
        )
        initialization = PUBLICATION_TEXT.split(
            "## 4. 初始化 GitHub 仓库", 1
        )[1].split("## 5. 本地主页预览", 1)[0]
        positions = [initialization.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "本地 Git 初始化、首次提交、创建 GitHub 远端和首次推送仍是可分别停止的状态改变",
            "不创建嵌套 `.git`",
            "不授权安装客户端、登录账号、创建远端或改变设置",
            "禁止用 `git add -A`、`git add .` 或等价整树暂存绕过候选账本",
            "确认所有者、准确仓库名和 public、private",
            "不根据账号惯例猜可见性",
            "内容边界已通过 / 本地 Git 已初始化 / 首次提交已创建 / GitHub 空远端已创建 / 首次推送已完成 / 实时远端已验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, initialization)

    def test_upload_boundary_checks_privacy_and_unnecessary_files_on_real_surfaces(
        self,
    ) -> None:
        audit = PUBLICATION_TEXT.split(
            "## 3. 审计 GitHub 上传边界", 1
        )[1].split("## 4. 初始化 GitHub 仓库", 1)[0]
        for fragment in (
            "本地物理文件",
            "本次获准候选",
            "Git 索引",
            "本地提交与可达历史",
            "实时 GitHub",
            "Git LFS、Release 资产或 Actions 制品",
            "用正式消费者判断必要性",
            "只应留在本机的用户内容、机器配置或运行状态",
            "生产者、消费者或权利边界尚不明确的未知内容",
            "检查隐私与敏感内容",
            "首次提交前还要检查提交作者姓名与邮箱",
            "工具缺失、命令失败、历史未取得、输入为空或被默认过滤时结论是未知",
            "必须在进入终端输出、工具结果、对话、报告或日志前脱敏",
            "撤销或轮换凭据作为第一处置",
            "`.gitignore` 只影响尚未跟踪的匹配路径",
            "不创建一个随后可能被误推送的半成品远端",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, audit)

    def test_history_cleanup_separates_hygiene_sensitive_data_and_cache_layers(
        self,
    ) -> None:
        history = PUBLICATION_TEXT.split(
            "### 历史清理先冻结类别、结果层和引用平面",
            1,
        )[1].split("## 4. 初始化 GitHub 仓库", 1)[0]

        layers = (
            "第 1 层——当前工作树、索引和新提交",
            "第 2 层——获准的本地分支、标签与其它引用",
            "第 3 层——实时远端活动分支、标签和新鲜克隆",
            "第 4 层——旧提交 SHA 缓存、PR 引用、fork、其它克隆或托管方存储",
        )
        positions = [history.index(fragment) for fragment in layers]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "分别判断**上传必要性**和**内容敏感性**",
            "工具使用了 `--sensitive-data-removal` 等选项",
            "不能反向证明内容属于凭据、隐私或其它敏感数据",
            "是不同动作",
            "枚举本地引用的名称和对象类型",
            "tree 等快照引用可能继续持有目标 blob",
            "按所有者和生命周期分成仓库公开引用",
            "活动宿主或工作区的回滚引用",
            "第 2 层的本地全引用结论不成立",
            "带取得时间的瞬时快照",
            "先让创建者停止",
            "不能循环删除",
            "精确租约或等价条件更新",
            "新鲜镜像或克隆",
            "不能据此把已经完成的仓库结果改写成受阻",
            "不能要求用户提交支持工单",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, history)

        github_audit = PROJECT_AUDIT_TEXT.split(
            "### GitHub 仓库必须审计实际上传边界",
            1,
        )[1].split("### 公开验证器必须实际进入保证链", 1)[0]
        for fragment in (
            "同时记录上传必要性与内容敏感性",
            "不能把两者合并成一个严重程度判断",
            "不把未知自动升级成敏感",
            "用户已经接受的准确清理层",
            "服务器缓存或托管方工单才进入完成条件",
            "反向扩大原发现",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, github_audit)

    def test_project_audit_consumes_the_shared_github_upload_boundary_read_only(
        self,
    ) -> None:
        github_audit = PROJECT_AUDIT_TEXT.split(
            "### GitHub 仓库必须审计实际上传边界", 1
        )[1].split("### 公开验证器必须实际进入保证链", 1)[0]
        for fragment in (
            "读取 `repository-publication.md` 的“审计 GitHub 上传边界”",
            "不在这里建立第二套敏感文件或目录黑名单",
            "不会仅为取得“全面”称谓扫描全部历史、其它分支、标签、Release 资产和 Actions 制品",
            "完整上传边界、隐私或历史暴露审计只有在用户明确要求发布、公开、上传边界审计或历史清理",
            "未展开的历史平面记录为待验证",
            "本地物理文件与拟上传候选、Git 索引、当前已跟踪树、本地提交和可达历史",
            "本地 `origin/*` 也不能代替实时 GitHub 内容",
            "没有消费者证据才说明它不应进入仓库",
            "同时核对 Git 提交作者姓名与邮箱的公开暴露",
            "本维度只能标为部分审查或待确认",
            "不能报告“没有隐私文件”",
            "只读综合审计不修改 `.gitignore`、不初始化 Git、不改变索引、不创建远端，也不清理历史",
            "才可以把 GitHub 上传边界标为已审查",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, github_audit)

        coverage_contract = PROJECT_AUDIT_TEXT.split(
            "用户要求“全部问题”“所有问题”或“全面检查”", 1
        )[1].split("## 实施计划符合性审计", 1)[0]
        self.assertIn(
            "需要核对的 GitHub 上传候选、索引、历史与实时远端内容边界",
            coverage_contract,
        )

    def test_clean_checkout_result_defines_repository_contents(self) -> None:
        for fragment in (
            "用干净克隆确定仓库边界",
            "仓库承诺交付的用户结果",
            "必须跟踪的输入",
            "仓库明确承诺提供的 Skill",
            "已被 Git 跟踪、尚未跟踪、命中忽略规则",
            "当前工作区的成功拼成干净克隆成功",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_public_install_entry_is_automatically_synced_to_readmes(self) -> None:
        for fragment in (
            "自动同步公开安装入口",
            "范围不限于 Skill",
            "不能根据仓库名、目录名或惯例猜测",
            "实际安装、下载依赖或运行安装脚本仍需当前请求授权",
            "每份活动语言 README 的安装段落",
            "不重复追加",
            "标明 shell 的代码块",
            "同一次获准发布闭包",
            "在推送成功后停止",
            "不等待 GitHub 页面、Actions 或远端安装消费者刷新",
            "用户另行明确要求远端验收时",
            "不能反向重跑无关本地检查",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_concurrent_writers_cannot_be_restored_or_published_by_accident(
        self,
    ) -> None:
        for fragment in (
            "同步客户端、生成器、编辑器监视器、其它 Agent 或进程",
            "不能解释的变化不得用 `git restore` 消掉",
            "不得顺手暂存",
            "是否证明提交遗漏了正式交付物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_remote_advance_rebuilds_the_semantic_publication_candidate(
        self,
    ) -> None:
        section = PUBLICATION_TEXT.split(
            "### 远端前进后先重建发布基线",
            1,
        )[1].split("创建提交、创建远程、选择或改变可见性", 1)[0]
        ordered = (
            "取得当前跟踪目标的实时远端 HEAD",
            "旧远端到新远端的变化",
            "重叠路径",
            "权威合同",
            "唯一方法所有者",
            "全部正式消费者",
            "只有仍属于本次获准结果的消费者才进入迁移",
            "重新冻结最终候选",
            "读取完整最终差异",
            "每项检查分别保留退出状态",
            "推送前再次取得目标远端",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "Git 能自动合并或文本没有冲突",
            "不能按提交时间、`ours`、`theirs`、文件多数或自动合并结果猜权威",
            "不复制许可证、schema 或公开身份方法",
            "不因需要整合远端而扩大普通工作树的发布范围",
            "不能把整合前的暂存检查或后续成功命令当作最终候选通过",
            "目标已经变化就重新建立上述账本",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_remote_checks_are_verified_without_granting_fix_authority(
        self,
    ) -> None:
        for fragment in (
            "required checks",
            "推送或派发 required checks、GitHub Actions、部署任务后立即停止",
            "只有用户明确要求远端验收时",
            "读取状态、日志和失败产物属于只读发布验证",
            "用户另行授权时才执行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_effective_merge_policy_and_server_rewrite_are_reconciled(
        self,
    ) -> None:
        section = PUBLICATION_TEXT.split(
            "### 冻结公开发布候选、标签与资产",
            1,
        )[1].split("项目将标签、Release", 1)[0]
        ordered = (
            "冻结候选 SHA、基准分支、实际保护规则或 ruleset",
            "分支规则与实际合并响应才是权威",
            "merge commit 被拒绝时",
            "优先保留提交粒度",
            "服务端 rebase 或 squash 会生成新的提交身份",
            "重新取得 PR 状态、远端默认分支 HEAD",
            "本地默认分支已同步",
            "证明原本地独有提交仍可由来源分支、备份引用或 reflog 找回",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("无法证明时保留分叉并报告", section)
        self.assertIn("不授权修改代码、测试、工作流或远端设置", section)

    def test_self_evolution_stops_at_the_successful_push(self) -> None:
        section = PUBLICATION_TEXT.split(
            "### Project Steward 自我进化使用整仓发布合同",
            1,
        )[1].split("### 本地提交与远端状态分层交付", 1)[0]
        for fragment in (
            "推送前核对工作区没有遗漏",
            "推送命令成功后立即停止",
            "不再执行状态回读",
            "不等待 GitHub Actions 或其它远端消费者",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_commit_or_push_does_not_override_project_deletion_rules(
        self,
    ) -> None:
        for fragment in (
            "读取项目规则对删除、归档、生成物和提交的额外限制",
            "通用的“提交”“推送到 main”或“发布”不能代替删除授权",
            "在暂存、提交或推送前准确列出所有待删除路径及理由",
            "任何受项目规则约束但尚未单独获准的删除都必须在暂存前停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_publication_still_preserves_existing_scope_gates(self) -> None:
        for fragment in (
            "推送授权只覆盖核对后的准确范围",
            "不自动包含同一工作树中的无关改动",
            "不创建提交、不创建远程仓库、不推送",
            "未经授权不通过强制推送、删除远程或改可见性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_project_steward_invocation_is_not_target_project_publish_authority(
        self,
    ) -> None:
        for fragment in (
            "调用 Project Steward、允许修改目标项目或确认治理方案，都不自动授权提交和推送该目标项目",
            "普通项目只有在用户明确要求提交或推送",
            "独立专项路径已经把精确提交与推送写入其确认结果",
            "Star History 使用其叶子方法的独立展示优化合同",
            "都不能为普通目标项目补造发布权限",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

        self.assertNotIn(
            "### 明确点名 Project Steward 的实施默认推送即停止",
            PUBLICATION_TEXT,
        )

    def test_public_visibility_does_not_expand_into_release_infrastructure(
        self,
    ) -> None:
        section = PUBLICATION_TEXT.split(
            "“公开仓库”“改成 public”或“让别人能看到”",
            1,
        )[1].split(
            "如果普通项目的推送请求承接同一对话",
            1,
        )[0]
        for fragment in (
            "只授权把已经准确确认的目标远端改变为公开可见",
            "不会把本地产品升级成发布候选",
            "不自动授权推送尚未发布的工作区内容",
            "先报告并分别取得处置权限",
            "安装器或自动更新器",
            "签名、打包与 Release 工作流",
            "GitHub Pages",
            "分支保护",
            "Topics",
            "Star History",
            "README 重设计",
            "CI 改造、部署或远端运行等待",
            "准确结果单独加入本次合同",
            "不能为了让“公开”显得完整而建设一整套发布基础设施",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_project_steward_self_evolution_publishes_the_whole_worktree(self) -> None:
        section = PUBLICATION_TEXT.split(
            "### Project Steward 自我进化使用整仓发布合同",
            1,
        )[1].split("### 本地提交与远端状态分层交付", 1)[0]
        ordered = (
            "整个当前工作区是一个不可拆分的发布范围",
            "全部已跟踪修改、未跟踪文件和现有删除",
            "根据整个工作区的实际影响范围建立验证账本",
            "使用 `git add -A`",
            "创建为一个新提交",
            "只向当前跟踪分支执行非强制推送",
            "推送前核对工作区没有遗漏",
            "推送命令成功后立即停止",
        )
        positions = [section.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "不按任务、来源、文件或内容片段选择性排除",
            "保留完整工作区并停止",
            "不能遗漏该项、退回最小依赖闭包",
            "工作区没有未暂存或新出现的遗漏",
            "不再执行状态回读",
            "不拆分工作区绕过阻塞",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_local_commits_and_remote_state_are_reported_separately(self) -> None:
        for fragment in (
            "本地提交与远端状态分层交付",
            "未推送提交会从多少变为多少",
            "已有提交与新提交分别服务哪个获准结果",
            "准确提交集合",
            "工作区与索引：",
            "本地分支、本轮新增提交及各自用途：",
            "相对上游的 ahead / behind：",
            "远端分支与 HEAD 的实际核对：",
            "尚未执行或尚未验证的推送、打包、部署与远端检查：",
            "不把未等待的远端结果写成已经验证",
            "用户只授权提交时明确说明远端没有变化",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


    def test_entangled_worktree_does_not_expand_publication_authority(
        self,
    ) -> None:
        for fragment in (
            "混合工作树先求获准依赖闭包",
            "从本次获准的用户结果开始",
            "最小依赖闭包",
            "只证明它属于技术闭包",
            "不会让用户原有或来源不明的改动自动获得暂存与发布授权",
            "完整工作树一起通过测试也只能证明组合兼容",
            "立即在暂存前停止",
            "不能把整个脏工作树改称“当前整合状态”来绕过确认",
            "不能因为拆分困难就执行 `git add -A`",
            "明确授权整个工作树",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_multi_root_results_publish_each_root_independently(self) -> None:
        for fragment in (
            "跨项目根的发布状态分别成立",
            "普通目录、Git 仓库、已提交、已推送和远端已验证",
            "发布候选只属于当前获准发布的准确项目根",
            "不能自动让那个根的文件获得暂存、提交或推送授权",
            "项目根 A 已推送、项目根 B 仍是普通目录或只有本地修改",
            "必须先把准确目标根与它的候选范围对应起来",
            "正式消费者测试不能静默读取相邻项目的绝对路径",
            "不能用该测试在当前开发机通过",
            "跨项目链已通过",
            "不能把两项拼成更高层结论",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_final_candidate_evidence_follows_affected_consumers(
        self,
    ) -> None:
        for fragment in (
            "为最终候选内容建立验证账本",
            "候选身份：工作树基线、待暂存路径及内容身份",
            "正式消费者：构建器、运行时、用户界面",
            "最后一次相关变化之后",
            "可见界面、媒体或交互发生变化时",
            "类型检查或构建成功不能代替这条用户链",
            "不机械重跑无关产品回归",
            "重新核对索引中的变化事实、正式消费者和新鲜证据仍然匹配",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_git_checks_cover_untracked_candidate_files(self) -> None:
        for fragment in (
            "检查覆盖：每项检查预期读取什么",
            "已跟踪工作树差异、暂存索引、未跟踪文件和被忽略路径",
            "`git diff --check` 只能检查它实际选中的 Git 差异",
            "候选全是未跟踪文件",
            "未获暂存授权时",
            "对已批准候选路径执行等价只读检查",
            "不由工具默认排除代替",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_local_validation_failure_does_not_grant_fix_authority(self) -> None:
        for fragment in (
            "本地候选在提交或推送前验证失败时",
            "立即冻结当前发布候选",
            "不授权为了消除失败而修改源码、配置、测试、工作流或生成逻辑",
            "用户看到失败证据后另行授权",
            "不暂存、不提交、不推送",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_authorized_fix_invalidates_only_affected_validation_evidence(
        self,
    ) -> None:
        for fragment in (
            "继续消费原验证账本",
            "不把一次修复当成全部证据清零",
            "新鲜通过结果继续有效",
            "优先重跑原失败检查、受修复影响的消费者和必要用户链",
            "测试收集、共享夹具、全局配置、公共边界",
            "不能为了得到一份整齐的新日志而丢弃仍然有效的昂贵证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)

    def test_single_root_history_replacement_is_a_conditional_transaction(
        self,
    ) -> None:
        for fragment in (
            "有意重建为单一根提交",
            "普通的“提交”“推送”或含糊的“继续”不授权改写历史",
            "旧本地分支引用",
            "已观测远端分支 SHA",
            "父提交为空和提交数为 1",
            "`--force-with-lease=<branch>:<observed-sha>`",
            "远端发生变化，立即中止",
            "推送后必须重新获取远端",
            "禁止路径或应归档内容未进入新树",
            "不包含等待 GitHub Actions",
            "标为异步且未验证并停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PUBLICATION_TEXT)


if __name__ == "__main__":
    unittest.main()
