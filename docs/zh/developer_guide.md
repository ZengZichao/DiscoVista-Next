# 开发者文档

## 1. 项目架构

```
DiscoVista-Next-项目代码/
├── discovista_next/          # 主包
│   ├── __init__.py           # 包初始化、版本信息、模式常量
│   ├── core/                 # 核心分析模块
│   │   ├── __init__.py
│   │   ├── config.py         # 配置与选项处理 (替代 reader.py)
│   │   ├── analyzer.py       # 分析控制器 (替代 analyze.py)
│   │   ├── tree_tools.py     # 树操作工具 (替代 tools.py)
│   │   ├── find_clades.py    # 进化支单系性检测 (替代 find_clades2.py)
│   │   ├── gc_stats.py       # GC 含量统计 (替代 gc_stats.py)
│   │   ├── occupancy.py      # 占据率分析 (替代 occupancy.R 数据处理)
│   │   └── relative_freq.py  # 相对频率分析 (替代 map_names.py 等)
│   ├── viz/                  # 可视化模块 (替代所有 R ggplot2 代码)
│   │   ├── __init__.py
│   │   ├── depict_clades.py  # 进化支热图/条形图 (替代 main_depict_clades.R)
│   │   ├── gc_plot.py        # GC 可视化 (替代 plot.gc.R)
│   │   ├── occupancy_plot.py # 占据率可视化 (替代 occupancy.R 绘图)
│   │   ├── branch_stat_plot.py # 分支统计可视化 (替代 branchStat.R)
│   │   ├── tree_plot.py      # 树绘制 (替代 plotTree.R)
│   │   └── relative_freq_plot.py # 相对频率可视化
│   ├── cli/                  # 命令行接口
│   │   ├── __init__.py
│   │   └── main.py           # CLI 入口 (替代 discoVista.py)
│   └── gui/                  # 图形用户界面
│       ├── __init__.py
│       ├── i18n.py           # 国际化（中英文）
│       └── main.py           # GUI 主窗口
├── docs/                     # 文档
│   ├── zh/                   # 中文文档
│   └── en/                   # 英文文档
├── examples/                 # 示例数据
├── setup.py                  # 安装配置
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

## 2. 模块对应关系

### 2.1 R → Python 映射

| 原 R 脚本 | Python 替代 | 说明 |
|-----------|-------------|------|
| `reader.R` | `core/config.py` | 选项解析 |
| `depict_clades.R` | `viz/depict_clades.py` | 进化支绘图入口 |
| `main_depict_clades.R` | `viz/depict_clades.py` | 核心绘图函数 |
| `plot.gc.R` | `viz/gc_plot.py` | GC 含量绘图 |
| `occupancy.R` | `core/occupancy.py` + `viz/occupancy_plot.py` | 占据率分析+绘图 |
| `branchStat.R` | `viz/branch_stat_plot.py` | 分支统计绘图 |
| `plotTree.R` | `viz/tree_plot.py` | 树绘制 |

### 2.2 Python 2 → Python 3 映射

| 原 Python 2 模块 | Python 3 替代 | 说明 |
|-----------------|---------------|------|
| `discoVista.py` | `cli/main.py` | 主入口 |
| `analyze.py` | `core/analyzer.py` | 分析控制器 |
| `reader.py` | `core/config.py` | 选项处理 |
| `tools.py` | `core/tree_tools.py` | 树操作工具 |
| `find_clades2.py` | `core/find_clades.py` | 进化支分析 |
| `gc_stats.py` | `core/gc_stats.py` | GC 统计 |
| `map_names.py` | `core/relative_freq.py` | 相对频率 |
| `generate_clade-defs.py` | (保留，已更新为 Python 3) | 进化支定义生成 |

### 2.3 Shell 脚本替代

| 原 Shell 脚本 | Python 替代 | 说明 |
|--------------|-------------|------|
| `pos-for-hyp.sh` | `core/relative_freq.py` 中的 `run()` | 相对频率流程 |
| `branchLengthCompare.sh` | (集成到 `tree_tools.py`) | 分支长度比较 |
| `maxOrAvgDistances.sh` | (集成到 `tree_tools.py`) | 距离计算 |

## 3. 核心设计

### 3.1 配置管理

`Options` 数据类封装所有运行参数，通过 `from_args()` 工厂方法从命令行构建。

```python
from discovista_next.core import Options

opt = Options.from_args(["-m", "0", "-p", "data/", "-c", "clades.txt",
                          "-t", "95", "-o", "results/"])
```

### 3.2 分析流程

`Analyzer` 类根据 `mode` 字段分发到对应的分析方法：

```python
from discovista_next.core import Analyzer

analyzer = Analyzer(opt)
analyzer.analyze()  # 自动选择正确的分析模式
```

### 3.3 可视化架构

所有可视化使用 matplotlib 的 `Agg` 后端（非交互式），确保在无显示器的服务器环境中也能正常工作。每个可视化类负责一种图表类型。

### 3.4 GUI 架构

- **i18n.py**：集中管理所有界面文本翻译
- **main.py**：主窗口，包含菜单栏、参数输入区域、日志输出和后台工作线程
- **AnalysisWorker**：继承 `QObject`，在 `QThread` 中执行分析避免阻塞 UI

## 4. 扩展开发

### 4.1 添加新的分析模式

1. 在 `__init__.py` 中添加模式常量
2. 在 `core/` 中创建新的分析模块
3. 在 `core/analyzer.py` 中添加对应的分发逻辑
4. 在 `viz/` 中创建对应的可视化模块
5. 更新 GUI 的模式下拉框

### 4.2 添加新的可视化

```python
from discovista_next.viz import DepictClades

# 自定义可视化
class MyPlot:
    def __init__(self, out_dir):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def plot(self, data):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        # ... 绘图代码 ...
        fig.savefig(os.path.join(self.out_dir, "my_plot.pdf"))
        plt.close(fig)
```

### 4.3 添加新的界面语言

在 `gui/i18n.py` 的 `TRANSLATIONS` 字典中添加新语言的映射，并在语言菜单中添加选项。

## 5. 测试

```bash
# 运行基本测试
python -m discovista_next.cli.main --help

# 使用示例数据测试
discoVista -m 0 -c examples/clade-defs.txt -p examples/species/ \
    -t 95 -o examples/results/
```

## 6. 贡献指南

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -am 'Add new feature'`)
4. 推送到分支 (`git push origin feature/new-feature`)
5. 创建 Pull Request
