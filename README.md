<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Project Steward 从项目结果中学习，在改动前预防返工，并沿根因完成治理">
</p>

<!-- readme-header:start -->

<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/project-steward/issues">反馈</a>
</p>

<p align="center">
  <a href="https://x.com/0xCheshire" title="X"><img src="https://img.shields.io/badge/X-%400xCheshire-000000?logo=x&amp;logoColor=white" alt="X：@0xCheshire"></a>
  <a href="https://t.me/CheshireBTC" title="Telegram"><img src="https://img.shields.io/badge/Telegram-CheshireBTC-26A5E4?logo=telegram&amp;logoColor=white" alt="Telegram：CheshireBTC"></a>
  <a href="https://blog.blacknico.com/" title="Blog"><img src="https://img.shields.io/badge/Blog-blog.blacknico.com-2E7D32?logo=rss&amp;logoColor=white" alt="博客：blog.blacknico.com"></a>
  <a href="https://blacknico.com/" title="Homepage"><img src="https://img.shields.io/badge/Home-blacknico.com-1F6FEB?logo=googlechrome&amp;logoColor=white" alt="个人主页：blacknico.com"></a>
</p>

<p align="center">
  <a href="https://github.com/CheshireMew/project-steward/stargazers"><img src="https://img.shields.io/github/stars/CheshireMew/project-steward?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/CheshireMew/project-steward/forks"><img src="https://img.shields.io/github/forks/CheshireMew/project-steward?style=flat" alt="GitHub Forks"></a>
  <a href="https://github.com/CheshireMew/project-steward/blob/main/LICENSE"><img src="https://img.shields.io/github/license/CheshireMew/project-steward?style=flat" alt="Repository License"></a>
</p>

<!-- readme-header:end -->

# Project Steward

**把一次项目工作里的成功、返工和纠正，变成下一次更稳的行动。**

Project Steward 是一个项目治理 Skill。它从完整项目过程提炼可复用方法，在改动前检查容易返工的边界，在缺陷发生后沿根因一次迁移生产者、边界和消费者。

它适合仓库级结果：理解项目、预防改坏、治理跨层问题、整理目录、优化 README、处理许可证与发布。单个函数或普通业务功能仍由正常开发任务负责。

> 检查、审计、诊断和复盘默认只读；只有明确要求修改、实施、自我进化或发布时，才改变对应项目。

## 它能帮你完成什么

### 从真实工作中进化

Project Steward 会把一次任务里的请求、决定、命令、等待、失败、纠正和最终结果按用户目标分组，找出已经有效的方法、最早偏离点和未来应该改变的行动。

它不会把每项内部经验继续追加到 README。内部方法由 SKILL、reference 和测试维护；README 只保留稳定的项目身份、使用入口和读者需要的边界。

### 在动手前预防返工

- 冻结目标行为、唯一真源、影响范围和停止位置。
- 一次迁移全部正式调用点，并让旧入口退出。
- 对持久操作、外部 CLI、模型调用、桌面生命周期和跨仓库合同叠加专项检查。
- 从正式生产者到最终用户结果设计验收，不用手写假数据绕过核心链。

### 问题发生后沿根因收口

- 区分用户看到的现象、直接原因、合法保护、最早可控根因、绕行和残留。
- 先保留失败证据，再迁移最终边界。
- 验证真实生产、传输或存储、消费、用户可见结果和旧路径退出。
- 对内聚、耦合、重复和上帝模块给出可实施的项目级治理结果。

### 处理项目的公共表面

Project Steward 还可以研究陌生项目、盘点目录、维护项目模板、治理产品体验与日志、记录用户执行环境，并完整处理 README、许可证、Star History 和仓库发布。

## 直接这样说

### 从一次会话中进化

~~~text
使用 $project-steward 阅读这个会话的完整过程。
按用户最终结果找出成功机制、能力缺口和根因，
先给我未来行为与影响文件，确认后再让 Project Steward 自我进化。
~~~

### 改动前先检查

~~~text
使用 $project-steward 检查这次改动。
先确定唯一真源、全部消费者、旧路径退出和真实验收，
再实施并持续做到证据充分。
~~~

### 沿根因修复

