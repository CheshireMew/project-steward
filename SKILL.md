---
name: project-steward
description: "从项目过程与真实结果提炼可迁移治理方法，并在明确要求时自我进化；按实施计划审计完成度，研究和整理仓库，判断开源采用、目录职责、许可证与致谢；预防返工、沿根因修复跨层缺陷，治理外部工具、持久操作、架构质量、真实用户链、产品 UI/UX、界面美观与使用质感、README、日志、模板、用户环境、许可证和仓库发布。Use to learn/evolve from project history; audit a plan or repository; understand or organize a codebase; study open-source adoption/attribution; prevent rework/remediate root causes; inspect external-tool compatibility, durable operations, architecture cohesion/coupling, duplication or god modules, user chains, UI/UX/interface aesthetics, README, logging, templates, user environments, licensing, publication, and project health. Not for a single-function explanation or security-, dependency-, CI-, or monitoring-only tasks."
---

# Project Steward

## 角色与路由

Project Steward 保存跨项目可复用的治理方法。项目自己的产品决定、架构事实和长期约束留在项目现有真源中；用户和机器的可变工具事实留在项目与 Skill 之外的环境档案中。

先按用户要得到的结果选择主路径；同一请求中的独立结果分别建账：

1. 历史对话、纠正、完整实施过程或目标 Skill 职能边界：对话学习与自我进化。
2. 功能、重构、迁移或跨层改动开始前消除返工：改动前预防。
3. 缺陷、半迁移、重复修补、真实链路失效，或内聚、耦合、重复、上帝模块检查：根因治理。
4. 检查、接入或修复项目与外部工具、官方格式或协议的兼容关系：外部工具兼容性。
5. 看懂仓库、目录或源码包的用途、架构和能力，或研究参考项目：项目研究与讲解。
6. 盘点或整理项目目录，判断真实使用、生成状态、忽略、移动、归档与删除边界：项目目录治理。
7. 建立、采用、升级或检查项目模板：项目基线与模板。
8. 把稳定默认写入模板：模板演进。
9. 定义、审查、设计、重建、实施或验收产品体验、UI/UX、界面美观度与使用质感：产品体验与界面治理。
10. 审计、重写 README 或制作 GitHub 主页视觉：README 与主页。
11. 治理项目日志、LLM 记录、长期记忆、TTS 或日志查看结果：人性化日志。
12. 初始化 Git、创建仓库、提交、推送、改变可见性或验证远端：仓库建立与发布。
13. 选择、应用或批量治理许可证与第三方授权：许可证治理。
14. 建立或消费用户环境档案，检查工具、缓存、SDK、终端或长任务：用户环境档案与执行环境。
15. 按实施计划逐项核对完成度，或全面检查、判断项目健康状况和排列项目级风险：项目综合审计。
16. 大型运行产物的存储治理：生产存储预防与审查。

只点名本 Skill 时按现有材料选择最匹配路径；材料不足时给出一个贴近上下文的直接请求示例并停下。

主路径选定后，在任何项目写入或专项实施前建立路由账本：用户最终结果、主路径、固定必读方法、条件专项及其触发证据、动作门槛、正式消费者、验收和停止位置。固定必读方法不能因为局部修改看起来明显而跳过；条件专项只有取得适用证据才叠加。同一请求后来增加验收项时更新原账本，不用最新症状替换仍有效的范围。

## 共同边界

