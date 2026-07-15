"""README 与 CLI 命令清单的同步守卫。

真源 = cli.py 的 _COMMANDS / _TOOLKIT_PASSTHROUGH。新增或改名子命令时
若忘了同步 README，本测试在 CI 直接红——README 漂移无法合入 main。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = str(ROOT / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from wewrite.cli import _COMMANDS, _TOOLKIT_PASSTHROUGH


def test_every_cli_command_documented_in_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    all_commands = [*_COMMANDS, *sorted(_TOOLKIT_PASSTHROUGH)]
    missing = [name for name in all_commands if name not in readme]
    assert not missing, (
        f"README.md 缺少以下 CLI 命令的说明，请同步（通常加在「核心能力」表和「CLI 独立使用」代码块）: {missing}"
    )
