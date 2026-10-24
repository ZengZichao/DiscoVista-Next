#!/usr/bin/env python3
"""
DiscoVista-Next 命令行接口
===========================

替代原 ``discoVista.py`` 主入口脚本。

用法 / Usage::

    python -m discovista_next.cli.main [options]

    discoVista [options]
"""

import sys
import traceback

from ..core.config import Options
from ..core.analyzer import Analyzer


def cli(argv=None) -> int:
    """命令行主函数。

    Parameters
    ----------
    argv : list[str] or None
        命令行参数。为 None 时使用 ``sys.argv``。

    Returns
    -------
    int
        退出码 (0=成功, 1=失败)。
    """
    try:
        opt = Options.from_args(argv)
        analyzer = Analyzer(opt)
        analyzer.analyze()
        return 0
    except ValueError:
        print("Analysis failed!")
        traceback.print_exc()
        return 1
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1


if __name__ == "__main__":
    sys.setrecursionlimit(50000)
    sys.exit(cli())
