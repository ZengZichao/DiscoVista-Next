#!/usr/bin/env python3
"""
DiscoVista-Next 安装配置
========================

::

    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discovista-next",
    version="0.1.0",
    author="DiscoVista-Next Team",
    description=(
        "DiscoVista-Next: Python 3 rewrite of DiscoVista - "
        "Phylogenetic discordance visualization & analysis tool"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "discovista_next": [
            "resources/*.png",
            "resources/*.ico",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "dendropy>=4.5.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "seaborn>=0.11.0",
        "PySide6>=6.4.0",
        "qt-material>=2.17",
    ],
    entry_points={
        "console_scripts": [
            "discoVista=discovista_next.cli.main:cli",
        ],
        "gui_scripts": [
            "discoVista-gui=discovista_next.gui.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
