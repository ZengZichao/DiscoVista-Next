#!/usr/bin/env python3
"""
DiscoVista-Next GUI 主窗口
===========================

基于 PySide6 + qt-material 构建的图形用户界面。
支持中英文界面切换和所有 qt-material 内置颜色主题（26 个主题）。
包含绘图显示面板，分析完成后自动展示生成的图形。

启动::

    python -m discovista_next.gui.main
    discoVista-gui
"""

import sys
import os
import glob
import threading
import traceback

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QStatusBar, QMenu, QMenuBar, QSpinBox, QDoubleSpinBox,
    QScrollArea, QSizePolicy, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QStackedWidget,
)
from PySide6.QtCore import Qt, Signal, QObject, QThread, QSize, QTimer
from PySide6.QtGui import (
    QAction, QActionGroup, QPixmap, QImage, QPainter, QIcon,
    QWheelEvent, QKeyEvent,
)

from qt_material import apply_stylesheet, list_themes

from discovista_next.gui.i18n import (
    set_language, get_language, tr, LANG_ZH, LANG_EN,
    TRANSLATIONS,
)
from discovista_next.core.config import Options
from discovista_next.core.analyzer import Analyzer
from discovista_next import ALL_MODES


# ======================================================================
# 图标资源路径
# ======================================================================
def _icon_path(name, size=24):
    """获取 resources 目录中指定名称和尺寸的图标路径。

    在 frozen 模式下，优先从 exe 所在目录的 resources 子目录查找。
    """
    candidates = []

    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        # PyInstaller 6.x 会将数据放在 _internal/ 下，旧版放在 exe 同级目录
        search_dirs = [
            os.path.join(exe_dir, "resources"),
            os.path.join(exe_dir, "_internal", "resources"),
        ]
        for res_dir in search_dirs:
            candidates.extend([
                os.path.join(res_dir, f"{name}_{size}.png"),
                os.path.join(res_dir, f"{name}_24.png"),
                os.path.join(res_dir, f"{name}_48.png"),
                os.path.join(res_dir, f"{name}_256.png"),
            ])
    else:
        res_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
        candidates.extend([
            os.path.join(res_dir, f"{name}_{size}.png"),
            os.path.join(res_dir, f"{name}_24.png"),
        ])

    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _load_icon(name, size=24):
    """加载指定名称的 QIcon，失败时返回空图标。"""
    path = _icon_path(name, size)
    if path:
        return QIcon(path)
    return QIcon()


# ======================================================================
# 工具函数：获取所有 qt-material 主题并分组
# ======================================================================
def get_all_themes():
    """获取所有 qt-material 内置主题，分为暗色和亮色两组。"""
    all_themes = list_themes()
    dark_themes = []
    light_themes = []
    for t in all_themes:
        name = t.replace(".xml", "")
        if name.startswith("dark_"):
            display = name.replace("dark_", "").capitalize()
            dark_themes.append((t, f"Dark - {display}"))
        elif name.startswith("light_"):
            display = name.replace("light_", "").capitalize()
            light_themes.append((t, f"Light - {display}"))
        else:
            dark_themes.append((t, name.capitalize()))
    return dark_themes, light_themes


def get_theme_color(theme_file):
    """从主题 XML 文件中提取主色调，用于预览。"""
    try:
        from xml.dom.minidom import parse
        theme_path = os.path.join(
            os.path.dirname(os.path.abspath(
                __import__("qt_material").__file__)),
            "themes", theme_file
        )
        if not os.path.exists(theme_path):
            return None
        document = parse(theme_path)
        for child in document.getElementsByTagName("color"):
            if child.getAttribute("name") == "primaryColor":
                return child.firstChild.nodeValue
    except Exception:
        pass
    return None


# ======================================================================
# 工作线程
# ======================================================================
class AnalysisWorker(QObject):
    """在后台线程中执行分析工作。"""

    finished = Signal(str)
    error = Signal(str)
    log = Signal(str)

    def __init__(self, options_dict: dict):
        super().__init__()
        self.options_dict = options_dict
        self._stop = False

    def run(self):
        """执行分析。"""
        try:
            d = self.options_dict
            argv = []
            argv.extend(["-m", str(d["mode"])])
            argv.extend(["-p", d["path"]])
            if d.get("label"):
                argv.extend(["-o", d["label"]])
            if d.get("annotation"):
                argv.extend(["-a", d["annotation"]])
            if d.get("clades"):
                argv.extend(["-c", d["clades"]])
            if d.get("root"):
                argv.extend(["-r", d["root"]])
            if d.get("thresh"):
                argv.extend(["-t", str(d["thresh"])])
            if d.get("modelCond"):
                argv.extend(["-x", d["modelCond"]])
            if d.get("newModel"):
                argv.extend(["-y", d["newModel"]])
            if d.get("newOrder"):
                argv.extend(["-w", d["newOrder"]])
            if d.get("missing"):
                argv.extend(["-k", "1"])
            if d.get("outg"):
                argv.extend(["-g", d["outg"]])

            opt = Options.from_args(argv)
            analyzer = Analyzer(opt)

            import io
            from contextlib import redirect_stdout, redirect_stderr

            class LogCapture(io.StringIO):
                def write(self, s):
                    super().write(s)
                    if s.strip():
                        self._worker.log.emit(s.strip())
                def flush(self):
                    pass

            capturer = LogCapture()
            capturer._worker = self

            with redirect_stdout(capturer), redirect_stderr(capturer):
                analyzer.analyze()

            self.finished.emit(opt.label)
        except SystemExit as e:
            self.error.emit(f"Exit: {e}")
        except Exception as e:
            self.error.emit(f"{e}\n{traceback.format_exc()}")