~~~text
使用 $project-steward 诊断并修复这个跨层问题。
不要在症状旁加特判，一次迁移生产者、边界和消费者，
证明旧架构已经退出。
~~~

### 看懂或治理一个仓库

~~~text
使用 $project-steward 看懂这个项目。
说明它解决什么、怎样运行、核心边界在哪里，
以及哪些能力值得复用、哪些不能直接复制。
~~~

### 优化 README

~~~text
使用 $project-steward 优化这个 README。
检查 Git 和仓库状态、正文与视觉、多语言、许可证、
Star History、链接和发布，并把真实结果完整交付。
~~~

## README 完整优化会做什么

一次完整 README 优化会检查仓库是否已经初始化、README 是否存在、项目身份与读者路径是否准确，再决定新写、重写、重组或压缩。

- 正文：删除内部方法镜像和重复说明，保留项目身份、主要结果、真实入口、第一次成功与维护导航。
- 视觉：核对 hero、图片和证据资格，并检查桌面、窄屏以及 GitHub 深浅主题。
- 首屏：按活动配置生成中文、English、日本語、文档、贡献、反馈、个人入口、Stars、Forks 与许可证。
- 许可证：已有且准确时保持；缺失时先核对授权权利和采用目标，再应用确认后的方案。
- Star History：对公开 GitHub 仓库运行真实工作流，验证输出分支、亮暗 SVG 和 README 消费端。
- 发布：已有远端且确认包含发布时，精确提交、推送并核对远端 HEAD；不会自动创建远端、改变可见性、强推或删除文件。

完整编排见 [README 完整交付方法](./references/readme-delivery.md)。

## 工作方式

~~~text
用户目标
  → 项目事实与权限边界
  → 预防 / 诊断 / 实施
  → 正式生产者与真实边界
  → 最终消费者与用户结果
  → 旧路径退出和回归
~~~

Project Steward 的主文件只负责路由。完整方法位于 [references](./references/)，确定性工具位于 [scripts](./scripts/)，项目自己的长期事实仍留在项目现有规则、代码、配置和测试中。

## 安装

~~~bash
npx skills add CheshireMew/project-steward
~~~

安装完成后，在请求中直接点名：

~~~text
使用 $project-steward 全面检查这个项目，并按风险顺序给出治理方案。
~~~

写入、运行、安装、提交和发布仍按照当前请求分别授权。Project Steward 自我进化采用两阶段确认：先展示未来行为和影响范围，确认后才修改自身。

## 仓库结构

| 位置 | 作用 |
| --- | --- |
| [SKILL.md](./SKILL.md) | 角色、主路由、权限和停止位置 |
| [references](./references/) | 各类项目治理方法的唯一所有者 |
| [scripts](./scripts/) | README、许可证、模板、目录、环境和 Star History 工具 |
| [assets](./assets/) | 许可证目录、模板、README profile 与视觉资源 |
| [tests](./tests/) | 活动路由、方法所有权、脚本和真实消费者合同 |

## 验证

运行全部活动测试：

~~~powershell
python -m unittest discover -s tests -v
~~~

审计三种语言的 README：

~~~powershell
python scripts/audit_readme.py README.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language zh-CN --branch main --navigation-target docs=SKILL.md
python scripts/audit_readme.py README.en.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language en --branch main --navigation-target docs=SKILL.md
python scripts/audit_readme.py README.ja.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language ja --branch main --navigation-target docs=SKILL.md
~~~

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history.svg">
  <img alt="Project Steward GitHub Star History" src="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history.svg">
</picture>

图表由当前仓库的 GitHub Actions 使用短期 github.token 生成并发布到独立的 star-history 分支。完整方法见 [Star History 治理](./references/github-star-history.md)。

## 许可证与第三方来源

Project Steward 的主体代码与文档采用 [Mozilla Public License 2.0](./LICENSE)。

README 内容与视觉方法的一部分改编自 [oil-oil/beautify-github-readme](https://github.com/oil-oil/beautify-github-readme)，并继续遵循其 MIT License。准确范围和完整声明见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) 与 [NOTICE](./NOTICE)。

问题和改进建议可以通过 [GitHub Issues](https://github.com/CheshireMew/project-steward/issues) 提交。