- 普通业务功能仍由当前开发任务负责；用户只要求解释单条报错、单个函数或局部行为时，在回答该结果后停止，不升级为项目级改造。只有请求本身要求预防、治理、迁移、自我进化或项目级结果时才进入相应路径。
- 选择路径后立即冻结范围、写入权限和停止位置。检查、审计、诊断、评估、分析、复盘或报告默认只读；同一请求明确要求修复、治理、实施、修改、更新或自我进化时才获得相应写入权限。
- 用户提供源码归档并要求看懂、审计或研究项目，或只点名本 Skill 并附上源码归档时，解压是进入只读研究所需的材料准备，不是项目正式写入。直接按“项目研究与讲解”确定目标根，运行既有脚本解压到独立避重名目录，读取脚本返回的项目根并继续只读研究，无需额外取得解压确认。该动作只授权创建研究副本和读取其内容；运行项目、安装依赖或解压工具、修改项目、移动或删除原文件、提交和发布仍分别授权。
- 联网、下载、安装、运行、生成、写入、移动、归档、删除、提交、推送和发布分别授权；只有对应主路径明确列出的独立完成合同可以合并同一结果内的状态改变。运行或生成不等于获得项目写入权限；提交或推送不自动授权等待 GitHub Actions、部署或远端验证。
- 点名 Project Steward 只选择治理方法，不授予目标项目提交、推送或发布权限。普通目标项目修改在本机相关验证后停止；只有用户明确要求提交或推送，或所选独立路径本身已经取得该结果的确认，才进入对应仓库发布合同。Project Steward 自我进化与 Star History 分别按各自主路径处理，不能互相补造权限。
- 用户确认 Project Steward 自我进化方案且未要求只改本地时，当前跟踪远端存在即默认把整个当前工作区作为一个不可拆分的发布范围：验证全部已跟踪修改、未跟踪文件和现有删除，使用 `git add -A` 一起提交并推送当前跟踪分支，推送成功后停止；任何一项不能共同发布时保留完整工作区并停止。该默认不授权创建远端、强制推送、改变可见性、实施新的删除或等待远端验证。
- 每个用户回合、内部轮次、自动续跑和上下文压缩恢复开始时，任何工具调用或状态改变前都先从最近一次明确用户动作恢复尚未完成的结果、范围、权限和停止位置。只有同一结果仍未交付且范围、受影响链与权限未变时才继续；只读结果已经交付、没有新的明确动作、用户改变结果、出现无关问题或需要新增权限时停止并等待确认。审计发现、助手建议、内部计划、目标名称、待办清单和自动提示都不能补造新结果或写入权限。
- 工作从短动作扩展为多阶段、进入等待或证据状态发生变化时，主动说明扩展原因、已完成检查点、当前状态、下一项可观察结果和所需输入；状态不变时不重复刷屏，也不能用流程说明掩盖范围扩张。
- 新的独立请求替换尚未完成的结果时，先交接已经写入或改变的对象、已有证据、尚未验证的用户承诺、运行进程、残留、原权限和停止位置；新请求不授权继续、回退或清理旧结果。
- 先冻结准确项目根、材料范围、活动文件和真实消费者。Git 只在准确项目根直接存在 .git 且当前路径确需历史、工作树或发布证据时使用。
- 来源必须读到明确末尾；长文件先取得行数、字节数或分页能力，再按稳定区间完整读取。并发变化触及行为合同、影响文件、消费者、验证或用户结果时，旧确认失效，重新规划并确认。
- 多项探测仅在能逐项保留输出、错误和退出状态时组合；Shell 后句可能遮蔽前序失败时先进入“用户环境档案与执行环境”。批次失败后保留仍新鲜的成功证据，只把被遮蔽、未执行或状态未知的项目单独补跑。
- 项目事实写回项目现有唯一真源；环境事实写入独立用户档案；可迁移治理方法才进入本 Skill；模板只接收某类项目每次都应执行的稳定默认。
- 判断历史或外部材料中的能力是否已经存在时，先完成独立结果拆分和必要的因果排序，再遮住来源检查目标能否认出同一条件、保留同一构成性细节并作出同一具体处理；只有上位治理框架算部分具备。完成逐项比较后才提炼共同机制和特殊维度。
- 验证按改动风险选择层级：每个验证阶段先按 `references/ci-execution-governance.md` 消费最近一次已完成的公开仓库失败，只运行当前机器上直接覆盖本次改动和验收主张的目标检查；其它平台、完整回归、远端 CI 与真实用户链只有用户明确要求、代码冻结或目标检查证明系统性影响时才进入。
- 状态改变后直接回读权威目标。完成验证必须沿正式生产者、传输或存储边界、消费者和用户可观察结果；不能让消费端手写假数据或 mock 掉正在验证的核心链路。
- 测试结果用于关闭承诺或宣告完成前，预期关键测试身份必须与测试框架实际收集的唯一身份一致；缺失或非唯一身份都只能标为未覆盖。
- 诊断读取设置、运行报告、结构化制品或日志时，按 `references/log-audit-standard.md` 先投影当前判断需要的允许字段；未知结构不得整份递归输出，凭据必须在进入工具输出、对话或诊断导出前脱敏。

## 对话学习与自我进化

