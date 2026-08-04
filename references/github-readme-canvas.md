# GitHub README 画布

用于所有 README 视觉任务。它只定义 GitHub 可靠支持的构件、尺寸、响应式、文件组织和无障碍要求，不选择背景明暗、配色、字体角色、构图或容器样式。完成画布约束后返回当前 README 子类型。

## 可靠构件

GitHub README 可靠支持 Markdown、表格、链接、代码块、`details`、本地图片以及用于简单对齐和尺寸控制的 HTML。

推荐嵌入：

```html
<p align="center">
  <img src="./assets/readme/hero.svg" width="100%"
       alt="项目名称及其具体用途">
</p>
```

混合 SVG 布局与栅格素材时发布已合成的 PNG/WebP：

```html
<p align="center">
  <img src="./assets/readme/hero.png" width="100%"
       alt="项目名称及其具体用途">
</p>
```

GitHub 能播放 GIF，但不会播放 SVG 内部动画。动画任务保留静态 SVG 源和回退。

## 首屏辅助区

语言与项目导航共用第一段，个人入口和仓库状态分别使用后续独立的居中段落，让 GitHub 在窄屏自然换行。当前语言使用文本，其它语言使用真实链接；文档、贡献和反馈在语言组后使用竖线分隔，并分别指向当前活动说明、独立贡献指南和已启用的正式反馈渠道。徽章图片由外层 `<a>` 提供点击目标，不依赖徽章服务 URL 中的 `link` 参数，也不把动态数字写进 alt text：

```html
<!-- readme-header:start -->
<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/OWNER/REPOSITORY/issues">反馈</a>
</p>

<p align="center">
  <a href="https://example.com/profile"><img src="https://img.shields.io/badge/Profile-name-1F6FEB" alt="Profile: name"></a>
</p>

<p align="center">
  <a href="https://github.com/OWNER/REPOSITORY/stargazers"><img src="https://img.shields.io/github/stars/OWNER/REPOSITORY?style=flat" alt="GitHub Stars"></a>
</p>
<!-- readme-header:end -->
```

实际成品由 `scripts/readme_header.py` 消费活动 profile、真实导航目标与目标仓库身份生成，不从示例复制取值。每个链接与图片提供独立含义；远程图片失效时 alt text 和外层链接仍允许读者识别并进入目标。徽章自带可读表面并在 GitHub 深浅背景中核对，必要文字、安装步骤和项目定义仍留在普通 Markdown 中。语言文件、配置的本地导航目标或许可证文件缺失，个人 profile 不适用于目标 owner，或者仓库不是公开 GitHub 项目时，不生成伪入口。

## SVG 画布

- 全宽模块使用 `1200` 单位宽的 `viewBox`。
- hero 常见高度 `300–420`。
- 章节标题常见高度 `120–170`。
- 解释图常见高度 `320–760`。
- 重要内容离边缘至少 `48–64` 单位。
- 大型视觉包含 `<title>` 和 `<desc>`。
- 使用系统字体，如 `-apple-system`、`BlinkMacSystemFont`、`Segoe UI`、`PingFang SC` 和 `sans-serif`。
- 视觉合同确实使用的圆角、线宽和间距在同一项目素材中保持一致。

`viewBox` 是坐标系，不是最终像素宽度。全宽 `1200` 单位素材按 `900px` 桌面宽度验收：

| 角色 | SVG 字号 | 约等于 900px 显示 |
| --- | ---: | ---: |
| 项目主标题 | `48+` | `36px+` |
| 章节标题 | `40+` | `30px+` |
| 必要图表或卡片文字 | `20+` | `15px+` |
| 辅助标签 | `18+` | `13.5px+` |
| 非必要元数据 | `16+` | `12px+` |

必要文字在 `360px` 窄屏仍需可用。过密时减少内容、拆图或把完整说明放回相邻 Markdown。

## GitHub 中不可靠的 SVG 功能

成品不依赖：

- `<script>`；
- `foreignObject`；
- 外部样式表和网络字体；
- 远程图片；
- 必要 hover 状态或 SVG 内动画；
- 体积很大或容易污染边缘的复杂滤镜。

使用路径、形状、文字、图案、渐变、裁剪和简单变换。发布前检查解析后的 SVG，而不只检查源码看起来是否正确。

## 响应式

GitHub 会整体缩放图片。每个全宽素材至少查看：

- `900px` 桌面宽度；
- `360px` 窄屏；
- GitHub 深色和浅色页面环境。

长文本不放进多列表格。全宽图可以有多列，但必要标签必须足够大；窄屏无法读取的详细说明回到 Markdown。

## 资产组织

仓库专属素材默认放在：

```text
assets/readme/
├── hero.svg
├── hero.png
├── hero.gif
├── showcase.png
├── section-*.svg
├── workflow.svg
└── source/
    ├── hero-layout.svg
    ├── hero-subject.png
    └── hero-prompt.txt
```

使用小写连字符文件名。中间帧、色键图和试验稿放在任务临时目录；用户要求保留的编辑源放入 `source/`。

## 无障碍与可信度

- alt text 说明图片传达的作用，不写“横幅”或“截图”这种空标签。
- 安装命令和关键说明保持为可复制文字。
- 使用真实输出，概念图明确标注为概念图。
- 图片失效时，标题、说明、命令和链接仍能让 README 成立。
- 素材提供维持自身对比度所需的表面。背景可以是浅色、深色或经双主题验证的透明表面，具体选择来自项目视觉合同，不由 GitHub 画布默认指定。

画布约束完成后返回当前 README 子类型，不选择 SVG、混合构图或动画。
