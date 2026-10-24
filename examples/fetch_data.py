#!/usr/bin/env python3
"""
下载 1KP 示例数据集
===================

从原版 DiscoVista 仓库下载示例数据包并解压到 ``examples/1KP/``。
仓库本身只收录了参数文件，基因树、序列、GC 含量等大体积数据需要
用本脚本单独获取（解压后约 400 MB）。

用法::

    python examples/fetch_data.py            # 下载缺失的数据
    python examples/fetch_data.py --force    # 重新下载全部数据

仅使用标准库，无需额外依赖。
"""

import argparse
import os
import sys
import tarfile
import urllib.error
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/esayyari/DiscoVista/master/example/1KP"

# 数据包名称 → 解压后的顶层目录（同名）
PACKAGES = [
    "genetrees",
    "species",
    "GC",
    "occupancy",
    "branchAnalysis",
    "relativeFreq",
]

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(HERE, "1KP")


def download(package):
    """下载单个数据包，返回本地 tar.gz 路径。"""
    url = f"{BASE_URL}/{package}.tar.gz"
    archive = os.path.join(TARGET_DIR, f"{package}.tar.gz")

    print(f"  下载 {package}.tar.gz ...", end="", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    with open(archive, "wb") as fh:
        fh.write(data)
    print(f" {len(data) / 1024 / 1024:.1f} MB")
    return archive


def extract(archive):
    """解压 tar.gz 到 examples/1KP/。"""
    with tarfile.open(archive, "r:gz") as tar:
        try:
            # Python 3.12+：用 data 过滤器避免路径穿越
            tar.extractall(TARGET_DIR, filter="data")
        except TypeError:
            tar.extractall(TARGET_DIR)


def main():
    parser = argparse.ArgumentParser(
        description="下载 1KP 示例数据集到 examples/1KP/"
    )
    parser.add_argument(
        "--force", action="store_true", help="即使目录已存在也重新下载"
    )
    parser.add_argument(
        "--keep-archive", action="store_true", help="解压后保留 tar.gz 文件"
    )
    args = parser.parse_args()

    os.makedirs(TARGET_DIR, exist_ok=True)

    pending = [p for p in PACKAGES if args.force or not os.path.isdir(
        os.path.join(TARGET_DIR, p))]

    if not pending:
        print("示例数据已就绪，无需下载。使用 --force 可重新下载。")
        return 0

    print(f"下载 {len(pending)} 个数据包到 {TARGET_DIR}")
    for package in pending:
        try:
            archive = download(package)
            extract(archive)
            if not args.keep_archive:
                os.remove(archive)
        except (urllib.error.URLError, OSError, tarfile.TarError) as exc:
            print(f"\n下载或解压 {package} 失败：{exc}", file=sys.stderr)
            return 1

    print("\n完成。现在可以在 GUI 中点击「加载示例数据」，")
    print("或按 README 的命令行示例运行分析。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