# ======================================================================
# 绘图显示面板
# ======================================================================
class PlotDisplayPanel(QWidget):
    """绘图显示面板，用于展示分析生成的图形。

    扫描输出目录中的 PNG 文件，以列表 + 预览的方式展示。
    支持缩放、翻页、适应窗口、外部打开等功能。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_paths = []
        self._current_index = -1
        self._zoom_factor = 1.0
        self._fit_mode = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        # --- 工具栏 ---
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(4)

        self.btn_prev = QPushButton()
        prev_icon = _load_icon("btn_prev", 24)
        if not prev_icon.isNull():
            self.btn_prev.setIcon(prev_icon)
            self.btn_prev.setIconSize(QSize(20, 20))
        else:
            self.btn_prev.setText("◀")
        self.btn_prev.setFixedSize(36, 32)
        self.btn_prev.clicked.connect(self._show_prev)

        self.btn_next = QPushButton()
        next_icon = _load_icon("btn_next", 24)
        if not next_icon.isNull():
            self.btn_next.setIcon(next_icon)
            self.btn_next.setIconSize(QSize(20, 20))
        else:
            self.btn_next.setText("▶")
        self.btn_next.setFixedSize(36, 32)
        self.btn_next.clicked.connect(self._show_next)

        self.lbl_status = QLabel()
        self.lbl_status.setAlignment(Qt.AlignCenter)

        self.btn_zoom_in = QPushButton()
        zi_icon = _load_icon("btn_zoom_in", 24)
        if not zi_icon.isNull():
            self.btn_zoom_in.setIcon(zi_icon)
            self.btn_zoom_in.setIconSize(QSize(20, 20))
        else:
            self.btn_zoom_in.setText("+")
        self.btn_zoom_in.setFixedSize(36, 32)
        self.btn_zoom_in.clicked.connect(self._zoom_in)

        self.btn_zoom_out = QPushButton()
        zo_icon = _load_icon("btn_zoom_out", 24)
        if not zo_icon.isNull():
            self.btn_zoom_out.setIcon(zo_icon)
            self.btn_zoom_out.setIconSize(QSize(20, 20))
        else:
            self.btn_zoom_out.setText("−")
        self.btn_zoom_out.setFixedSize(36, 32)
        self.btn_zoom_out.clicked.connect(self._zoom_out)

        self.btn_zoom_fit = QPushButton()
        zf_icon = _load_icon("btn_zoom_fit", 24)
        if not zf_icon.isNull():
            self.btn_zoom_fit.setIcon(zf_icon)
            self.btn_zoom_fit.setIconSize(QSize(20, 20))
        else:
            self.btn_zoom_fit.setText("⤢")
        self.btn_zoom_fit.setFixedSize(48, 32)
        self.btn_zoom_fit.clicked.connect(self._zoom_fit)

        self.btn_open = QPushButton()
        open_icon = _load_icon("btn_open_ext", 24)
        if not open_icon.isNull():
            self.btn_open.setIcon(open_icon)
            self.btn_open.setIconSize(QSize(20, 20))
        else:
            self.btn_open.setText("⧉")
        self.btn_open.setFixedSize(48, 32)
        self.btn_open.clicked.connect(self._open_externally)

        self.btn_refresh = QPushButton()
        refresh_icon = _load_icon("btn_refresh", 24)
        if not refresh_icon.isNull():
            self.btn_refresh.setIcon(refresh_icon)
            self.btn_refresh.setIconSize(QSize(20, 20))
        else:
            self.btn_refresh.setText("⟳")
        self.btn_refresh.setFixedSize(48, 32)
        self.btn_refresh.clicked.connect(self._refresh)

        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.lbl_status, stretch=1)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addSpacing(8)
        toolbar_layout.addWidget(self.btn_zoom_out)
        toolbar_layout.addWidget(self.btn_zoom_in)
        toolbar_layout.addWidget(self.btn_zoom_fit)
        toolbar_layout.addSpacing(8)
        toolbar_layout.addWidget(self.btn_open)
        toolbar_layout.addWidget(self.btn_refresh)
        layout.addLayout(toolbar_layout)

        # --- 主体：左侧文件列表 + 右侧图像显示 ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(150)
        self.list_widget.setMaximumWidth(280)
        self.list_widget.currentRowChanged.connect(self._on_list_changed)
        splitter.addWidget(self.list_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Expanding)
        self.image_label.setMinimumSize(400, 300)
        self.scroll_area.setWidget(self.image_label)

        splitter.addWidget(self.scroll_area)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, stretch=1)

        self._update_navigation()
        self._show_placeholder()

    def retranslate_ui(self):
        """更新面板中的翻译文本。"""
        self.btn_prev.setToolTip(tr("plot_prev"))
        self.btn_next.setToolTip(tr("plot_next"))
        self.btn_zoom_in.setToolTip(tr("plot_zoom_in"))
        self.btn_zoom_out.setToolTip(tr("plot_zoom_out"))
        self.btn_zoom_fit.setToolTip(tr("plot_zoom_fit"))
        self.btn_open.setToolTip(tr("plot_open"))
        self.btn_refresh.setToolTip(tr("plot_refresh"))

        # 如果按钮没有图标（使用文字），在语言切换时也更新文字
        if self.btn_prev.icon().isNull():
            self.btn_prev.setText("◀")
        if self.btn_next.icon().isNull():
            self.btn_next.setText("▶")
        if self.btn_zoom_in.icon().isNull():
            self.btn_zoom_in.setText("+")
        if self.btn_zoom_out.icon().isNull():
            self.btn_zoom_out.setText("−")
        if self.btn_zoom_fit.icon().isNull():
            self.btn_zoom_fit.setText("⤡")
        if self.btn_open.icon().isNull():
            self.btn_open.setText("⧈")
        if self.btn_refresh.icon().isNull():
            self.btn_refresh.setText("⟳")

        self._update_navigation()

    def load_plots(self, output_dir: str):
        """扫描输出目录中的 PNG 文件并加载到面板。"""
        self._image_paths = []

        if output_dir and os.path.isdir(output_dir):
            patterns = [
                os.path.join(output_dir, "*.png"),
                os.path.join(output_dir, "**", "*.png"),
            ]
            found = set()
            for pattern in patterns:
                for f in glob.glob(pattern, recursive=True):
                    found.add(os.path.abspath(f))
            self._image_paths = sorted(found)

        self.list_widget.clear()
        for path in self._image_paths:
            name = os.path.basename(path)
            item = QListWidgetItem(name)
            item.setToolTip(path)
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

        if self._image_paths:
            self._current_index = 0
            self.list_widget.setCurrentRow(0)
            self._display_image(0)
        else:
            self._current_index = -1
            self._show_placeholder()

        self._update_navigation()

    def _show_placeholder(self):
        """显示占位文本。"""
        self.image_label.setText(tr("plot_no_images"))
        self.image_label.setPixmap(QPixmap())

    def _display_image(self, index: int):
        """显示指定索引的图像。"""
        if not self._image_paths or index < 0 or index >= len(self._image_paths):
            self._show_placeholder()
            return

        path = self._image_paths[index]
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image_label.setText(f"Failed to load: {os.path.basename(path)}")
            return

        self._current_index = index
        self._fit_mode = True
        self._apply_pixmap(pixmap)

    def _apply_pixmap(self, pixmap: QPixmap):
        """根据缩放模式应用 pixmap 到 label。"""
        if pixmap.isNull():
            return

        if self._fit_mode:
            avail = self.scroll_area.size()
            if avail.width() > 20 and avail.height() > 20:
                scaled = pixmap.scaled(
                    avail.width() - 10, avail.height() - 10,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            else:
                scaled = pixmap.scaled(
                    800, 600,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            self.image_label.setPixmap(scaled)
        else:
            orig_w = pixmap.width()
            orig_h = pixmap.height()
            new_w = max(int(orig_w * self._zoom_factor), 10)
            new_h = max(int(orig_h * self._zoom_factor), 10)
            scaled = pixmap.scaled(
                new_w, new_h,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

    def _update_navigation(self):
        """更新导航按钮状态和状态标签。"""
        has_images = len(self._image_paths) > 0
        self.btn_prev.setEnabled(has_images and self._current_index > 0)
        self.btn_next.setEnabled(
            has_images and self._current_index < len(self._image_paths) - 1
        )
        self.btn_zoom_in.setEnabled(has_images)
        self.btn_zoom_out.setEnabled(has_images)
        self.btn_zoom_fit.setEnabled(has_images)
        self.btn_open.setEnabled(has_images)

        if has_images:
            name = os.path.basename(self._image_paths[self._current_index])
            self.lbl_status.setText(
                tr("plot_status").format(
                    current=self._current_index + 1,
                    total=len(self._image_paths),
                    name=name
                )
            )
        else:
            self.lbl_status.setText("")

    def _show_prev(self):
        if self._current_index > 0:
            self.list_widget.setCurrentRow(self._current_index - 1)

    def _show_next(self):
        if self._current_index < len(self._image_paths) - 1:
            self.list_widget.setCurrentRow(self._current_index + 1)

    def _on_list_changed(self, row: int):
        if 0 <= row < len(self._image_paths):
            self._display_image(row)
            self._update_navigation()

    def _zoom_in(self):
        self._fit_mode = False
        self._zoom_factor = min(self._zoom_factor * 1.25, 10.0)
        if self._current_index >= 0:
            pixmap = QPixmap(self._image_paths[self._current_index])
            self._apply_pixmap(pixmap)

    def _zoom_out(self):
        self._fit_mode = False
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.05)
        if self._current_index >= 0:
            pixmap = QPixmap(self._image_paths[self._current_index])
            self._apply_pixmap(pixmap)

    def _zoom_fit(self):
        self._fit_mode = True
        if self._current_index >= 0:
            pixmap = QPixmap(self._image_paths[self._current_index])
            self._apply_pixmap(pixmap)

    def _open_externally(self):
        """用系统默认程序打开当前图像。"""
        if self._current_index >= 0:
            path = self._image_paths[self._current_index]
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')

    def _refresh(self):
        """刷新当前显示的图像。"""
        if self._current_index >= 0:
            self._display_image(self._current_index)

    def resizeEvent(self, event):
        """窗口大小变化时重新适应图像。"""
        super().resizeEvent(event)
        if self._fit_mode and self._current_index >= 0:
            pixmap = QPixmap(self._image_paths[self._current_index])
            QTimer.singleShot(50, lambda: self._apply_pixmap(pixmap))


# ======================================================================
# 主窗口
# ======================================================================
class MainWindow(QMainWindow):
    """DiscoVista-Next 主窗口。"""

    def __init__(self, app=None):
        super().__init__()
        self._app = app
        self._current_theme = "dark_teal.xml"
        self._worker = None
        self._thread = None
        self._last_output_dir = ""

        self._dark_themes, self._light_themes = get_all_themes()

        self._build_ui()
        self._build_menu_bar()
        self._retranslate_ui()
        if app is not None:
            self._apply_theme(self._current_theme)

        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

    # ==================================================================
    # UI 构建
    # ==================================================================
    def _build_ui(self):
        """构建主界面，使用 QSplitter 分隔参数面板和绘图面板。"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # --- 顶部：分析模式选择 + 主题选择 ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.mode_group = QGroupBox()
        mode_layout = QFormLayout(self.mode_group)
        mode_layout.setSpacing(6)
        mode_layout.setContentsMargins(8, 12, 8, 8)
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(32)
        for mode_id, mode_name in sorted(ALL_MODES.items()):
            self.mode_combo.addItem(f"{mode_id}: {mode_name}", mode_id)
        mode_layout.addRow(self.mode_combo)
        top_layout.addWidget(self.mode_group, stretch=3)

        self.theme_group_widget = QGroupBox()
        theme_layout = QFormLayout(self.theme_group_widget)
        theme_layout.setSpacing(6)
        theme_layout.setContentsMargins(8, 12, 8, 8)
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(32)
        self._populate_theme_combo()
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addRow(self.theme_combo)
        top_layout.addWidget(self.theme_group_widget, stretch=2)

        main_layout.addLayout(top_layout)

        # --- 中部：参数面板 + 绘图面板（QSplitter 水平分隔） ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(5)

        left_widget = self._build_left_panel()
        splitter.addWidget(left_widget)

        self.plot_panel = PlotDisplayPanel()
        self.plot_group = QGroupBox()
        plot_layout = QVBoxLayout(self.plot_group)
        plot_layout.setSpacing(2)
        plot_layout.setContentsMargins(4, 4, 4, 4)
        plot_layout.addWidget(self.plot_panel)
        splitter.addWidget(self.plot_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([500, 900])
        main_layout.addWidget(splitter, stretch=1)

        # --- 操作按钮 ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_run = QPushButton()
        self.btn_run.setMinimumHeight(40)
        self.btn_run.setMinimumWidth(120)
        self.btn_run.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_run.clicked.connect(self._run_analysis)

        self.btn_clear = QPushButton()
        self.btn_clear.setMinimumHeight(40)
        self.btn_clear.setMinimumWidth(100)
        self.btn_clear.clicked.connect(self._clear_log)

        self.btn_load_example = QPushButton()
        self.btn_load_example.setMinimumHeight(40)
        self.btn_load_example.setMinimumWidth(120)
        self.btn_load_example.clicked.connect(self._load_example_data)

        self.btn_stop = QPushButton()
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setMinimumWidth(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_analysis)

        btn_layout.addWidget(self.btn_load_example)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        main_layout.addLayout(btn_layout)

        # --- 进度条 ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(18)
        main_layout.addWidget(self.progress)

        # --- 日志输出 ---
        self.log_group = QGroupBox()
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setSpacing(4)
        log_layout.setContentsMargins(8, 12, 8, 8)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        self.log_text.setMaximumHeight(180)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(self.log_group)

        # --- 状态栏 ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _build_left_panel(self) -> QWidget:
        """构建左侧参数设置面板。"""
        self.param_group = QGroupBox()
        param_outer_layout = QVBoxLayout(self.param_group)
        param_outer_layout.setSpacing(4)
        param_outer_layout.setContentsMargins(8, 12, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        param_widget = QWidget()
        param_layout = QGridLayout(param_widget)
        param_layout.setSpacing(6)
        param_layout.setContentsMargins(4, 4, 4, 4)

        row = 0

        self.lbl_path = QLabel()
        self.edit_path = QLineEdit()
        self.edit_path.setMinimumHeight(28)
        self.btn_path = QPushButton()
        self.btn_path.setMinimumHeight(28)
        self.btn_path.setMinimumWidth(80)
        self.btn_path.clicked.connect(lambda: self._browse_dir(self.edit_path))
        param_layout.addWidget(self.lbl_path, row, 0)
        param_layout.addWidget(self.edit_path, row, 1)
        param_layout.addWidget(self.btn_path, row, 2)
        row += 1

        self.lbl_annotation = QLabel()
        self.edit_annotation = QLineEdit()
        self.edit_annotation.setMinimumHeight(28)
        self.btn_annotation = QPushButton()
        self.btn_annotation.setMinimumHeight(28)
        self.btn_annotation.setMinimumWidth(80)
        self.btn_annotation.clicked.connect(
            lambda: self._browse_file(self.edit_annotation))
        param_layout.addWidget(self.lbl_annotation, row, 0)
        param_layout.addWidget(self.edit_annotation, row, 1)
        param_layout.addWidget(self.btn_annotation, row, 2)
        row += 1

        self.lbl_clades = QLabel()
        self.edit_clades = QLineEdit()
        self.edit_clades.setMinimumHeight(28)
        self.btn_clades = QPushButton()
        self.btn_clades.setMinimumHeight(28)
        self.btn_clades.setMinimumWidth(80)
        self.btn_clades.clicked.connect(
            lambda: self._browse_file(self.edit_clades))
        param_layout.addWidget(self.lbl_clades, row, 0)
        param_layout.addWidget(self.edit_clades, row, 1)
        param_layout.addWidget(self.btn_clades, row, 2)
        row += 1

        self.lbl_root = QLabel()
        self.edit_root = QLineEdit()
        self.edit_root.setMinimumHeight(28)
        self.btn_root = QPushButton()
        self.btn_root.setMinimumHeight(28)
        self.btn_root.setMinimumWidth(80)
        self.btn_root.clicked.connect(
            lambda: self._browse_file(self.edit_root))
        param_layout.addWidget(self.lbl_root, row, 0)
        param_layout.addWidget(self.edit_root, row, 1)
        param_layout.addWidget(self.btn_root, row, 2)
        row += 1

        self.lbl_threshold = QLabel()
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.0, 100.0)
        self.spin_threshold.setValue(75.0)
        self.spin_threshold.setDecimals(2)
        self.spin_threshold.setMinimumHeight(28)
        param_layout.addWidget(self.lbl_threshold, row, 0)
        param_layout.addWidget(self.spin_threshold, row, 1, 1, 2)
        row += 1

        self.lbl_output = QLabel()
        self.edit_output = QLineEdit()
        self.edit_output.setMinimumHeight(28)
        self.btn_output = QPushButton()
        self.btn_output.setMinimumHeight(28)
        self.btn_output.setMinimumWidth(80)
        self.btn_output.clicked.connect(
            lambda: self._browse_dir(self.edit_output))
        param_layout.addWidget(self.lbl_output, row, 0)
        param_layout.addWidget(self.edit_output, row, 1)
        param_layout.addWidget(self.btn_output, row, 2)
        row += 1

        self.lbl_model_cond = QLabel()
        self.edit_model_cond = QLineEdit()
        self.edit_model_cond.setMinimumHeight(28)
        param_layout.addWidget(self.lbl_model_cond, row, 0)
        param_layout.addWidget(self.edit_model_cond, row, 1, 1, 2)
        row += 1

        self.lbl_new_model = QLabel()
        self.edit_new_model = QLineEdit()
        self.edit_new_model.setMinimumHeight(28)
        self.btn_new_model = QPushButton()
        self.btn_new_model.setMinimumHeight(28)
        self.btn_new_model.setMinimumWidth(80)
        self.btn_new_model.clicked.connect(
            lambda: self._browse_file(self.edit_new_model))
        param_layout.addWidget(self.lbl_new_model, row, 0)
        param_layout.addWidget(self.edit_new_model, row, 1)
        param_layout.addWidget(self.btn_new_model, row, 2)
        row += 1

        self.lbl_new_order = QLabel()
        self.edit_new_order = QLineEdit()
        self.edit_new_order.setMinimumHeight(28)
        self.btn_new_order = QPushButton()
        self.btn_new_order.setMinimumHeight(28)
        self.btn_new_order.setMinimumWidth(80)
        self.btn_new_order.clicked.connect(
            lambda: self._browse_file(self.edit_new_order))
        param_layout.addWidget(self.lbl_new_order, row, 0)
        param_layout.addWidget(self.edit_new_order, row, 1)
        param_layout.addWidget(self.btn_new_order, row, 2)
        row += 1

        self.chk_missing = QCheckBox()
        self.chk_missing.setMinimumHeight(28)
        param_layout.addWidget(self.chk_missing, row, 0, 1, 3)
        row += 1

        self.lbl_outgroup = QLabel()
        self.edit_outgroup = QLineEdit()
        self.edit_outgroup.setMinimumHeight(28)
        param_layout.addWidget(self.lbl_outgroup, row, 0)
        param_layout.addWidget(self.edit_outgroup, row, 1, 1, 2)
        row += 1

        param_layout.setColumnStretch(0, 0)
        param_layout.setColumnStretch(1, 1)
        param_layout.setColumnStretch(2, 0)

        scroll.setWidget(param_widget)
        param_outer_layout.addWidget(scroll)

        return self.param_group

    def _populate_theme_combo(self):
        """填充主题选择下拉框。"""
        self.theme_combo.clear()
        for theme_file, display_name in self._dark_themes:
            self.theme_combo.addItem(display_name, theme_file)
        self.theme_combo.insertSeparator(self.theme_combo.count())
        for theme_file, display_name in self._light_themes:
            self.theme_combo.addItem(display_name, theme_file)
        idx = self.theme_combo.findData(self._current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def _build_menu_bar(self):
        """构建菜单栏。"""
        menubar = self.menuBar()

        self.menu_file = menubar.addMenu("")
        self.action_open = QAction(self)
        self.action_open.triggered.connect(
            lambda: self._browse_dir(self.edit_path))
        self.action_quit = QAction(self)
        self.action_quit.triggered.connect(self.close)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)

        self.menu_view = menubar.addMenu("")
        self.menu_theme = self.menu_view.addMenu("")

        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        self.action_dark_label = QAction(self)
        self.action_dark_label.setEnabled(False)
        self.menu_theme.addAction(self.action_dark_label)

        for theme_file, display_name in self._dark_themes:
            action = QAction(self)
            action.setText(display_name)
            action.setCheckable(True)
            action.setData(theme_file)
            if theme_file == self._current_theme:
                action.setChecked(True)
            action.triggered.connect(
                lambda checked, tf=theme_file: self._switch_theme_by_name(tf))
            self.theme_action_group.addAction(action)
            self.menu_theme.addAction(action)

        self.menu_theme.addSeparator()

        self.action_light_label = QAction(self)
        self.action_light_label.setEnabled(False)
        self.menu_theme.addAction(self.action_light_label)

        for theme_file, display_name in self._light_themes:
            action = QAction(self)
            action.setText(display_name)
            action.setCheckable(True)
            action.setData(theme_file)
            action.triggered.connect(
                lambda checked, tf=theme_file: self._switch_theme_by_name(tf))
            self.theme_action_group.addAction(action)
            self.menu_theme.addAction(action)

        self.menu_language = menubar.addMenu("")

        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)

        self.action_zh = QAction(self)
        self.action_zh.setCheckable(True)
        self.action_zh.setChecked(True)
        self.action_zh.triggered.connect(lambda: self._switch_lang(LANG_ZH))
        self.lang_group.addAction(self.action_zh)
        self.menu_language.addAction(self.action_zh)

        self.action_en = QAction(self)
        self.action_en.setCheckable(True)
        self.action_en.triggered.connect(lambda: self._switch_lang(LANG_EN))
        self.lang_group.addAction(self.action_en)
        self.menu_language.addAction(self.action_en)

        self.menu_help = menubar.addMenu("")
        self.action_about = QAction(self)
        self.action_about.triggered.connect(self._show_about)
        self.menu_help.addAction(self.action_about)

    def _apply_theme(self, theme: str) -> None:
        """应用 qt-material 主题。"""
        extra = {
            "density_scale": "0",
            "button_shape": "default",
        }
        apply_stylesheet(self._app, theme=theme,
                         invert_secondary="light" in theme,
                         extra=extra)

    def _switch_theme_by_name(self, theme: str) -> None:
        """通过主题文件名切换主题。"""
        self._current_theme = theme
        self._apply_theme(theme)
        idx = self.theme_combo.findData(theme)
        if idx >= 0:
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(idx)
            self.theme_combo.blockSignals(False)

    def _on_theme_changed(self, index: int) -> None:
        """主题下拉框变化时触发。"""
        theme = self.theme_combo.itemData(index)
        if theme:
            self._switch_theme_by_name(theme)
            for action in self.theme_action_group.actions():
                if action.data() == theme:
                    action.setChecked(True)
                    break

    def _switch_lang(self, lang: str) -> None:
        """切换界面语言。"""
        set_language(lang)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """重新翻译所有 UI 文本。"""
        self.setWindowTitle(tr("app_title"))

        self.menu_file.setTitle(tr("menu_file"))
        self.action_open.setText(tr("menu_file_open"))
        self.action_quit.setText(tr("menu_file_quit"))
        self.menu_view.setTitle(tr("menu_view"))
        self.menu_theme.setTitle(tr("menu_view_theme"))
        self.action_dark_label.setText(tr("menu_view_dark_themes"))
        self.action_light_label.setText(tr("menu_view_light_themes"))
        self.menu_language.setTitle(tr("menu_language"))
        self.action_zh.setText(tr("menu_lang_zh"))
        self.action_en.setText(tr("menu_lang_en"))
        self.menu_help.setTitle(tr("menu_help"))
        self.action_about.setText(tr("menu_help_about"))

        self.mode_group.setTitle(tr("mode_group"))
        # 保存当前选择的模式，重新填充后恢复
        current_mode = self.mode_combo.currentData()
        self.mode_combo.clear()
        for mode_id, mode_name in sorted(ALL_MODES.items()):
            display = tr(f"mode_{mode_id}")
            self.mode_combo.addItem(f"{mode_id}: {display}", mode_id)
        # 恢复之前选择的模式
        if current_mode is not None:
            idx = self.mode_combo.findData(current_mode)
            if idx >= 0:
                self.mode_combo.setCurrentIndex(idx)

        self.theme_group_widget.setTitle(tr("menu_view_theme"))

        self.param_group.setTitle(tr("param_group"))
        self.lbl_path.setText(tr("param_data_path"))
        self.btn_path.setText(tr("param_browse"))
        self.lbl_annotation.setText(tr("param_annotation"))
        self.btn_annotation.setText(tr("param_browse"))
        self.lbl_clades.setText(tr("param_clades"))
        self.btn_clades.setText(tr("param_browse"))
        self.lbl_root.setText(tr("param_root"))
        self.btn_root.setText(tr("param_browse"))
        self.lbl_threshold.setText(tr("param_threshold"))
        self.lbl_output.setText(tr("param_output"))
        self.btn_output.setText(tr("param_browse"))
        self.lbl_model_cond.setText(tr("param_model_cond"))
        self.lbl_new_model.setText(tr("param_new_model"))
        self.btn_new_model.setText(tr("param_browse"))
        self.lbl_new_order.setText(tr("param_new_order"))
        self.btn_new_order.setText(tr("param_browse"))
        self.chk_missing.setText(tr("param_missing"))
        self.lbl_outgroup.setText(tr("param_outgroup"))

        self.btn_run.setText(tr("btn_run"))
        self.btn_clear.setText(tr("btn_clear"))
        self.btn_load_example.setText(tr("btn_load_example"))
        self.btn_stop.setText(tr("btn_stop"))

        self.log_group.setTitle(tr("log_group"))

        self.plot_group.setTitle(tr("plot_group"))
        self.plot_panel.retranslate_ui()

        self.status_bar.showMessage(tr("status_ready"))

    def _browse_dir(self, edit: QLineEdit) -> None:
        dir_path = QFileDialog.getExistingDirectory(self)
        if dir_path:
            edit.setText(dir_path)

    def _browse_file(self, edit: QLineEdit) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            edit.setText(file_path)

    def _load_example_data(self) -> None:
        """加载示例数据路径。"""
        possible_paths = []

        if getattr(sys, 'frozen', False):
            # PyInstaller onedir 模式：优先从 exe 所在目录及各级上级查找 examples
            exe_dir = os.path.dirname(sys.executable)
            possible_paths.extend([
                os.path.join(exe_dir, "examples"),
                os.path.join(exe_dir, "..", "examples"),
                os.path.join(exe_dir, "..", "..", "examples"),
                os.path.join(exe_dir, "_internal", "examples"),
            ])
            # 同时检查 sys._MEIPASS（PyInstaller 临时解包目录）
            meipass = getattr(sys, '_MEIPASS', None)
            if meipass:
                possible_paths.append(os.path.join(meipass, "examples"))
        else:
            package_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
            possible_paths.append(os.path.join(package_dir, "examples"))

        possible_paths.append(os.path.join(os.getcwd(), "examples"))

        example_dir = None
        for p in possible_paths:
            if os.path.isdir(p):
                example_dir = p
                break

        if example_dir is None:
            QMessageBox.warning(self, tr("app_title"), tr("msg_no_example"))
            return

        kp_dir = os.path.join(example_dir, "1KP")
        if not os.path.isdir(kp_dir):
            QMessageBox.warning(self, tr("app_title"), tr("msg_no_example"))
            return

        param_dir = os.path.join(kp_dir, "parameters")
        annotation = os.path.join(param_dir, "annotation.txt")
        clades = os.path.join(param_dir, "clade-defs.txt")
        root = os.path.join(param_dir, "rooting.txt")
        new_model = os.path.join(param_dir, "newModel.txt")
        new_order = os.path.join(param_dir, "newOrders.txt")

        if os.path.isfile(annotation):
            self.edit_annotation.setText(annotation)
        if os.path.isfile(clades):
            self.edit_clades.setText(clades)
        if os.path.isfile(root):
            self.edit_root.setText(root)
        if os.path.isfile(new_model):
            self.edit_new_model.setText(new_model)
        if os.path.isfile(new_order):
            self.edit_new_order.setText(new_order)

        species_dir = os.path.join(kp_dir, "species")
        if os.path.isdir(species_dir):
            self.edit_path.setText(species_dir)
            self.mode_combo.setCurrentIndex(0)
            self.spin_threshold.setValue(95)

        output_dir = os.path.join(kp_dir, "results")
        self.edit_output.setText(output_dir)

        self.status_bar.showMessage(tr("msg_example_loaded"))

    def _run_analysis(self) -> None:
        """执行分析。"""
        mode = self.mode_combo.currentData()
        if mode is None:
            QMessageBox.warning(self, tr("app_title"), tr("msg_select_mode"))
            return
        if not self.edit_path.text():
            QMessageBox.warning(self, tr("app_title"), tr("msg_select_path"))
            return
        if not self.edit_output.text():
            QMessageBox.warning(self, tr("app_title"), tr("msg_select_output"))
            return

        options_dict = {
            "mode": mode,
            "path": self.edit_path.text(),
            "label": self.edit_output.text(),
            "annotation": self.edit_annotation.text(),
            "clades": self.edit_clades.text(),
            "root": self.edit_root.text(),
            "thresh": self.spin_threshold.value(),
            "modelCond": self.edit_model_cond.text(),
            "newModel": self.edit_new_model.text(),
            "newOrder": self.edit_new_order.text(),
            "missing": 1 if self.chk_missing.isChecked() else 0,
            "outg": self.edit_outgroup.text(),
        }

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setVisible(True)
        self.status_bar.showMessage(tr("status_running"))
        self.log_text.clear()

        self._worker = AnalysisWorker(options_dict)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._on_log)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_log(self, msg: str) -> None:
        self.log_text.append(msg)

    def _on_finished(self, output_dir: str) -> None:
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self.status_bar.showMessage(tr("status_done"))
        self._last_output_dir = output_dir

        # 加载生成的图形到绘图面板
        self.plot_panel.load_plots(output_dir)

        # 统计图形数量
        plot_count = len(self.plot_panel._image_paths)
        if plot_count > 0:
            QMessageBox.information(
                self, tr("app_title"),
                tr("msg_success") + output_dir +
                f"\n({plot_count} plots displayed)"
            )
        else:
            QMessageBox.information(
                self, tr("app_title"),
                tr("msg_success") + output_dir
            )

    def _on_error(self, msg: str) -> None:
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self.status_bar.showMessage(tr("status_error"))
        self.log_text.append(f"ERROR: {msg}")
        QMessageBox.critical(self, tr("app_title"), tr("msg_failed"))

    def _stop_analysis(self) -> None:
        """停止正在运行的分析。"""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(5000)
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self.status_bar.showMessage(tr("status_ready"))

    def _clear_log(self) -> None:
        self.log_text.clear()

    def _show_about(self) -> None:
        QMessageBox.about(self, tr("msg_about_title"), tr("msg_about_text"))

    def closeEvent(self, event):
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(3000)
        event.accept()


# ======================================================================
# 主入口
# ======================================================================
def main() -> int:
    """GUI 主入口函数。"""
    app = QApplication(sys.argv)

    # 设置应用图标
    icon_path = _icon_path("app_icon", 256) or _icon_path("app_icon", 64)
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow(app=app)
    window.show()

    if hasattr(app, "exec"):
        return app.exec()
    else:
        return app.exec_()


if __name__ == "__main__":
    sys.exit(main())