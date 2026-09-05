<!-- readme-header:start -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="160" alt="Project Steward">
</p>

<h1 align="center">Project Steward</h1>

<p align="center">
  <strong>一个帮助你研究和审计项目、预防返工、修复根因，并改善界面设计与使用体验的 Agent Skill。</strong>
</p>

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

Project Steward 是一个由兼容 Agent 使用的项目治理 Skill。把仓库、实施计划、界面问题或一次任务的完整过程交给它，可以研究项目、核对完成度、设计和优化界面、预防返工、修复跨层问题，并整理开发与发布所需的配套工作。

> 检查、审计、诊断和复盘默认只读；明确要求实施后才修改对应内容。普通业务功能和单个函数问题仍按正常开发任务处理。

## 它能帮你完成什么

### 设计、美化和改善界面体验

从零设计界面、调整视觉方向，或打磨已有产品的布局、字体、配色、信息层级、组件、交互和动效。它也能依据参考界面重建页面，统一多页面的设计系统，并处理桌面窗口、响应式布局和本地文件工作区的体验问题。

检查会结合相关页面、窗口和主要状态，找出影响美观、理解和操作的问题。获准实施后，从实际入口核对最终画面和连续操作，区分代码已修改、画面已验收和使用体验已检查。方法见[产品体验与界面治理](./references/product-experience-governance.md)。

### 看懂项目，核对计划与实际完成度

解释陌生仓库解决什么、如何运行、主要模块怎样配合；研究参考项目时，区分值得学习的方法与实际可复用的内容。对照实施计划逐项核对已完成、遗漏和未验证事项；全面审计时按项目类型检查适用范围，并给出有证据的优先级。

### 在动手前预防返工

功能、重构或迁移开始前，明确目标、依赖和受影响的调用方，安排修改顺序与验收。根据实际改动检查性能、任务进度、长时间操作、模型参与的流程和跨项目接口，提前发现会导致重复修改的问题。

### 问题发生后沿根因收口

从现象追到真正需要修改的位置，修复涉及的模块、数据和调用关系，并核对旧实现是否退出。也可以检查架构耦合、重复实现和职责过多的模块，避免同一问题在不同位置反复修补。

### 整理项目、运行环境与发布

| 工作 | 可以得到什么 | 方法 |
| --- | --- | --- |
| 目录整理 | 区分活动文件、本地状态和历史材料，提出忽略、移动或归档方案 | [目录治理](./references/repository-directory-governance.md) |
| 外部工具兼容 | 检查工具接入、官方格式和导出链，定位并修复兼容问题 | [工具兼容](./references/external-tool-compatibility.md) |
| 项目模板 | 建立、采用、升级项目基线，把反复适用的做法写进模板 | [模板](./references/project-template-system.md) · [模板演进](./references/template-evolution.md) |
| 日志与执行环境 | 让日志能追溯实际操作，核对工具、SDK、缓存和长任务的运行条件 | [日志](./references/log-audit-standard.md) · [环境](./references/user-environment-governance.md) |
| 运行产物存储 | 治理模型、下载、媒体、缓存和测试产物的存放、增长与残留 | [存储治理](./references/production-storage-governance.md) |
| README 与发布 | 整理项目介绍、主页视觉、多语言、许可证和 GitHub 发布信息 | [README](./references/readme-delivery.md) · [许可证](./references/license-governance.md) · [发布](./references/repository-publication.md) |

### 从真实工作中进化

从一次完整任务中找出有效做法、失败原因和用户纠正，提出下次应该怎样处理。确认后将可复用方法写回 Project Steward；项目自己的决定仍留在该项目的文档、代码和配置中。

## 直接这样说

在兼容 Agent 中点名 `$project-steward`，附上对应项目或材料即可。请求中的“检查”“给方案”和“实施”决定这次要做到哪一步。

| 你想做什么 | 请求示例 |
| --- | --- |
| 优化界面 | 使用 $project-steward 优化这个项目的界面和使用体验，改善布局、视觉层级、组件和交互，并检查实际画面与主要操作。 |
| 从零设计 | 使用 $project-steward 为这个产品设计界面，先给出结构和视觉方向供我选择。 |
| 重建参考界面 | 使用 $project-steward 按这个参考界面重建页面，并对照实际运行结果检查差异。 |
| 看懂或治理一个仓库 | 使用 $project-steward 看懂这个仓库，解释用途、架构和运行方式；另外评估哪些能力值得复用。 |
| 核对实施计划 | 使用 $project-steward 对照这份计划检查项目，列出已完成、漏做和仍未验证的事项。 |
| 全面审计 | 使用 $project-steward 全面检查这个项目，按用户影响和风险给出治理方案。 |
| 改动前先检查 | 使用 $project-steward 检查这次改动的影响范围、依赖和验收方式，先给实施方案。 |
| 沿根因修复 | 使用 $project-steward 诊断并修复这个问题，处理受影响的调用方，并验证实际结果。 |
| 整理目录 | 使用 $project-steward 检查哪些文件仍在使用、哪些不应上传，先给整理方案。 |
| 检查兼容性 | 使用 $project-steward 检查项目与这个外部工具或官方格式的兼容性，指出失效的位置。 |
| 建立或升级模板 | 使用 $project-steward 检查这个项目的基线，提出模板采用或升级方案。 |
| 演进模板 | 使用 $project-steward 判断这些做法是否适合作为稳定默认，并更新对应项目模板。 |
| 整理日志 | 使用 $project-steward 治理这个项目的日志，让一次操作的输入、过程、失败和结果能够查清。 |
| 核对环境 | 使用 $project-steward 检查这个项目需要的工具、SDK 和缓存位置，说明当前环境的缺口。 |
| 治理存储 | 使用 $project-steward 检查模型、媒体、缓存和测试产物的增长与残留，先给存储治理方案。 |
| 优化 README | 使用 $project-steward 优化这个 README，完整处理正文、多语言、主页信息和相关发布事项。 |
| 处理许可证 | 使用 $project-steward 检查这个仓库的许可证与第三方来源，给出适用范围和调整方案。 |
| 提交发布 | 使用 $project-steward 检查上传内容，并将确认后的改动提交、推送到现有远端。 |
| 从一次会话中进化 | 使用 $project-steward 阅读这次会话的完整过程，提出未来行为和影响文件，确认后再自我进化。 |

## README 完整优化会做什么

根据项目事实组织主要用途和使用入口，处理正文、主页视觉、多语言、导航与许可证。公开 GitHub 仓库还包含 Star History、Topics 和 About Description；Website 只使用符合条件的正式入口。

- 视觉按素材源码结构和引用关系核对，不把结构检查说成画面美观已经验收。
- Star History 实施到工作流派发后停止，生成图表和远端展示仍标为未验证；另行要求远端验收时再检查。
- 提交与推送依照已确认范围执行，推送后不等待新一轮远端检查。

完整范围和执行条件见 [README 完整交付方法](./references/readme-delivery.md)。

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

检查本页 README（其它语言使用对应页面列出的命令）：

~~~powershell
python scripts/audit_readme.py README.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language zh-CN --project-name "Project Steward" --tagline "一个帮助你研究和审计项目、预防返工、修复根因，并改善界面设计与使用体验的 Agent Skill。" --identity-image assets/readme/hero.svg --identity-image-width 160 --branch main --navigation-target docs=SKILL.md
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
