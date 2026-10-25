#!/usr/bin/env python3
"""
DiscoVista-Next 打包入口
========================

所有元数据（名称、版本、依赖、入口点、URL 等）都定义在 ``pyproject.toml``，
本文件只保留给仍以 ``python setup.py ...`` 方式调用的旧工具链使用。

::

    pip install -e .      # 开发模式安装
    python -m build       # 构建 sdist + wheel
"""

from setuptools import setup

setup()
