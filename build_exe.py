#!/usr/bin/env python3
"""
DiscoVista-Next PyInstaller 构建脚本
====================================

使用 PyInstaller 构建 exe 文件（onedir 模式，非自包含）。

exe 文件依赖外部的 examples/ 和 resources/ 目录，
因此需要将 exe 与这些目录放在一起分发。

用法::

    python build_exe.py

构建结果将出现在 ``dist/DiscoVista-Next/`` 目录下。
"""

import os
import sys
import subprocess


def build():
    """执行 PyInstaller 构建。"""
    # 获取项目根目录
    root = os.path.dirname(os.path.abspath(__file__))

    # 图标文件路径（.ico）
    icon_path = os.path.join(root, "discovista_next", "resources", "app_icon.ico")

    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name", "DiscoVista-Next",
        "--windowed",       # 不显示控制台窗口
        # 不使用 --onefile，使用默认的 onedir 模式
        # 添加数据文件：qt_material 主题和字体
        "--collect-all", "qt_material",
        # 收集 matplotlib 数据文件（字体、样式等）
        "--collect-data", "matplotlib",
        # 添加资源文件（图标等）
        "--add-data", os.path.join(root, "discovista_next", "resources") + os.pathsep + "resources",
        # 运行时钩子
        "--runtime-hook", os.path.join(root, "discovista_next", "gui", "runtime_hook.py"),
        # 隐式导入
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtGui",
        # matplotlib 后端
        "--hidden-import", "matplotlib.backends.backend_agg",
        "--hidden-import", "matplotlib.backends.backend_pdf",
        "--hidden-import", "matplotlib.font_manager",
        # dendropy
        "--collect-all", "dendropy",
        # 排除冲突的 Qt 绑定
        "--exclude-module", "PyQt5",
        "--exclude-module", "PyQt6",
        "--exclude-module", "PySide2",
        # 排除不需要的大型库以加快启动速度
        "--exclude-module", "IPython",
        "--exclude-module", "jedi",
        "--exclude-module", "parso",
        "--exclude-module", "Cython",
        "--exclude-module", "scipy",
        "--exclude-module", "lxml",
        "--exclude-module", "cryptography",
        "--exclude-module", "Bio",
        "--exclude-module", "simplejson",
        "--exclude-module", "wcwidth",
        "--exclude-module", "regex",
        "--exclude-module", "pytz",
        "--exclude-module", "pywin32",
        "--exclude-module", "win32",
        "--exclude-module", "fontTools",
        "--exclude-module", "PIL",
        "--exclude-module", "_brotli",
        # 入口脚本
        os.path.join(root, "discovista_next", "gui", "main.py"),
    ]

    # 添加图标（如果 .ico 文件存在）
    if os.path.isfile(icon_path):
        cmd.extend(["--icon", icon_path])
    else:
        print(f"WARNING: Icon file not found: {icon_path}")
        print("  Will generate it from PNG...")

    print("=" * 60)
    print("DiscoVista-Next PyInstaller Build (onedir mode)")
    print("=" * 60)
    print(f"Project root: {root}")
    print(f"Icon: {icon_path}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    # 如果没有 .ico 文件，先从 PNG 生成
    if not os.path.isfile(icon_path):
        _generate_ico_from_png(
            os.path.join(root, "discovista_next", "resources", "app_icon_256.png"),
            icon_path,
        )

    # 执行构建
    result = subprocess.run(cmd, cwd=root)
    if result.returncode != 0:
        print("\nBuild FAILED!")
        sys.exit(1)
    else:
        print("\nBuild SUCCESS!")
        dist_dir = os.path.join(root, 'dist', 'DiscoVista-Next')
        print(f"Output: {os.path.join(dist_dir, 'DiscoVista-Next.exe')}")

        # 后处理：复制 examples 目录到 exe 同级目录
        _post_build_copy(root, dist_dir)

        print("\nNOTE: The exe depends on 'examples/' and 'resources/' directories.")
        print("      Make sure to distribute them alongside the exe.")


def _post_build_copy(root, dist_dir):
    """构建后复制 examples 目录到 dist 目录（exe 同级）。"""
    import shutil

    # 复制 examples 目录
    src_examples = os.path.join(root, "examples")
    dst_examples = os.path.join(dist_dir, "examples")
    if os.path.isdir(src_examples):
        if os.path.isdir(dst_examples):
            shutil.rmtree(dst_examples)
        shutil.copytree(src_examples, dst_examples)
        print(f"Copied: examples -> {dst_examples}")
    else:
        print("WARNING: examples directory not found in project root!")

    # resources 目录：PyInstaller 已将 resources 打包到 _internal/resources，
    # 但我们也复制一份到 exe 同级目录，确保 _icon_path 可以找到
    src_resources = os.path.join(root, "discovista_next", "resources")
    dst_resources = os.path.join(dist_dir, "resources")
    if os.path.isdir(src_resources):
        if os.path.isdir(dst_resources):
            shutil.rmtree(dst_resources)
        shutil.copytree(src_resources, dst_resources)
        print(f"Copied: resources -> {dst_resources}")

    # 同时将 examples 复制到 _internal 目录，供 _MEIPASS 模式查找
    internal_dir = os.path.join(dist_dir, "_internal")
    if os.path.isdir(internal_dir):
        internal_examples = os.path.join(internal_dir, "examples")
        if not os.path.isdir(internal_examples):
            try:
                shutil.copytree(src_examples, internal_examples)
                print(f"Copied: examples -> {internal_examples}")
            except Exception:
                pass


def _generate_ico_from_png(png_path, ico_path):
    """从 PNG 文件生成 ICO 图标文件。"""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
        from PIL import Image

    img = Image.open(png_path)
    # 保存为 .ico，包含多种尺寸
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"Generated ICO file: {ico_path}")


if __name__ == "__main__":
    build()
