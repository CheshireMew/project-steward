# GitHub Star History 治理

## 适用范围

用户询问 README 里的 Star History 为什么失效、以后还能不能显示、怎样替换，或要求为一个或多个 GitHub 仓库接入长期可维护的星标历史图时读取本页。

只问原因、现状或复杂度时保持只读：检查 README 当前图片来源、实际 HTTP 结果、仓库可见性、 Actions 策略、工作流是否存在和启用、最近运行结果以及输出分支，不修改仓库。用户明确要求接入、修复或替换时，才进入实施；除非用户明确要求只改本地，完成位置默认是远端图表已经生成并能被 README 消费，不是本地 YAML 和图片链接已经写完。

## 默认实现

Project Steward 仓库是唯一生成器与可复用工作流来源：

- `.github/workflows/star-history.yml` 接受其它仓库调用；
- `.github/actions/star-history/action.yml` 负责固定执行环境和参数边界；
- `scripts/github_star_history.py` 是读取、渲染和发布的唯一实现；
- 每个调用仓库只保留定时 / 手动触发器与 README 图片引用；
- 生成结果写入调用仓库的 `star-history` 分支，默认文件是 `star-history.svg` 和 `star-history-dark.svg`；
- 使用调用仓库每次运行时自动签发的 `github.token`，不建立长期个人访问令牌，也不把凭据传给第三方服务。

生成器读取 GitHub stargazers API 的带时间戳结果，确认分页结果数量与仓库权威星标数一致，随后生成确定性的亮色和暗色 SVG。两个文件通过 Git Data API 在一次提交中更新；内容未变化时不提交。图表横轴止于最后一次星标日期，因此没有新星标时定时运行也不会产生日期漂移。

## 调用仓库

在调用仓库建立 `.github/workflows/star-history.yml`：

```yaml
name: Update Star History

on:
  schedule:
    - cron: "17 3 * * 1"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    permissions:
      contents: write
    uses: CheshireMew/project-steward/.github/workflows/star-history.yml@main
```

README 使用调用仓库自己的原始文件地址：

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/OWNER/REPOSITORY/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/OWNER/REPOSITORY/star-history/star-history.svg">
  <img alt="GitHub Star History" src="https://raw.githubusercontent.com/OWNER/REPOSITORY/star-history/star-history.svg">
</picture>
```

`@main` 表示所有调用仓库共享 Project Steward 当前的稳定实现，修复不需要逐仓复制。只有调用器和图片里的 `OWNER/REPOSITORY` 属于各项目；不要复制生成脚本，也不要保留旧的第三方 Star History 图片作为回退，因为回退会让失效来源继续处于活动架构中。

## 默认完成事务

接入、修复或替换按一个连续事务完成：

1. 从准确 Git 根确认调用仓库身份、当前分支、现有 upstream、远端默认分支、GitHub CLI 登录状态以及工作流写权限；README 中的所有者和仓库名必须来自该身份。
2. 写入调用工作流和 README 后运行本地检查，建立本轮获准改动的依赖闭包。混合工作树只按文件或内容片段暂存该闭包，不使用整个工作树代替发布范围。
3. 创建只包含该闭包的提交并推送到现有 upstream。推送前重新读取远端分支，发现分叉、保护策略、认证失败或未获准依赖时停止；不创建远端、不改变可见性，也不强制推送。
4. 推送成功后手动运行一次调用仓库的工作流，并等待该次运行结束：

```powershell
gh workflow run star-history.yml --repo OWNER/REPOSITORY --ref DEFAULT_BRANCH
gh run watch --repo OWNER/REPOSITORY
```

5. 运行成功后核对 `star-history` 分支、两个 SVG、日志星标数、两个 raw 地址和 GitHub README 的明暗主题显示。再次手动运行验证 `changed=false` 时，继续观察同一个正式工作流，不以本地生成文件代替。

只有上述远端链路全部成立才报告接入完成。工作流尚未运行、输出分支尚未生成、raw 地址仍返回错误或 README 仍无法显示时，分别报告已经写入、已经提交、已经推送或远端生成受阻，不能概括成图表已经可用。

## 真实验收

实施不能停在 YAML 能解析或单元测试通过。按正式链路验证：

```text
调用仓库的定时或手动触发
→ 调用 Project Steward 可复用工作流
→ github.token 读取调用仓库 stargazers 时间戳
→ 生成器同时发布亮色和暗色 SVG
→ 调用仓库 star-history 分支保存一次原子提交
→ raw.githubusercontent.com 返回 SVG
→ README 的 picture 元素读取并展示
```

至少核对工作流运行成功、日志报告的星标数等于仓库当前星标数、输出分支同时存在两个 SVG、原始地址返回 SVG 内容，并在 GitHub README 的深浅主题入口确认图像能够显示。再次手动运行且星标未变时，还要确认生成器报告 `changed=false`，输出分支没有新增提交。

## 生命周期与故障定位

GitHub 会自动停用连续 60 天没有仓库活动的公开仓库定时工作流。图片不会因此立即消失，但会停止更新。检查时区分“输出仍存在”和“生产者仍在运行”；恢复后启用并手动触发一次：

```powershell
gh workflow enable star-history.yml --repo OWNER/REPOSITORY
gh workflow run star-history.yml --repo OWNER/REPOSITORY
```

常见故障按边界定位：

- 调用工作流无法加载：确认 Project Steward 仓库和 `main` 分支可访问，并检查调用仓库的 Actions 允许策略；
- API 返回 403：确认调用工作流明确授予 `contents: write`，组织策略没有把令牌降为只读；
- API 没有 `starred_at`：确认请求使用带时间戳的 stargazers 媒体类型，并且当前令牌可以读取仓库 Metadata；
- 数量校验失败：星标可能恰在分页期间变化，重新运行；生成器不得用不完整数据发布看似成功的图；
- 分支存在但 README 不显示：直接检查两个 raw URL、响应内容与 README 最终 `srcset`，不要用本地手写 SVG 冒充生产结果；
- 定时任务长期没有运行：检查工作流是否被 GitHub 自动停用，启用后再走一次完整链路。

本页是叶子资源；完成诊断、实施或验收后返回 `SKILL.md` 的“README 与主页”路径。
