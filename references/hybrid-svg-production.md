# 混合 SVG 构图

上层已经确认“SVG 控制排版，栅格素材提供人物、角色、有机纹理、复杂材质或光影”时使用。它消费已经选定的视觉合同，不重新选择背景、配色、构图、容器语言或主题元素。真实截图、输出、标志或已有项目插画更能说明项目时，优先使用真实素材。

## 输出合同

SVG 是可编辑构图源，PNG/WebP 是默认发布素材：

```text
assets/readme/
├── hero.png
└── source/
    ├── hero-layout.svg
    ├── hero-subject.png
    └── hero-prompt.txt
```

色键源图和试验图放在任务临时目录。用户未要求时不把废弃版本带入仓库。

发布素材不包含绝对路径、未解析相对栅格引用或远程图片。用户明确要求自包含混合 SVG 时，先说明 base64 体积和渲染兼容性，再验证 GitHub 实际显示。

## 制作顺序

1. 读取并冻结上层视觉合同及每项表面选择的来源。
2. 写清栅格主体承担的沟通任务，以及它为什么属于该项目。
3. 先完成 SVG 排版，并为主体预留准确位置。
4. 使用当前环境可用的图像生成能力制作主体；标题、正文、标签、标志和 UI 文字留在 SVG 层。
5. 在提示词中确定姿势、视线、裁切、配色、光线方向和负空间，使其匹配预留位置。
6. 选择背景处理：
   - 不透明、硬边主体可以使用色键移除。
   - 头发、毛发、烟雾、玻璃、半透明、反射或软阴影不需要后续大幅移动时，优先生成匹配最终背景。
   - 用户要求原生透明输出时，遵守当前图像生成能力的透明输出条件。
7. 把最终透明主体保存进项目，和 SVG 排版合成后导出 PNG/WebP。
8. 分别检查透明层和最终构图；一次只调整一个问题。

## 色键提示结构

选择主体中不会使用的色键；通常使用 `#00ff00`，主体含绿色时使用 `#ff00ff`。

提示词包含：

```text
Asset type: transparent cutout subject for a GitHub README hero
Composition/framing: match the reserved hero area; specify crop, gaze, and direction
Color palette: use the selected project palette; exclude the selected key color; do not inherit colors from another project or example
Constraints: one isolated subject; generous padding; no text; no letters; no logo; no watermark
Background: perfectly flat solid key color; no gradient, texture, floor, reflection, or shadow
```

背景移除由当前图像生成能力提供的正式方法完成，不复制另一套处理脚本进本 Skill。

## 构图规则

- SVG 只控制视觉合同实际使用的文字、标志、图、边界、连接和对齐；合同没有网格或容器时不补加。
- 栅格层只提供确实受益于生成或摄影的材质、角色、复杂光影和有机细节。
- 主体光线方向和边缘颜色匹配 SVG 配色。
- 主体放入命名组或预留框，后续替换不重做排版。
- 头发、工具和服饰细节周围保留足够对比度。
- 必要证据不被主体遮挡。
- 命令、链接、安装步骤和长解释保持 Markdown。

## 验收

透明主体：

- 存在 alpha 通道；
- 四角完全透明；
- 主体覆盖比例合理；
- 深浅背景上没有明显色键边；
- 细线、发丝和轮廓光得到保留；
- 没有意外文字或水印。

最终素材：

- `1200px` GitHub 宽度和窄屏预览；
- 标题与必要标签清楚；
- 裁切和视觉平衡稳定；
- 没有本地图片缺失占位；
- PNG/WebP 体积合理；
- alt text 说明素材作用；
- 即使主体移除，结构仍能解释项目；
- 隐藏文字后，构图和主体关系仍能回到当前项目材料，或诚实地只剩排版留白；
- 整体配色、构图和边界能逐项回到上层视觉合同。

交付时说明生成方式、最终提示词、透明素材、构图源、发布素材以及有意保留的中间文件，然后返回当前 README 子类型。
