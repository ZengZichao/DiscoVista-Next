# 示例数据

本目录用于存放 **1KP 植物数据集**，用于快速试用 DiscoVista-Next 的各种分析模式。

## 仓库内已包含的内容

```
examples/1KP/
├── README              # 原版 DiscoVista 的数据组织说明
└── parameters/         # 参数文件（已收录）
    ├── annotation.txt      # 物种 → 进化支注释
    ├── annotation-1.txt    # 注释文件的另一套划分
    ├── clade-defs.txt      # 进化支（split）定义
    ├── rooting.txt         # 外群与定根定义
    ├── newModel.txt        # 模型条件重排
    ├── newOrders.txt       # 进化支重排
    └── ...
```

## 需要单独获取的内容

基因树、序列数据、GC 含量、占据率、分支统计、相对频率等大体积数据
（解压后约 400 MB、8600 余个文件）不随仓库提供。在项目根目录执行：

```bash
python examples/fetch_data.py
```

脚本会从原版 [DiscoVista](https://github.com/esayyari/DiscoVista) 仓库下载
各数据包的 `tar.gz` 并解压到 `examples/1KP/`：

| 数据包 | 内容 |
|--------|------|
| `genetrees.tar.gz` | 基因树（按支持度过滤的多个版本） |
| `species.tar.gz` | 物种树 |
| `GC.tar.gz` | GC 含量分析数据 |
| `occupancy.tar.gz` | 占据率分析数据 |
| `branchAnalysis.tar.gz` | 分支统计 vs 分支长度数据 |
| `relativeFreq.tar.gz` | 相对频率分析数据 |

## 数据就绪后的样子

```
examples/1KP/
├── parameters/
├── genetrees/
├── species/
├── GC/
├── occupancy/
├── branchAnalysis/
└── relativeFreq/
```

此时在 GUI 中点击「加载示例数据」按钮，或在命令行中按 README 的示例命令运行，
即可复现各分析模式的结果。

> 数据获取后不需要提交到 Git —— `.gitignore` 已排除 `examples/1KP/` 下除
> `parameters/` 与 `README` 之外的全部内容。

## 使用自己的数据

示例数据的目录结构即为 DiscoVista-Next 的输入约定，详见
[使用手册](../docs/zh/user_guide.md) 与 [User Guide](../docs/en/user_guide.md)。
