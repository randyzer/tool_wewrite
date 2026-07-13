---
name: wewrite-learn
description: |
  WeWrite 自学习模块：从用户的人工修改中学习写作偏好（playbook 飞轮）、导入范文建风格库、
  从公众号文章学习排版主题。
  触发关键词：学习我的修改、我改了学习一下、导入范文、学习这篇文章、查看范文库、
  学习排版、学排版。
  不应被通用的"学习"、"总结这篇文章"触发——需要公众号/WeWrite 上下文。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - WebFetch
---

# wewrite-learn — 自学习（改稿飞轮 / 范文库 / 排版学习）

<!-- wewrite:standalone-start -->
## 运行约定

- **{root}** = `{skill_dir}/root`（本目录内指向 WeWrite 仓库根的符号链接）。
- **Python**：优先 venv——`PY="{root}/.venv/bin/python3"; [ -x "$PY" ] || PY="python3"`；下文 `python3` 均指 `$PY`。
- **`读取: <路径>`** = 用文件读取工具真实读完该文件再继续，不是注释。
- **references/ 文档中的 `{skill_dir}`** 一律指 `{root}`（历史约定，指仓库根）。
<!-- wewrite:standalone-end -->

## 子功能分发

| 用户说 | 动作 |
|--------|------|
| 学习我的修改 / 我改了，学习一下 | `读取: {root}/references/learn-edits.md`，按其流程执行。支持本地 markdown 修改与微信草稿箱同步（`python3 {root}/scripts/learn_edits.py --from-wechat`） |
| 学习排版 / 学排版 + URL | `python3 {root}/scripts/learn_theme.py <url> --name <name>`，提取后提示用户设置 style.yaml 的 theme 字段 |
| 学习这篇文章 / 导入范文 + URL | `python3 {root}/scripts/fetch_article.py <url> -o /tmp/article.md && python3 {root}/scripts/extract_exemplar.py /tmp/article.md -s <账号名>` |
| 导入范文 + 本地文件 | `python3 {root}/scripts/extract_exemplar.py <文件路径>`（多文件可批量） |
| 查看范文库 | `python3 {root}/scripts/extract_exemplar.py --list` |

**范文库的用途**：exemplars 会在写作模块（wewrite-write）按框架类型注入初稿 prompt，
是 SICO 式 few-shot 的来源。导入完成后告知用户库里现有多少篇、覆盖哪些 category。

**改稿飞轮的价值**：每次学习让下一篇初稿更接近用户风格。learn-edits.md 的
confidence 分级（≥5 硬约束 / <5 软参考 / <2 淘汰）决定规则在写作时的效力。