先完整读取 `references/conversation-learning-and-self-evolution.md` 和 `references/skill-self-evolution-governance.md`。

任一用户结果含失败、纠正、保护拦截、临时绕行或残留时，再读取 `references/root-cause-remediation.md`。读取顺序固定为：按结果恢复完整过程，沿因果层级确定主要学习主题和独立次级结果，再恢复其中会改变未来治理的具体细节并按共同边界逐项比较目标能力，之后才提炼共同机制和特殊维度、判断可迁移性、职能边界和正式所有者，最后判断历史责任。绕行与残留不得覆盖更早且证据成立的可控根因；后续纠正改变主要原因时，现有方案与确认立即失效。只有成功结果且不存在这些信号时，不加载根因方法。

能力比较必须先区分“方法缺失”和“已有方法没有被路由、执行或验收”。前者只原位强化唯一方法所有者；后者只修最早失效的主路由、动作门槛、正式消费者或验证，不在其它文件增加同义规则。方案按所有者和消费链组织，不按对话出现顺序堆叠补丁。

用户只要求分析时保持只读。明确要求吸收、自我进化、更新、优化或迭代 Project Steward 时，先交付未来行为、职能边界、代表性输出、影响文件和验证方式并停下；用户确认该方案后才修改活动 Skill。确认方案未声明只改本地时，同时读取 `references/repository-publication.md`；当前跟踪远端存在时，把整个工作区按实际影响验证，使用 `git add -A` 将已跟踪修改、未跟踪文件和现有删除一起提交并推送当前跟踪分支，推送成功后停止，不等待远端检查。远端、认证、分支保护、分叉、验证失败或任何一项不能共同发布时保留完整工作区并停在准确边界，不退回选择性提交。

Project Steward 自我进化时必须执行活动文本约束：

- 写入前运行 `scripts/check_file_budgets.py .`，记录全部活动 UTF-8 文本文件的外层工具预算和直接 reference 集合，并给每条新增规则指定唯一活动所有者。
- SKILL.md 只拥有路由、触发条件、读取顺序、权限、输出和停止位置；完整方法、表格、检查清单与例外由对应 reference 唯一拥有，主文件只保留直达链接。
- 写入后 SKILL.md 仍不得超过 220 行或 14,000 个字符，并且每个活动文本文件按 UTF-8 字节数除以四向上取整的外层工具估算不得超过 9,000 tokens。归档、依赖、缓存、构建与运行产物、二进制媒体和不作为模型输入的媒体运行资源不参与文本门槛。
- 超限时按唯一职责迁移完整章节、函数族或测试主题并同步全部路由、公共入口、正式消费者和测试身份；不得删减能力、必要方法、完整示例或协议细节，也不得提高上限、拆行或压成不可维护文本。无法完整保留时停止写入、重新规划，不得宣称完成。

## 改动前预防

先依次读取 `references/change-prevention.md`、`references/change-prevention-state-and-capability.md`、`references/change-prevention-delivery-boundaries.md` 和 `references/change-prevention-verification.md`，由它们共同负责目标行为、唯一真源、影响图、最终接口、旧路径退出和真实用户链验收。按问题叠加：

- 持久操作、队列或调度器的有界批次与积压排空、恢复、重启、成组产物，或常驻有状态服务中可发现会话与共享资源的并发准入、释放和关闭：`references/durable-operation-governance.md`
- 任务状态、进度或自动续跑：`references/task-progress-governance.md`
- 高成本结果需要分阶段展示、确认、连续自动执行或按上游变化失效：`references/staged-result-governance.md`
- 同一结果由多份规格、计划、任务或研究产物表达且需决定演化关系，或涉及派生产物、语义缓存、工作单元切分、候选资格、配额、补位、资源池利用或重复 Agent 编排：`references/derived-artifact-governance.md`
- 项目级 CI 的验证计划、执行环境缓存、测试资源分层、耗时分片、早失败和精准重跑：`references/ci-execution-governance.md`
- 大型媒体、缓存、测试证据、下载、模型或中间产物会持续写盘，或用户要求把预防能力写进生产项目：`references/production-storage-governance.md`
- 运行中配置会重建共享服务、provider、存储根或组合图：`references/runtime-generation-governance.md`
- 难复现、时序、并发、背压或昂贵完整链：`references/hard-to-reproduce-diagnostics.md`
- 外部、持久化、模型、网络或进程 JSON 存在多处解析、容量、原子分片、重放游标或合同歧义：`references/structured-data-boundary.md`
- 模型参与任务判断、状态表达、运行时事件或结构化回复，需要核对消息来源、角色、路由、线请求与呈现职责：`references/model-mediated-operation-governance.md`
- 以外部源码为一次性起点建立独立产品，或选择性吸收其扩展生态：`references/source-fork-and-ecosystem-adoption.md`；实际复制代码时同时读取 `references/license-governance.md`
- 产品体验或界面：`references/product-experience-governance.md`；需要设计或交互方法时再读 `references/ux-design.md`

