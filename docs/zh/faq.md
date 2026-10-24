# 常见问题解答 (FAQ)

## 1. DiscoVista-Next 与原版 DiscoVista 有何区别？

DiscoVista-Next 是原版 DiscoVista 的 Python 3 全面重写版。主要区别：

- **无 R 依赖**：原版需要安装 R 及多个扩展包，本版完全使用 Python 实现
- **Python 3**：原版部分代码使用 Python 2，本版完全使用 Python 3
- **GUI**：原版仅有命令行界面，本版新增了基于 qt-material 的图形界面（26 个主题）
- **国际化**：本版支持中英文界面切换
- **独立 exe**：本版可构建自包含的独立可执行文件
- **示例数据**：1KP 参数文件随仓库提供，大体积数据文件（约 400MB）需按 `examples/README.md` 的说明单独获取

## 2. 是否可以继续使用原版的数据文件？

是的。DiscoVista-Next 保持了与原版完全兼容的数据目录结构和输入文件格式。

## 3. 相对频率分析（模式 5）需要什么前置步骤？

模式 5 需要先使用 ASTRAL（DiscoVista 分支）运行基因树，生成 `freqQuad.csv` 文件。然后将该文件放在数据目录中。

## 4. 如何选择正确的自展阈值？

- 物种树分析：通常使用 95（自展支持）或 0.95（本地后验概率）
- 基因树分析：通常使用 75

## 5. GUI 启动时出现黑屏或白屏怎么办？

这通常是 qt-material 资源加载问题。尝试：

```bash
pip install --upgrade qt-material
```

## 6. 如何在没有图形界面的服务器上运行？

DiscoVista-Next 的可视化模块使用 matplotlib 的 `Agg` 后端，不需要图形界面即可生成 PDF 图表。只需使用命令行模式：

```bash
discoVista -m 0 -c clade-defs.txt -p data/ -t 95 -o results/
```

## 7. 输出目录中只有 CSV 文件没有 PDF 图表怎么办？

请检查：
1. matplotlib 和 seaborn 是否正确安装
2. 日志中是否有绘图相关错误
3. 确保输出目录有写权限

## 8. 有多少个颜色主题可选？

共有 26 个内置 qt-material 颜色主题（9 个暗色 + 17 个亮色）。可通过界面下拉菜单或菜单栏切换。

## 9. exe 文件很大，能否减小体积？

exe 文件包含所有依赖，但不包含示例数据。如需使用"加载示例数据"功能，请将 1KP 数据集放在 exe 同级的 `examples/` 目录下。

## 10. exe 文件首次启动很慢？

这是正常现象。PyInstaller 在首次启动时需要解压临时文件，后续启动会更快。

## 11. 如何构建独立 exe 文件？

```bash
pip install pyinstaller
python build_exe.py
# 或
pyinstaller DiscoVista-Next.spec
```

构建结果位于 `dist/DiscoVista-Next.exe`。

## 12. "加载示例数据"按钮提示找不到示例数据？

请确保 `examples/1KP/` 目录存在且包含以下子目录：
- `parameters/` — 参数文件
- `species/` — 物种树数据
- 其他数据目录

如使用独立 exe，请将示例数据放在 exe 同级的 `examples/` 目录下。

## 13. 如何报告 Bug？

请在项目仓库中创建 Issue，包含：
- 操作系统和 Python 版本
- 完整的命令行参数
- 错误日志输出
