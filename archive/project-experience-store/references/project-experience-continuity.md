# 已归档：项目经验的连续使用

用于把一次项目里已经确认的认识保存下来，并让另一个项目在动手前真正读到和采用。项目内记录与跨项目经验承担不同职责：

```text
项目内记录
  保存这个项目现在成立的结论、证据和来源
  ↓ 提炼并确认
共享经验
  保存脱离项目专名后仍成立的判断方法
  ↓ 检索并判断适用性
另一个项目
  记录这条经验具体改变了哪个决定
```

另一个项目读取共享经验正文和来源关系，不读取来源项目的全部笔记。项目模板只接收已经稳定到应当成为某一类项目默认约束的少数经验；仍需结合情境判断的通用做法留在共享经验库。

## 1. 存储边界

项目内状态固定在：

```text
<项目根>/.project-steward/experience/
├── catalog.json
├── topics/<主题 ID>.md
└── history.jsonl
```

- `catalog.json` 是主题标识、当前状态、适用范围、正文位置和跨项目去向的索引。
- `topics/*.md` 是各主题当前成立的结论。更新同一主题时原位替换正文并递增修订号，不创建第二份“最新版”。
- `history.jsonl` 只记录何时、为什么改变当前结论，采用了哪条共享经验，以及分支结束时怎样处置认识；它不复制当前正文。
- 没有真实主题时只创建目录索引，不生成空主题、空历史或示例内容。

共享经验库位于 Skill 源码之外，由用户选择稳定目录。解析顺序固定为：

```text
命令行 --store
→ PROJECT_STEWARD_EXPERIENCE_STORE
→ 用户配置中的 experience_store
```

用户配置路径可由 `--config` 或 `PROJECT_STEWARD_CONFIG` 指定；未指定时使用当前操作系统的用户配置目录。项目目录不保存共享库的绝对路径，因此项目移动或克隆后仍由使用者自己的配置解析。

## 2. 建立项目记录

先只读检查：

```powershell
python scripts/project_experience.py inspect <项目根>
```

用户确认要保存项目经验后初始化：

```powershell
python scripts/project_experience.py init <项目根> --project-id <稳定项目 ID>
```

一个主题只有出现真实结论时才写入。先把正文准备为 UTF-8 Markdown，再执行：

```powershell
python scripts/project_experience.py upsert <项目根> `
  --topic <主题 ID> `
  --title <标题> `
  --summary <一句当前结论> `
  --applicability <适用条件> `
  --status validated `
  --evidence <可核对证据> `
  --body-file <正文文件> `
  --change-note <为什么建立或改变这项结论>
```

已有主题更新时必须传入当前 `--expected-revision`。这使并行任务不能在没有读到最新结论时静默覆盖它。项目主题状态含义为：

- `candidate`：已经值得保留，但证据还不足以作为当前确定结论；
- `validated`：已由用户确认、真实结果或可复现证据支持；
- `retired`：当前已不再成立，正文和历史仍保留用于解释去向。

正文写项目当前应该怎样判断和行动。原始聊天、完整日志、补丁和临时试验留在原证据位置；主题的 `evidence` 只保存能够回到这些证据的稳定说明。

## 3. 形成跨项目经验

首次使用先配置共享目录：

```powershell
python scripts/project_experience.py configure `
  --store <共享经验目录>
```

已有用户配置指向另一个目录时，命令保持原配置并停止；用户确认切换后再加 `--replace`。切换只改变以后解析的共享目录，不移动或删除旧目录内容。

项目主题进入共享库前必须通过四个问题：

1. 去掉项目名、文件名和本次补丁后，核心判断是否仍成立；
2. 能否说清它适用的机制、前提、最早决定点和可观察结果；
3. 另一个项目能否据此改变一个决定，而不只是收到“多注意”的提醒；
4. 当前证据支持候选、可注册经验，还是只支持项目内部结论。

通过后，使用新的共享 ID 创建经验；以后结论变化时更新同一 ID：

```powershell
python scripts/project_experience.py promote <项目根> `
  --topic <项目主题 ID> `
  --shared-id <共享经验 ID> `
  --title <通用标题> `
  --summary <通用结论> `
  --applicability <适用机制或项目范围> `
  --stage registered `
  --body-file <抽象后的正文> `
  --confirmed-by <确认者> `
  --change-note <本次新增或变化>
```

只有 `validated` 的项目主题可以进入共享库。`candidate` 表示还需要更多证据，不参与普通检索；`registered` 表示已可被其它项目显式采用；`retired` 表示已经退出使用。注册只代表可被检索，不代表每个匹配项目都应自动采用。

更新已有共享经验时必须传入当前 `--expected-revision`。脚本递增同一个共享条目的修订号、保留来源项目和主题修订，并把再次验证写回同一条经验，不制造并列的“新版本”。

结论已经不再成立时，用同一个 `promote` 入口和当前修订号把现有共享条目更新为 `--stage retired`，正文说明它为何退出及替代判断。退役内容保留来源与历史，但不再进入普通检索；以后出现新证据时仍更新同一 ID。

## 4. 动手前检索与采用

开始功能、重构或迁移前，用当前用户结果、改动对象、平台和主要机制组成查询：

```powershell
python scripts/project_experience.py search <项目根> `
  --query <当前改动及其机制>
```

检索结果先返回当前项目主题，再返回已注册的共享经验，并包含完整正文路径与正文。分数只帮助缩小候选；正式采用前逐条判断：

```text
机制是否相同：
触发条件是否相同：
最早需要决定的问题是否相同：
预期用户结果是否相同：
这条经验具体改变或排除了什么：
```

只有最后一项能写成明确决定时才算采用。采用、调整后采用，以及验证后排除都具有价值，分别记录为 `adopted`、`adapted`、`ruled-out`：

```powershell
python scripts/project_experience.py adopt <项目根> `
  --shared-id <共享经验 ID> `
  --expected-revision <检索到的修订号> `
  --outcome adopted `
  --applied-to <本次改动中的决定位置> `
  --decision <它实际改变的决定> `
  --confirmed-by <确认者>
```

这条记录同时进入当前项目历史和共享经验的验证记录。只是关键词相似、读过但没有改变决定、或者内容与本次改动无关时，不记录采用。

## 5. 验证与完成

写入后运行：

```powershell
python scripts/project_experience.py verify <项目根>
```

验证必须证明：

- 项目索引能够解析每个当前正文；
- 共享索引能够解析每个经验正文；
- 项目主题指向的共享经验真实存在，并保留该项目主题的来源关系；
- 当前项目记录的采用事件也存在于共享经验的验证记录；
- 退役内容不会进入普通检索。

用户可观察的完成结果不是“创建了几个文件”，而是：项目 A 的确定结论有稳定位置；抽象后的共享经验保留来源；项目 B 能从正式检索入口读到完整内容；采用记录能说明它改变了 B 的哪个决定；B 的验证结果又回到同一个共享条目。