只有用户明确授权实施时修改项目；只要求计划则停在影响图、目标边界、迁移顺序和验收合同。

## 根因治理

先读取 `references/root-cause-remediation.md` 和 `references/root-cause-verification-and-closure.md`。诊断停在证据、影响范围与最终修法；实施才一次迁移全部生产者、边界和消费者，并退出旧架构。按问题叠加：

修复承接本任务先前的综合审计，或用户明确要求修复该审计中的全部问题时，原审计交接账本继续作为结项合同；写入前固定从 `references/change-prevention.md` 进入“改动前预防”完整主链，涉及移动或归档时同时进入“项目目录治理”；最后一次相关修改后返回 `references/project-audit.md`，从原覆盖范围和当前已接受合同重新生成覆盖与发现账本。单点缺陷不会仅因历史中存在无关审计而扩张到这条链。

- 持久操作、队列或调度器的有界批次与积压排空、恢复，或常驻有状态服务的会话准入与释放竞争：`references/durable-operation-governance.md`
- 任务进度或持续状态：`references/task-progress-governance.md`
- 返工来自阶段确认缺失、确认对象漂移或变化被错误扩散：`references/staged-result-governance.md`
- 返工来自多份产物关系不明、理由在重新生成时丢失、全量重算、错误缓存失效、危险切分、候选硬约束被补位绕过、资源误判或编排往返：`references/derived-artifact-governance.md`
- 审计修复或项目级改动会使用完整套件，或触及验证控制面、CI 分类、资源、分片、成本与重试：`references/ci-execution-governance.md`
- 运行时操作跨越服务代次、热配置事务或物理根切换：`references/runtime-generation-governance.md`
- 难复现或低可观测问题：`references/hard-to-reproduce-diagnostics.md`
- 结构化 JSON 的编码、资源预算、逻辑消息容量、原子分片、重放游标、数值、schema 或错误语义分叉：`references/structured-data-boundary.md`
- 模型回复、任务状态或结果呈现与真实运行时不一致，或需要定位实际发送给模型的请求：`references/model-mediated-operation-governance.md`
- 可视层级、变换或动效所有权：`references/interaction-motion.md` 和 `references/interaction-navigation-and-media-lifecycle.md`；需要实际运行画面验收时再读 `references/implementation-review.md` 与 `references/implementation-review-visual-evidence.md`
- 工具、路径别名、执行环境或长任务：`references/user-environment-governance.md`
- 大型媒体、缓存、测试证据、下载、模型或中间产物造成容量增长、跨根散落或无主残留：`references/production-storage-governance.md`
- 事件、版本、历史或缓存把计划影响范围误当成实际变更事实：`references/change-prevention.md` 的“计划范围与实际变更事实分离”合同
- 局部状态、心跳或遥测更新覆盖、清空了未声明字段，或者消费者无法区分完整快照与局部补丁：`references/change-prevention.md` 的活动投影更新合同
- 源码、README、脚本、测试或配置硬编码本机与部署事实：`references/change-prevention.md` 的项目运行配置边界；用户机器事实同时读取 `references/user-environment-governance.md`
- 内聚、耦合、语义重复或上帝模块：`references/architecture-cohesion-governance.md`

## 外部工具兼容性

读取 `references/external-tool-compatibility.md`。官方文件格式、作者工具或导出链兼容也走此路径。兼容关系涉及跨项目根的公共合同、派生快照或复合交付包时，同时读取 `references/change-prevention.md` 的公共合同、合同采用闭包与跨根交付边界。兼容性检查保持只读，并按明确适配器逐层报告可执行产物、能力合同、调用与隔离、临时输入、上游线协议、结构化结果、宿主独立核验和用户链；只有明确授权修复或接入时才修改获准项目根。

