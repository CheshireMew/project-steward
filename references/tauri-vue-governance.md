# Tauri + Vue 项目治理

用于已经确认使用 Tauri v2 与 Vue 的桌面项目。它把 Tauri 配置、Vue 应用外壳、窗口 API、capability 权限和 Windows 实机行为连接成一条链，不决定产品任务、视觉方向或上层项目路径。

## 1. 技术栈识别

至少同时满足：

- 项目根存在 `src-tauri/tauri.conf.json` 或可解析的等价 Tauri 配置；
- `package.json` 的依赖或开发依赖包含 Vue；
- 前端源码和 Rust/Tauri 根都属于同一准确项目边界。

只出现一个 `src-tauri` 目录或一个 Vue 文件不足以自动采用模板。

## 2. 集成标题栏

项目决策为 `integrated` 时：

1. Tauri 主窗口配置显式关闭装饰，例如窗口的 `decorations` 为 `false`。
2. Vue 顶层应用外壳只创建一个标题栏，并与导航和主内容共享同一个根布局。
3. 拖动区域使用 `data-tauri-drag-region`，或使用明确的 `startDragging()` 实现；交互子元素不属于拖动区。
4. 最小化、最大化或还原、关闭按钮使用当前窗口句柄。
5. 内容标题的底边线只覆盖内容区，标题栏或外壳边界才可以横跨整个窗口。
6. 浏览器开发预览允许没有原生窗口 API，但必须有明确的环境分支；不能让桌面按钮在浏览器中静默报错。

项目决策为 `native-explicit` 时，窗口装饰保持开启，Vue 不再渲染第二套窗口按钮。两种策略不能同时活动。

## 3. Capability 权限映射

Tauri v2 capability 决定哪些窗口或 webview 能调用哪些 core 或插件命令。检查项目实际启用的 capability 文件或内联 capability，并逐项对应前端调用。

常见映射：

| 前端窗口动作 | 对应权限 |
| --- | --- |
| `minimize()` | `core:window:allow-minimize` |
| `toggleMaximize()` | `core:window:allow-toggle-maximize` |
| `startDragging()` | `core:window:allow-start-dragging` |
| `close()` | `core:window:allow-close` |
| `destroy()` | `core:window:allow-destroy` |

权限可能来自明确 permission set，但最终必须证明目标窗口实际获得该命令。看到 capability 文件里有相似字符串不等于生效；窗口标签、平台和引用关系都要匹配。

`close()` 与 `destroy()` 不能互换。正常产品退出优先使用能够进入项目关闭合同的正常关闭语义；如果源码调用 `destroy()`，必须同时证明强制销毁是有意行为、清理已经完成且 `allow-destroy` 已授予。

## 4. Vue 外壳责任

Vue 负责：

- 标题栏、侧栏、内容头和主内容的布局；
- 主题、焦点、悬停和窗口状态展示；
- 把按钮操作转成单一窗口服务调用；
- 显示可理解的失败信息；
- 在组件卸载时清理监听器。

窗口 API 不应散落在多个按钮组件和页面。建立一个窗口服务或 composable 作为前端唯一边界，使权限、浏览器降级、错误转换和测试共享同一实现。

Rust/Tauri 负责：

- capability 和目标窗口；
- 需要原生保证的关闭、刷盘或进程生命周期；
- 本地文件、凭据和其它不能由 Vue 决定的能力。

同一保存状态不能由 Vue store 和 Rust 状态各自成为真源。

## 5. 关闭和刷盘

沿真实链核对：

```text
Vue 关闭按钮
  → 窗口服务
  → 保存或关闭协调器
  → Rust / 文件系统真实写入
  → 冲突与失败结果
  → Tauri 正常关闭命令
  → CloseRequested / 退出生命周期
  → 再启动读取
```

如果 Rust 拦截 CloseRequested，前端按钮、系统关闭按钮和快捷键必须进入同一协调器，避免一个路径保存、另一个路径直接退出。重复关闭请求要幂等，保存失败时不能销毁最后可恢复状态。

## 6. 确定性检查

模板脚本可以静态检查：

- Tauri 配置是否存在和可解析；
- Vue 依赖是否存在；
- `integrated` 决策下装饰是否关闭；
- 前端是否存在拖动区和最小化、最大化、关闭调用；
- 每个实际调用是否存在对应 capability 权限；
- `destroy()` 是否错误地只有 `allow-close`，或 `close()` 是否没有 `allow-close`。

静态扫描不能证明 capability 引用到准确窗口，也不能证明关闭刷盘和视觉边界，因此这些仍进入真实验收。

## 7. Windows 实机链

至少在 Windows 运行一次真实 Tauri 窗口：

1. 确认系统白色标题栏已经按项目决策出现或消失。
2. 拖动标题栏、双击切换、最小化、最大化、还原和关闭。
3. 检查标题栏、侧栏、内容头的分隔线没有越界。
4. 在浅色、深色和 125% 缩放下检查布局。
5. 制造脏文件，通过自定义关闭按钮退出，再启动读取保存内容。
6. 用系统关闭按钮重复同一链。
7. 制造保存失败或外部冲突，确认窗口保持可恢复且提示可操作。
8. 确认应用和开发终端没有 `not allowed` 权限错误或未处理 Promise。

完成后返回静态检查结果、真实窗口行为、关闭刷盘证据和未覆盖的平台。
