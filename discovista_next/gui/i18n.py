"""
国际化 (i18n) 模块
==================

支持中英文界面切换。所有 GUI 文本通过 ``tr()`` 函数获取，
语言切换时自动更新所有界面文本。
"""

from typing import Dict

# 语言常量
LANG_ZH = "zh"
LANG_EN = "en"

# 当前语言
_current_lang = LANG_ZH

# 翻译字典
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ---------- 窗口标题 ----------
    "app_title": {
        "zh": "DiscoVista-Next 系统发育不一致性分析工具",
        "en": "DiscoVista-Next Phylogenetic Discordance Analysis",
    },
    # ---------- 菜单栏 ----------
    "menu_file": {"zh": "文件(&F)", "en": "&File"},
    "menu_file_open": {"zh": "打开数据目录", "en": "Open Data Directory"},
    "menu_file_save": {"zh": "保存结果", "en": "Save Results"},
    "menu_file_quit": {"zh": "退出", "en": "Quit"},
    "menu_view": {"zh": "视图(&V)", "en": "&View"},
    "menu_view_theme": {"zh": "主题", "en": "Theme"},
    "menu_view_dark_themes": {"zh": "暗色主题", "en": "Dark Themes"},
    "menu_view_light_themes": {"zh": "亮色主题", "en": "Light Themes"},
    "menu_view_light": {"zh": "白天模式", "en": "Light Mode"},
    "menu_view_dark": {"zh": "黑夜模式", "en": "Dark Mode"},
    "menu_language": {"zh": "语言(&L)", "en": "&Language"},
    "menu_lang_zh": {"zh": "中文", "en": "Chinese"},
    "menu_lang_en": {"zh": "英文", "en": "English"},
    "menu_help": {"zh": "帮助(&H)", "en": "&Help"},
    "menu_help_about": {"zh": "关于", "en": "About"},
    # ---------- 分析模式 ----------
    "mode_group": {"zh": "分析模式", "en": "Analysis Mode"},
    "mode_0": {"zh": "物种树不一致性分析", "en": "Species Tree Discordance"},
    "mode_1": {"zh": "基因树不一致性分析", "en": "Gene Tree Discordance"},
    "mode_2": {"zh": "GC 含量分析", "en": "GC Content Analysis"},
    "mode_3": {"zh": "占据率分析", "en": "Occupancy Analysis"},
    "mode_4": {"zh": "分支统计 vs 分支长度", "en": "Branch Support vs Branch Length"},
    "mode_5": {"zh": "相对频率分析", "en": "Relative Frequency Analysis"},
    # ---------- 参数设置 ----------
    "param_group": {"zh": "参数设置", "en": "Parameters"},
    "param_data_path": {"zh": "数据目录路径:", "en": "Data Path:"},
    "param_browse": {"zh": "浏览...", "en": "Browse..."},
    "param_annotation": {"zh": "注释文件:", "en": "Annotation File:"},
    "param_clades": {"zh": "进化支定义文件:", "en": "Clade Definition File:"},
    "param_root": {"zh": "根定义文件:", "en": "Rooting File:"},
    "param_threshold": {"zh": "自展阈值:", "en": "Bootstrap Threshold:"},
    "param_output": {"zh": "输出目录:", "en": "Output Directory:"},
    "param_model_cond": {"zh": "模型条件:", "en": "Model Condition:"},
    "param_new_model": {"zh": "模型重排文件:", "en": "Model Reorder File:"},
    "param_new_order": {"zh": "进化支重排文件:", "en": "Clade Reorder File:"},
    "param_missing": {"zh": "部分缺失视为完整", "en": "Treat partial missing as complete"},
    "param_outgroup": {"zh": "外群名称:", "en": "Outgroup:"},
    # ---------- 绘图显示面板 ----------
    "plot_group": {"zh": "绘图显示", "en": "Plot Display"},
    "plot_no_images": {
        "zh": "暂无图像。运行分析后将在此显示生成的图形。",
        "en": "No images yet. Plots will be displayed here after analysis.",
    },
    "plot_prev": {"zh": "上一张", "en": "Previous"},
    "plot_next": {"zh": "下一张", "en": "Next"},
    "plot_open": {"zh": "在外部打开", "en": "Open Externally"},
    "plot_refresh": {"zh": "刷新", "en": "Refresh"},
    "plot_zoom_in": {"zh": "放大", "en": "Zoom In"},
    "plot_zoom_out": {"zh": "缩小", "en": "Zoom Out"},
    "plot_zoom_fit": {"zh": "适应窗口", "en": "Fit to Window"},
    "plot_status": {"zh": "图像 {current}/{total}: {name}", "en": "Image {current}/{total}: {name}"},
    "plot_no_plots": {
        "zh": "未找到任何图像文件。",
        "en": "No plot files found.",
    },
    # ---------- 操作按钮 ----------
    "btn_run": {"zh": "运行分析", "en": "Run Analysis"},
    "btn_stop": {"zh": "停止", "en": "Stop"},
    "btn_clear": {"zh": "清空", "en": "Clear"},
    "btn_load_example": {"zh": "加载示例数据", "en": "Load Example Data"},
    # ---------- 日志输出 ----------
    "log_group": {"zh": "运行日志", "en": "Execution Log"},
    # ---------- 状态栏 ----------
    "status_ready": {"zh": "就绪", "en": "Ready"},
    "status_running": {"zh": "运行中...", "en": "Running..."},
    "status_done": {"zh": "分析完成", "en": "Analysis complete"},
    "status_error": {"zh": "分析出错", "en": "Analysis error"},
    # ---------- 对话框 ----------
    "msg_select_mode": {"zh": "请选择分析模式", "en": "Please select an analysis mode"},
    "msg_select_path": {"zh": "请输入数据目录路径", "en": "Please enter the data path"},
    "msg_select_output": {"zh": "请输入输出目录路径", "en": "Please enter the output directory"},
    "msg_running": {"zh": "分析正在运行中，请等待完成...", "en": "Analysis is running, please wait..."},
    "msg_success": {"zh": "分析完成！结果已保存到: ", "en": "Analysis complete! Results saved to: "},
    "msg_failed": {"zh": "分析失败，请查看日志", "en": "Analysis failed, please check the log"},
    "msg_no_example": {
        "zh": "未找到示例数据目录，请确保已安装示例数据。",
        "en": "Example data directory not found. Please ensure example data is installed.",
    },
    "msg_example_loaded": {
        "zh": "示例数据已加载，请根据需要调整参数后运行分析。",
        "en": "Example data loaded. Please adjust parameters as needed and run analysis.",
    },
    "msg_about_title": {"zh": "关于 DiscoVista-Next", "en": "About DiscoVista-Next"},
    "msg_about_text": {
        "zh": (
            "<h3>DiscoVista-Next v0.1.0</h3>"
            "<p>系统发育不一致性可视化与分析工具</p>"
            "<p>原 DiscoVista 的 Python 3 全面重写版</p>"
            "<p>作者: DiscoVista-Next 团队</p>"
            "<p>许可证: GPL-3.0</p>"
        ),
        "en": (
            "<h3>DiscoVista-Next v0.1.0</h3>"
            "<p>Phylogenetic discordance visualization & analysis tool</p>"
            "<p>A complete Python 3 rewrite of DiscoVista</p>"
            "<p>Author: DiscoVista-Next Team</p>"
            "<p>License: GPL-3.0</p>"
        ),
    },
}


def set_language(lang: str) -> None:
    """设置当前语言。"""
    global _current_lang
    _current_lang = lang


def get_language() -> str:
    """获取当前语言。"""
    return _current_lang


def tr(key: str) -> str:
    """获取翻译文本。

    Parameters
    ----------
    key : str
        翻译键。

    Returns
    -------
    str
        当前语言对应的文本。
    """
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(_current_lang, entry.get(LANG_EN, key))
