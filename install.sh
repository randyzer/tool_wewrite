#!/usr/bin/env bash
# WeWrite 安装脚本：venv 依赖 + Claude Code skill 符号链接
#
# 1) 在仓库根的 .venv 里创建虚拟环境并安装 requirements。
#    解决 macOS Homebrew Python 3.11+ 的 PEP 668
#    (externally-managed-environment) 限制 —— 该限制会让直接
#    `pip install -r requirements.txt` 报错。
# 2) 把 skills/ 下的主入口 wewrite 与各 wewrite-* 模块逐个
#    符号链接到 ~/.claude/skills/（v2.0 模块化架构；v1.x 的
#    整仓单链接方式已废弃，本脚本会自动替换同名旧链接）。
#
# 用法：  bash install.sh
# 幂等：  可重复运行，已存在的 venv 不会重建，链接原地更新。
#
# 安装后无需手动 activate —— 各 SKILL.md 会自动优先使用
# .venv/bin/python3（见 SKILL.md 的「Python 解释器约定」）。

set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "✗ 找不到 $PYTHON。请先安装 Python 3.11+（macOS: brew install python）。" >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "→ 创建虚拟环境 .venv ..."
  "$PYTHON" -m venv .venv
else
  echo "→ 复用已有的 .venv"
fi

echo "→ 安装依赖到 .venv ..."
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "✓ 依赖已装入 $(pwd)/.venv（无需手动 activate，skill 运行时自动使用）"

# ---- Claude Code skill 链接（可用 CLAUDE_SKILLS_DIR 覆盖目标目录）----
SKILLS_TARGET="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
if [ -d skills ]; then
  mkdir -p "$SKILLS_TARGET"
  linked=0
  for d in skills/wewrite*; do
    [ -f "$d/SKILL.md" ] || continue
    name="$(basename "$d")"
    ln -sfn "$(pwd)/$d" "$SKILLS_TARGET/$name"
    linked=$((linked + 1))
  done
  echo "✓ 已链接 $linked 个 skill 到 $SKILLS_TARGET（主入口 wewrite + 各 wewrite-* 模块）"
  echo "  单独激活示例：/wewrite-topic 选题、/wewrite-review 自检、/wewrite-rewrite 多平台改写"
fi