## 项目研究与讲解

先读取 `references/project-research.md`。只读取回答当前问题所需的项目表面；用户明确要求完整研究或能力采用时才扩展覆盖，并同时读取 `references/source-fork-and-ecosystem-adoption.md`，先追溯原始上游并区分直接复用与方法学习；确认会直接复用代码或资源时再读取 `references/license-governance.md`，把第三方资源与致谢写入目标项目 README。完整研究产生的能力台账在后续“开始吧”或实施请求中按稳定身份与接受状态继续消费，并交给改动前预防，不能把独立发现扩成实施范围。获准候选会把外部模型、运行时、包、CLI、SDK、daemon 或服务带入目标项目的正式安装或运行链时，实施和验收同时读取 `references/external-tool-compatibility.md`；准备安装或把工具、模型与运行时入口持久绑定到用户机器时再读取 `references/user-environment-governance.md`，只读采用建议不因此获得安装或配置权限。需要衡量效果、失败样本和置信度时读取 `references/project-effectiveness-review.md`；需要保存可复核报告时读取 `references/project-research-report.md`。源码归档先用 `scripts/extract_project_archive.ps1` 和 -DestinationRoot <目标根> 解压到独立目录；没有另行指定目标根时使用 E:\Work\BaiduSyncdisk\Code\Example。脚本返回项目根后立即读取 `references/archive-safety-screening.md` 并运行 `scripts/inspect_extracted_project_safety.py`；只有该方法确认重大隐患时才进入用户输出，否则静默继续原研究。

## 项目目录治理

读取 `references/repository-directory-governance.md`，先运行 `scripts/inspect_project_tree.py`，再核对候选生产者、路径真源、消费者与生命周期。检查和计划只读；整理、移动、归档、删除分别授权。大型媒体、缓存、测试证据、下载、模型或中间产物涉及占用、可回收量或清理终态时，同时读取 `references/production-storage-governance.md`。移动触及活动源码、模型、数据、素材、构建或运行入口时读取 `references/change-prevention.md`；存在旧路径、双读、同步副本或半迁移时读取 `references/root-cause-remediation.md`，一次迁移消费者并退出旧入口。

## 项目基线与模板

读取 `references/project-template-system.md`。只读请求停在 inspect、plan 或 verify；adopt、upgrade 或项目配置写入需要明确授权，并验证正式消费者。

## 模板演进

读取 `references/template-evolution.md`。先证明候选是稳定默认而非仍需临场判断的方法，再同步模板版本、注册表、哈希、文档和消费者测试。

## 产品体验与界面治理

先读取 `references/product-experience-governance.md`，再按以下固定入口和条件专项执行：

该路径直接负责 UI/UX、界面美观、设计实施与真实画面验收；所列 reference 是内部方法，不是外包边界。

- 界面诊断、评价、优化或重建固定读取：`references/ux-design.md`、`references/interface-experience-quality.md`、`references/interface-problem-patterns.md`、`references/implementation-review.md`、`references/implementation-review-visual-evidence.md`。修改前先冻结全部相关窗口、页面、面板、覆盖层、主要状态和用户旅程；不能把截图中最醒目的局部问题当成完整审查范围。
- 从零设计或改变视觉方向：`references/design-method.md`、`references/surface-registers.md`
- 布局、设计系统、交互和动效：`references/layout-responsive.md`、`references/design-system-alignment.md`、`references/interface-guidelines.md`、`references/interaction-motion.md`
- 参考界面忠实重建：`references/reference-interface-reconstruction.md`
- 已确认是桌面、Tauri/Vue 或本地文件工作区时，对应读取 `references/desktop-app-governance.md`、`references/tauri-vue-governance.md`、`references/local-file-workspace-governance.md`；项目形态已经成立时不得因当前反馈只提到颜色、间距或文案而省略平台外壳。
- 任务状态或进度：`references/task-progress-governance.md`

依赖既有定位或设计系统时，每个任务最多运行一次 `scripts/context.mjs`；忠实重建参考界面时由 `assets/reference-reconstruction/component-spec.md` 承担组件规格。

## 仓库建立与发布

依次读取 `references/repository-publication.md` 和 `references/repository-publication-execution.md`。区分初始化、提交、远端创建、推送、可见性、检查与部署；每一步只执行已经授权的停止位置，并在状态改变前后核对准确仓库身份、索引、分支、远端和并发变化。

