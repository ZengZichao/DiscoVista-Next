# 安装指南

## 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows / macOS / Linux
- 磁盘空间：约 500MB（依赖）；如需 1KP 示例数据，另加约 400MB

## 安装方式

### 方式一：从源代码安装（推荐开发者）

#### 1. 安装 Python 3

确保系统已安装 Python 3.8+：

```bash
python --version
```

#### 2. 创建虚拟环境

```bash
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

#### 3. 安装 DiscoVista-Next

```bash
# 进入项目目录
cd DiscoVista-Next-项目代码

# 安装依赖和本包
pip install -e .
```

或手动安装依赖：

```bash
pip install -r requirements.txt
```

#### 4. 验证安装

```bash
# 命令行工具
discoVista --help

# GUI 工具
discoVista-gui
```

### 方式二：使用独立 exe 文件（推荐普通用户）

1. 获取 `DiscoVista-Next.exe` 文件
2. 双击运行即可，无需安装 Python 环境
3. exe 文件包含所有依赖（不含示例数据）

### 方式三：构建独立 exe 文件

详见下方"构建 exe 文件"部分。

## 依赖列表

| 包 | 版本要求 | 用途 |
|---|---|---|
| dendropy | >= 4.5.0 | 系统发育树读取与操作 |
| matplotlib | >= 3.5.0 | 数据可视化 |
| pandas | >= 1.3.0 | 数据处理 |
| numpy | >= 1.20.0 | 数值计算 |
| seaborn | >= 0.11.0 | 高级统计绘图 |
| PySide6 | >= 6.4.0 | GUI 框架 |
| qt-material | >= 2.17 | Material Design 主题（26 个内置主题） |
| pyinstaller | >= 5.0 | 构建 exe 文件（可选） |

## 构建 exe 文件

### 前提条件

```bash
pip install pyinstaller
pip install -e .
```

### 方法一：使用构建脚本

```bash
python build_exe.py
```

### 方法二：使用 spec 文件

```bash
pyinstaller DiscoVista-Next.spec
```

### 构建结果

构建完成后，独立 exe 文件位于 `dist/DiscoVista-Next.exe`。

### 注意事项

- exe 文件包含所有依赖，约 200-400MB
- 首次启动可能较慢（解压临时文件）
- 确保 `examples/` 目录存在且包含示例数据
- 构建过程可能需要 5-10 分钟

## 常见安装问题

### 问题：PySide6 安装失败

PySide6 是较大的包，安装可能需要较长时间。建议使用：

```bash
pip install PySide6 --no-cache-dir
```

### 问题：matplotlib 后端错误

如果遇到图形界面相关错误，确保使用 `Agg` 后端（已在代码中设置）。

### 问题：Windows 上命令行工具无法使用

确保 Python Scripts 目录在 PATH 中。或直接使用：

```bash
python -m discovista_next.cli.main [options]
```

### 问题：qt-material 主题不显示

确保 qt-material 已正确安装：

```bash
pip install qt-material --upgrade
```

### 问题：构建 exe 时出现 ModuleNotFoundError

确保所有依赖已安装：

```bash
pip install -r requirements.txt
pip install pyinstaller
```
