"""
PyInstaller 运行时钩子
=====================

在 PyInstaller 打包的 exe 启动时最先执行，
用于设置环境变量和解决 frozen 模式下的常见问题。
"""

import os
import sys

# 设置 matplotlib 配置目录为用户临时目录，避免权限问题
if getattr(sys, 'frozen', False):
    import tempfile
    mpl_config_dir = os.path.join(tempfile.gettempdir(), "mpl_config")
    os.environ.setdefault('MPLCONFIGDIR', mpl_config_dir)
    os.makedirs(mpl_config_dir, exist_ok=True)

    # 设置 matplotlib 字体目录
    exe_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(exe_dir, "_internal")
    matplotlib_data = os.path.join(internal_dir, "matplotlib", "mpl-data")
    if os.path.isdir(matplotlib_data):
        os.environ.setdefault('MATPLOTLIBDATA', matplotlib_data)