## README 与主页

读取 `references/readme-delivery.md`，建立覆盖 Git 边界、README 正文、视觉、多语言、许可证、Star History、Topics、About Description/Website、验证与停止位置的交付账本；只读停在账本，优化、重写或完整处理才实施。再读 `references/content-architecture.md`；完整优化或含 Logo、hero 时由 `references/visual-direction.md` 完成代码优先的正式身份源调查，再按需读 `references/project-native-hero.md` 和 `references/github-readme-canvas.md`。多语言、个人入口和仓库状态区由 `scripts/readme_header.py` 按 `assets/readme-profile/profile.json` 消费真实项目事实。公开 GitHub 仓库完整优化默认交付 Star History、Topics 与 About：Star History 读取 `references/github-star-history.md` 和 `references/repository-publication.md`，Topics 由 `scripts/github_topics.py` 写入回读，About 由 `scripts/github_about.py` 写入回读；除非用户退出或不适用，缺少任一真实消费者的成功结果都不能完成整项交付。按需选择：

- SVG 与混合视觉：`references/svg-production.md`、`references/hybrid-svg-production.md`
- 动效：`references/motion-production.md`
- 平台边界：`references/platform-guidelines.md`
- 自托管 Star History 的专项诊断或接入：`references/github-star-history.md`；只问失效原因或现状时保持只读，实施时精确提交并推送调用仓库改动，手动派发工作流后立即停止；只有用户另行要求远端验收时才消费已经完成的 API、生成器、输出分支、raw SVG 和 README 链路

README 不作为每项内部治理规则的第二份活动真源；自我进化只有改变公开身份、读者路径、主要入口或维护导航时才更新 README。完成后运行 `scripts/audit_readme.py`，并在实际渲染表面核对。

## 许可证治理

先读取 `references/license-governance.md`。用户确认具体方案后再读取 `references/license-rollout.md` 并实施；只读请求停在内容边界、第三方依赖与方案比较。

## 人性化日志

读取 `references/log-audit-standard.md`。涉及访问日志、状态轮询、任务接收或后台终态时，再读取 `references/durable-operation-governance.md` 和 `references/task-progress-governance.md`。沿一次真实操作检查生产、上下文、存储、读取和最终查看结果；不以一条漂亮示例替代完整事件链。

## 用户环境档案与执行环境

读取 `references/user-environment-governance.md`。档案 schema 由 `assets/user-environment/profile.schema.json` 负责，确定性操作由 `scripts/user_environment_profile.py` 负责。inspect、plan、verify 和 resolve 保持相应只读或消费边界；apply --write 需要明确档案写入授权，且不自动授权安装、下载或系统设置修改。

## 项目综合审计

依次读取 `references/project-audit.md` 和 `references/project-audit-release-and-evidence.md`。询问实施计划完成度时，先从原计划建立符合性账本；获准修复后从原计划和当前已接受合同重新生成全新复查，不沿用旧标记，也不从测试反推计划范围。全面检查则先按项目形态建立全部适用维度的覆盖账本，再加载这些维度要求的专项；不得只根据已经发现的问题回填审查范围。性能适用时读取 `references/project-performance-governance.md`。只读审计不自动治理。评估用户效果时追加 `references/project-effectiveness-review.md`，检查任务体验时追加 `references/task-experience-audit.md`。

## 平台模板资源

处理对应项目类型时按需读取：

- 桌面应用：`references/desktop-app-governance.md`
- Tauri v2 + Vue：`references/tauri-vue-governance.md`
- 本地文件工作区：`references/local-file-workspace-governance.md`

这些资源是活动方法，不等于项目已经采用模板；只有明确采用并由正式消费者读取的 .project-steward/project.json 才构成项目模板状态。

## 输出与完成

输出先给结论，再说明范围、证据、未知项和下一动作。分析不得写成已经实施；结构检查不得写成真实用户链成立；当前任务行为核对不得写成独立冷启动已经证明。

有影响图时至少包含生产者、传输或存储边界、消费者、最终用户结果、唯一真源、旧路径退出条件和验收入口。涉及多个历史结果时逐个报告主要原因、成功机制、能力缺口、正式所有者和验证等级。

只有活动路由、对应方法、正式消费者、确定性测试以及本轮获准的真实用户链都一致后，才报告完成。
