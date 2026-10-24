# -*- mode: python ; coding: utf-8 -*-
"""
DiscoVista-Next PyInstaller 打包配置
====================================

用法::

    pyinstaller DiscoVista-Next.spec

所有路径均为相对项目根目录的路径，请在项目根目录下执行。
构建结果输出到 ``dist/DiscoVista-Next/``。
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── 数据文件 ────────────────────────────────────────────────────────
# 图标等资源：打包到 exe 同级（或 _internal）的 resources 目录，
# 与 discovista_next/gui/main.py 中的运行时查找逻辑保持一致。
datas = [
    (os.path.join("discovista_next", "resources"), "resources"),
]

binaries = []
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "matplotlib.backends.backend_agg",
    "matplotlib.backends.backend_pdf",
    "matplotlib.font_manager",
]

for _pkg in ("qt_material", "dendropy"):
    _datas, _binaries, _hiddenimports = collect_all(_pkg)
    datas += _datas
    binaries += _binaries
    hiddenimports += _hiddenimports

# matplotlib 数据文件（字体、样式等）
datas += collect_data_files("matplotlib")

# 排除与 PySide6 冲突或体积过大的非必需模块
excludes = [
    "PyQt5", "PyQt6", "PySide2",
    "IPython", "jedi", "parso", "Cython", "scipy", "lxml",
    "cryptography", "Bio", "simplejson", "wcwidth", "regex",
    "pytz", "pywin32", "win32", "fontTools", "PIL", "_brotli",
]

a = Analysis(
    [os.path.join("discovista_next", "gui", "main.py")],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join("discovista_next", "gui", "runtime_hook.py")],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DiscoVista-Next",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join("discovista_next", "resources", "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DiscoVista-Next",
)
