# Changelog

本文件记录 DiscoVista-Next 的版本变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-10-24

首个发布版本。

### 功能

- 6 种分析模式：物种树不一致性（模式 0）、基因树不一致性（模式 1）、
  GC 含量（模式 2）、占据率（模式 3）、分支统计 vs 分支长度（模式 4）、
  相对频率（模式 5）
- 基于 qt-material 的图形用户界面，内置 26 个颜色主题
- 中英文界面切换
- 命令行接口，兼容原 DiscoVista 的参数格式
- 基于 matplotlib + seaborn 的可视化
- PyInstaller 独立可执行文件打包支持
- 1KP 植物数据集的参数文件与示例说明
- 中英文文档（安装、使用、开发、API、FAQ）

### 说明

- 纯 Python 3 实现，不依赖 R 语言及其扩展包
- 树操作基于 dendropy，参数解析基于 argparse
