# 许可证实施与验证

这份方法只在许可证选择和范围矩阵已经准确、且用户已经批准实施后使用。`license-governance.md` 中与仓库分类相符的稳定默认已经完成许可证选择，无需另问一次许可证偏好，但它不证明授权权利，也不替代用户对实际写入或远程发布的批准。矩阵是本次任务的实施输入，不是 Skill 的永久事实；不要把账号名、仓库清单、提交 SHA 或一次性判断写回 Skill。

## 1. 方案是唯一实施边界

`scripts/apply_license.py` 接受 schema v2 JSON：

```json
{
  "schema_version": 2,
  "projects": [
    {
      "id": "example",
      "disposition": "apply",
      "reason": "批准矩阵中的简短理由",
      "target": {
        "kind": "local",
        "path": "D:/Projects/example",
        "expected_head": "可选的当前 Git HEAD"
      },
      "project_name": "Example",
      "year": "2026",
      "copyright_holder": "Copyright holder",
      "commit_message": "docs: establish repository licensing",
      "files": [
        {
          "path": "LICENSE",
          "action": "create",
          "source": {"kind": "catalog-license", "id": "MPL-2.0"}
        },
        {
          "path": "NOTICE",
          "action": "create",
          "source": {"kind": "catalog-notice", "id": "MPL-2.0-Notice"}
        },
        {
          "path": "LICENSING.md",
          "action": "create",
          "source": {
            "kind": "text",
            "content": "# Licensing\n\nThe scope map approved by the owner.\n"
          }
        }
      ]
    }
  ]
}
```

GitHub 目标改为：

```json
{
  "kind": "github",
  "repository": "owner/name",
  "expected_visibility": "public",
  "expected_is_fork": false,
  "branch": "真实默认分支",
  "expected_head": "预检得到的完整提交 SHA"
}
```

Fork 目标还必须提供 `"expected_parent": "upstream/name"`。这些字段让实施前重新核对账号矩阵的范围，防止仓库可见性或 Fork 身份变化后继续套用旧方案。

矩阵中明确保留现状的仓库使用 `"disposition": "retain"`，提供 `reason`，且不包含文件动作。这样预演可以证明每个纳入范围的仓库都有结论，而不是静默遗漏。

## 2. 文件动作

只支持两种写入动作：

- `create`：目标必须不存在。
- `replace-preserve`：目标必须存在，方案必须给出 `expected_sha256` 和 `preserve_as`。脚本先把旧文件的原始字节保存到历史路径，再写新文件。

不提供直接覆盖、删除、移动或任意仓库文件编辑。可写路径限制在许可证、版权、NOTICE、第三方声明和 `LICENSING.md` 一类治理文件。README 修改由 README 路径完成，不能借许可证脚本写任意文档。

可用来源：

- `catalog-license`：从正式许可证目录读取并校验源文件哈希。
- `catalog-notice`：从目录读取 MPL、保留所有权等范围通知。
- `gnu-notice`：为 GPL 或 AGPL 明确生成 `only` 或 `or-later` 项目声明。
- `text`：只用于已经展示并批准的 `LICENSING.md`、第三方声明或历史说明。

每项来源在预演中显示源标识、渲染后 SHA-256、字节数和首行。预演内容和实际写入内容来自同一渲染结果。

## 3. 全量预检

任何写入前先预检整个方案：

1. 所有项目 ID、目标仓库和输出路径唯一。
2. 本地目录存在；GitHub 使用当前已认证的 `gh`，仓库可见性、Fork 身份与上游、分支和 `expected_head` 全部匹配。
3. `create` 目标不存在。
4. `replace-preserve` 的当前字节哈希匹配，历史路径不存在。
5. 目录正式文本哈希匹配，模板字段全部解析。
6. Fork、第三方内容或待确认项目没有被错误放入 `apply`。

默认命令只预演：

```text
python scripts/apply_license.py --plan plan.json
```

只有全部预检通过，才允许：

```text
python scripts/apply_license.py --plan plan.json --write
python scripts/apply_license.py --plan plan.json --publish
```

`--write` 只接受本地实施项目，`--publish` 只接受 GitHub 实施项目。两者不混用，以免一次命令模糊本地和公开写入权限。

## 4. 原子边界与历史许可证

一个 GitHub 仓库的所有文件通过一个 Git tree 和一个 commit 更新，再以非强制方式移动目标分支引用，因此单仓库内是一个提交。账号下多个仓库无法组成全局事务：发布中途失败时，保留已经公开的真实结果，报告成功、失败和未开始项目，不删除或回滚公开提交。

替换已有许可证时，历史文件必须逐字节保留。范围说明同时记录：

- 历史许可证适用到哪个提交；
- 当前许可证从哪个提交开始；
- 旧版本已经获得的权利继续有效；
- 哪些第三方或 Fork 内容不受新许可证覆盖。

## 5. 验证

写入和发布会立即验证，也可以独立运行：

```text
python scripts/apply_license.py --plan plan.json --verify
```

本地验证读取真实文件；远程验证读取目标分支的 Git tree。检查渲染文件 SHA-256、历史副本哈希、分支 HEAD，以及 GitHub 许可证检测结果。最终报告区分：

- `dry-run`：只证明方案当前可实施；
- `written`：本地文件已经写入并读取验证；
- `published`：远程提交已经创建、分支已经更新并读取验证；
- `verified`：当前状态符合方案，但本次没有写入。

GitHub 的许可证检测是消费者信号，不是权利结论。混合授权、多个根级许可证或 CC BY-NC-SA 等非开源内容许可可能显示 `Other`；以实际文件和范围说明为准。
