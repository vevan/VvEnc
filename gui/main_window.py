"""
主窗口 - 视频编码工具主界面
"""
import os
import sys
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QProgressBar, QLabel,
    QFileDialog, QMessageBox, QGroupBox,
    QTextEdit, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor, QBrush, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Windows 任务栏进度条支持（仅 Windows）
if sys.platform == 'win32':
    try:
        from PyQt5.QtWinExtras import QWinTaskbarButton, QWinTaskbarProgress
        HAS_WIN_TASKBAR = True
    except ImportError:
        HAS_WIN_TASKBAR = False
else:
    HAS_WIN_TASKBAR = False
from core.config_manager import ConfigManager
from core.ffmpeg_handler import FFmpegHandler
from core.file_processor import FileProcessor
from gui.settings_dialog import SettingsDialog
from translations import LanguageManager
from typing import Optional, Dict


class NumericTableWidgetItem(QTableWidgetItem):
    """支持数值排序的表格项"""
    def __lt__(self, other):
        # 优先使用UserRole中的数值进行排序
        self_data = self.data(Qt.UserRole)
        other_data = other.data(Qt.UserRole)
        
        # 如果UserRole有值，使用数值排序
        if self_data is not None and other_data is not None:
            try:
                return float(self_data) < float(other_data)
            except (ValueError, TypeError):
                pass
        
        # 否则使用文本排序
        return super().__lt__(other)


# 表格列索引常量
COL_FILENAME = 0
COL_STATUS = 1
COL_RESOLUTION = 2
COL_BITRATE = 3
COL_FRAMERATE = 4
COL_DURATION = 5
COL_VIDEO_CODEC = 6
COL_FILE_SIZE = 7
COL_AUDIO_CODEC = 8
COL_AUDIO_BITRATE = 9
COL_BITS_PER_PIXEL = 10
COL_PATH = 11


# 文件状态代码
STATUS_WAITING = "waiting"
STATUS_ENCODING = "encoding"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_PAUSED = "paused"

STATUS_KEY_MAP = {
    STATUS_WAITING: 'STATUS_WAITING',
    STATUS_ENCODING: 'STATUS_ENCODING',
    STATUS_DONE: 'STATUS_DONE',
    STATUS_FAILED: 'STATUS_FAILED',
    STATUS_PAUSED: 'STATUS_PAUSED',
}

# 各状态对应的浅色背景
STATUS_BG_COLORS = {
    STATUS_WAITING: QColor('#FFF9CC'),   # 浅黄
    STATUS_ENCODING: QColor('#DDEEFF'),  # 浅蓝
    STATUS_DONE: QColor('#E5F8E5'),      # 浅绿
    STATUS_FAILED: QColor('#FAD4D4'),    # 浅红
    STATUS_PAUSED: QColor('#F0E6FF'),    # 浅紫
}


class FileInfoWorker(QThread):
    """文件信息获取工作线程"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, file_path
    file_info_ready = pyqtSignal(str, dict)  # file_path, info
    finished = pyqtSignal()
    
    def __init__(self, ffmpeg_handler, files: list):
        super().__init__()
        self.ffmpeg_handler = ffmpeg_handler
        self.files = files
        self.cancelled = False
    
    def run(self):
        """获取文件信息"""
        total = len(self.files)
        for current, file_path in enumerate(self.files, 1):
            if self.cancelled:
                break
            self.progress_updated.emit(current, total, file_path)
            
            if self.ffmpeg_handler:
                try:
                    info = self.ffmpeg_handler.get_detailed_video_info(file_path)
                    self.file_info_ready.emit(file_path, info)
                except Exception:
                    self.file_info_ready.emit(file_path, {})
            else:
                self.file_info_ready.emit(file_path, {})
        
        self.finished.emit()
    
    def cancel(self):
        """取消获取"""
        self.cancelled = True


class LoadingDialog(QDialog):
    """加载对话框"""
    def __init__(self, parent=None, tr_func=None):
        super().__init__(parent)
        self.tr_func = tr_func or (lambda key, default=None: default or key)
        self.setWindowTitle(self.tr_func('LOADING_FILES', '加载中...'))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)
        
        # 根据父窗口大小设置对话框大小
        if parent:
            parent_width = parent.width()
            dialog_width = int(parent_width * 0.8)
            # 高度大约5行：标签（2行）+ 进度条 + 间距
            font_metrics = self.fontMetrics()
            line_height = font_metrics.lineSpacing()
            dialog_height = line_height * 5 + 40  # 5行高度 + 边距
            self.setFixedSize(dialog_width, dialog_height)
        else:
            # 如果没有父窗口，使用默认大小
            self.setFixedSize(400, 150)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.label = QLabel(self.tr_func('LOADING_FILES_INIT', '正在载入文件信息...'))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # 允许文本换行
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        layout.addWidget(self.progress_bar)
    
    def update_progress(self, current: int, total: int, file_path: str = ""):
        """更新进度"""
        filename = os.path.basename(file_path) if file_path else ""
        loading_text = self.tr_func('LOADING_FILES_PROGRESS', '正在载入 {current}/{total} 文件')
        self.label.setText(f"{loading_text.format(current=current, total=total)}\n{filename}")
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)


class EncodeWorker(QThread):
    """编码工作线程"""
    progress_updated = pyqtSignal(int, int, str, float, str)  # current, total, file, progress, message
    file_started = pyqtSignal(int, int, str)  # current, total, file_path
    file_finished = pyqtSignal(int, int, str, bool, str)  # current, total, file_path, success, message
    finished = pyqtSignal(list)  # results
    
    def __init__(self, file_processor: FileProcessor, files: list, output_dir: str, encode_kwargs: dict,
                 per_file_options: Optional[Dict[str, Dict[str, object]]] = None):
        super().__init__()
        self.file_processor = file_processor
        self.files = files
        self.output_dir = output_dir
        self.encode_kwargs = encode_kwargs
        self.per_file_options = per_file_options or {}
        self.cancelled = False
    
    def run(self):
        """执行编码任务"""
        results = self.file_processor.process_files(
            self.files,
            self.output_dir,
            progress_callback=self.on_progress,
            file_started_callback=self.on_file_started,
            file_finished_callback=self.on_file_finished,
            cancel_flag=lambda: self.cancelled,
            per_file_options=self.per_file_options,
            **self.encode_kwargs
        )
        # 发送结果（无论是否取消都发送）
        self.finished.emit(results)
    
    def on_file_started(self, current: int, total: int, file_path: str):
        """文件开始编码回调"""
        if not self.cancelled:
            self.file_started.emit(current, total, file_path)
    
    def on_file_finished(self, current: int, total: int, file_path: str, success: bool, message: str):
        """文件结束编码回调"""
        if not self.cancelled:
            self.file_finished.emit(current, total, file_path, success, message)
    
    def on_progress(self, current: int, total: int, file_path: str, progress: float, message: str):
        """进度回调"""
        if not self.cancelled:
            self.progress_updated.emit(current, total, file_path, progress, message)
    
    def cancel(self):
        """取消编码"""
        self.cancelled = True


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, i18n_manager: LanguageManager = None):
        super().__init__()
        self.config_manager = ConfigManager()
        self.i18n_manager = i18n_manager or LanguageManager()
        self.ffmpeg_handler = None
        self.file_processor = None
        self.encode_worker = None
        self.file_list = []  # 待编码文件列表
        self.file_info_dict = {}  # 文件信息字典 {文件路径: 详细信息}
        self.file_status = {}  # 文件状态 {文件路径: 状态代码}
        self._last_encoded_total_size = None  # 最近一次编码后的总大小（字节），用于语言切换时刷新显示
        self.file_info_worker = None  # 文件信息获取工作线程
        self.loading_dialog = None  # 加载对话框
        
        # 设置窗口图标（窗口左上角图标）
        # 处理 PyInstaller 打包后的路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件：从临时目录读取
            base_path = sys._MEIPASS
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.dirname(__file__))
        
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 初始化 Windows 任务栏进度条（仅 Windows）
        if HAS_WIN_TASKBAR:
            self.taskbar_button = QWinTaskbarButton(self)
            self.taskbar_progress = self.taskbar_button.progress()
            self.taskbar_progress.setMaximum(100)
            self.taskbar_progress.setValue(0)
            self.taskbar_progress.setVisible(False)
        
        self.init_ffmpeg()
        self.init_ui()
        self.load_output_dir()
    
    def tr(self, key: str, default: str = None) -> str:
        """翻译函数"""
        return self.i18n_manager.tr(key, default)
    
    def format_duration(self, seconds: float) -> str:
        """格式化时长"""
        if seconds <= 0:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def load_table_settings(self):
        """加载表格设置（列顺序和列宽）"""
        column_order = self.config_manager.get("table_column_order", None)
        column_widths = self.config_manager.get("table_column_widths", None)
        
        if column_order and isinstance(column_order, list) and len(column_order) == self.file_table.columnCount():
            # 恢复列顺序（需要在所有列创建后执行）
            # 这里先保存顺序，稍后在init_ui完成后应用
            self._pending_column_order = column_order
        else:
            self._pending_column_order = None
        
        if column_widths and isinstance(column_widths, dict):
            # 恢复列宽
            for col_index_str, width in column_widths.items():
                col_index = int(col_index_str)
                if 0 <= col_index < self.file_table.columnCount():
                    self.file_table.setColumnWidth(col_index, int(width))
    
    def apply_pending_column_order(self):
        """应用待处理的列顺序"""
        if hasattr(self, '_pending_column_order') and self._pending_column_order:
            # column_order存储的是逻辑索引的顺序
            # 需要将逻辑索引移动到对应的视觉位置
            header = self.file_table.horizontalHeader()
            for visual_pos, logical_index in enumerate(self._pending_column_order):
                if visual_pos < self.file_table.columnCount() and logical_index < self.file_table.columnCount():
                    current_visual = header.visualIndex(logical_index)
                    if current_visual != visual_pos:
                        header.moveSection(current_visual, visual_pos)
    
    def save_table_settings(self):
        """保存表格设置（列顺序和列宽）"""
        # 获取当前列顺序（逻辑索引的顺序）
        column_order = []
        for i in range(self.file_table.columnCount()):
            logical_index = self.file_table.horizontalHeader().logicalIndex(i)
            column_order.append(logical_index)
        
        # 获取当前列宽
        column_widths = {}
        for i in range(self.file_table.columnCount()):
            column_widths[i] = self.file_table.columnWidth(i)
        
        # 保存到配置
        self.config_manager.set("table_column_order", column_order)
        self.config_manager.set("table_column_widths", column_widths)
        self.config_manager.save_config()
    
    def on_column_moved(self, logical_index: int, old_visual_index: int, new_visual_index: int):
        """列移动时的回调"""
        self.save_table_settings()
    
    def on_column_resized(self, logical_index: int, old_size: int, new_size: int):
        """列大小改变时的回调"""
        self.save_table_settings()
    
    def init_ffmpeg(self):
        """初始化FFmpeg处理器"""
        try:
            ffmpeg_path = self.config_manager.get("ffmpeg_path", "")
            self.ffmpeg_handler = FFmpegHandler(ffmpeg_path if ffmpeg_path else "")
            self.file_processor = FileProcessor(self.ffmpeg_handler)
        except FileNotFoundError as e:
            QMessageBox.warning(
                self,
                self.tr('MSG_FFMPEG_NOT_FOUND'),
                f"{str(e)}\n\n" + self.tr('MSG_FFMPEG_NOT_INIT')
            )
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(self.tr('MAIN_WINDOW_TITLE'))
        self.setMinimumSize(800, 600)
        # 恢复上次保存的窗口大小和位置
        try:
            width = int(self.config_manager.get("window_width", 0) or 0)
            height = int(self.config_manager.get("window_height", 0) or 0)
            if width > 0 and height > 0:
                self.resize(width, height)
            
            pos_x = int(self.config_manager.get("window_pos_x", 0) or 0)
            pos_y = int(self.config_manager.get("window_pos_y", 0) or 0)
            if pos_x > 0 and pos_y > 0:
                self.move(pos_x, pos_y)
        except Exception:
            pass
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton(self.tr('ADD_FILES'))
        self.add_files_btn.clicked.connect(self.add_files)
        toolbar_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton(self.tr('ADD_FOLDER'))
        self.add_folder_btn.clicked.connect(self.add_folder)
        toolbar_layout.addWidget(self.add_folder_btn)
        
        self.remove_btn = QPushButton(self.tr('REMOVE_SELECTED'))
        self.remove_btn.clicked.connect(self.remove_selected)
        toolbar_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton(self.tr('CLEAR_LIST'))
        self.clear_btn.clicked.connect(self.clear_list)
        toolbar_layout.addWidget(self.clear_btn)
        
        toolbar_layout.addStretch()
        
        # 语言切换按钮（固定显示为"Language"）
        self.language_btn = QPushButton("Language")
        self.language_btn.clicked.connect(self.show_language_menu)
        toolbar_layout.addWidget(self.language_btn)
        
        self.settings_btn = QPushButton(self.tr('SETTINGS'))
        self.settings_btn.clicked.connect(self.show_settings)
        toolbar_layout.addWidget(self.settings_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 文件列表（使用表格显示详细信息）
        self.list_group = QGroupBox(self.tr('FILE_LIST_TITLE'))
        list_layout = QVBoxLayout()
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(12)  # 文件名 + 状态 + 其它信息 + 路径列
        self.file_table.setHorizontalHeaderLabels([
            self.tr('COL_FILENAME'), self.tr('COL_STATUS'), self.tr('COL_RESOLUTION'), self.tr('COL_BITRATE'),
            self.tr('COL_FRAMERATE'), self.tr('COL_DURATION'), self.tr('COL_VIDEO_CODEC'),
            self.tr('COL_FILE_SIZE'), self.tr('COL_AUDIO_CODEC'), self.tr('COL_AUDIO_BITRATE'),
            self.tr('COL_BITS_PER_PIXEL'), self.tr('COL_PATH')
        ])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.setAlternatingRowColors(True)
        # 启用表头排序
        self.file_table.setSortingEnabled(True)
        # 启用列拖曳
        self.file_table.horizontalHeader().setSectionsMovable(True)
        self.file_table.horizontalHeader().setDragDropMode(QHeaderView.InternalMove)
        # 连接列移动信号，保存列顺序
        self.file_table.horizontalHeader().sectionMoved.connect(self.on_column_moved)
        self.file_table.horizontalHeader().sectionResized.connect(self.on_column_resized)
        # 表格右键菜单（用于修改状态）
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_table.customContextMenuRequested.connect(self.on_table_context_menu)
        
        # 加载保存的列顺序和列宽
        self.load_table_settings()
        
        # 默认列宽（如果配置中没有）
        default_widths = {
            COL_FILENAME: 200,       # 文件名
            COL_STATUS: 80,          # 状态
            COL_RESOLUTION: 100,     # 分辨率
            COL_BITRATE: 100,        # 码率
            COL_FRAMERATE: 80,       # 帧率
            COL_DURATION: 100,       # 总时长
            COL_VIDEO_CODEC: 100,    # 视频编码
            COL_FILE_SIZE: 100,      # 文件大小
            COL_AUDIO_CODEC: 100,    # 音频编码
            COL_AUDIO_BITRATE: 100,  # 音频码率
            COL_BITS_PER_PIXEL: 150, # 每帧/10000像素bit数
        }
        
        # 应用列宽
        for col, width in default_widths.items():
            if self.file_table.columnWidth(col) == 100:  # 默认宽度，应用自定义宽度
                self.file_table.setColumnWidth(col, width)
        
        self.file_table.setColumnHidden(COL_PATH, True)  # 隐藏路径列
        
        list_layout.addWidget(self.file_table)
        
        # 文件大小总计标签
        self.total_size_label = QLabel()
        self.total_size_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        self.update_total_size_display()
        list_layout.addWidget(self.total_size_label)
        
        self.list_group.setLayout(list_layout)
        layout.addWidget(self.list_group)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.output_dir_text_label = QLabel(self.tr('OUTPUT_DIR') + ":")
        output_layout.addWidget(self.output_dir_text_label)
        
        self.output_dir_label = QLabel(self.tr('OUTPUT_DIR_NOT_SET'))
        self.output_dir_label.setStyleSheet("color: gray;")
        output_layout.addWidget(self.output_dir_label)
        
        self.output_dir_btn = QPushButton(self.tr('SELECT_OUTPUT_DIR'))
        self.output_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_btn)
        
        layout.addLayout(output_layout)
        
        # 进度显示
        self.progress_group = QGroupBox(self.tr('ENCODING_PROGRESS'))
        progress_layout = QVBoxLayout()
        
        # 总体进度
        self.overall_label = QLabel(self.tr('OVERALL_PROGRESS') + ":")
        progress_layout.addWidget(self.overall_label)
        
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setRange(0, 100)
        self.overall_progress_bar.setValue(0)
        progress_layout.addWidget(self.overall_progress_bar)
        
        self.overall_progress_label = QLabel(self.tr('WAITING'))
        progress_layout.addWidget(self.overall_progress_label)
        
        # 分隔线
        progress_layout.addSpacing(10)
        
        # 当前文件进度
        self.current_label = QLabel(self.tr('CURRENT_FILE_PROGRESS') + ":")
        progress_layout.addWidget(self.current_label)
        
        self.current_file_progress_bar = QProgressBar()
        self.current_file_progress_bar.setRange(0, 100)
        self.current_file_progress_bar.setValue(0)
        progress_layout.addWidget(self.current_file_progress_bar)
        
        self.current_file_label = QLabel("")
        progress_layout.addWidget(self.current_file_label)
        
        self.progress_group.setLayout(progress_layout)

        # 日志区域（固定高度，大约 6 行）
        self.log_group = QGroupBox(self.tr('LOG_TITLE'))
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # 使用字体行高估算 6 行高度
        line_height = self.log_text.fontMetrics().lineSpacing()
        self.log_text.setFixedHeight(line_height * 6 + 12)
        log_layout.addWidget(self.log_text)
        
        self.log_group.setLayout(log_layout)

        # 将进度和日志区域并排放置到一个单独的容器中，并固定该容器高度
        self.info_widget = QWidget()
        progress_log_layout = QHBoxLayout(self.info_widget)
        progress_log_layout.setContentsMargins(0, 0, 0, 0)
        progress_log_layout.addWidget(self.progress_group, 2)
        progress_log_layout.addWidget(self.log_group, 3)
        # 估算信息区域高度：进度部分 + 日志部分
        info_height = self.log_text.height() + self.overall_progress_bar.sizeHint().height() * 3 + 40
        self.info_widget.setFixedHeight(info_height)
        layout.addWidget(self.info_widget)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.start_btn = QPushButton(self.tr('START_ENCODING'))
        self.start_btn.clicked.connect(self.start_encoding)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(self.tr('STOP'))
        self.stop_btn.clicked.connect(self.stop_encoding)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 启用拖放
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.exists(path):
                self.add_path(path)
        event.acceptProposedAction()
    
    def add_path(self, path: str):
        """添加路径（文件或文件夹）"""
        if not self.file_processor:
            QMessageBox.warning(self, self.tr('MSG_ERROR'), self.tr('MSG_FFMPEG_NOT_INIT'))
            return
        
        files = self.file_processor.scan_files(path)
        if not files:
            QMessageBox.information(self, self.tr('MSG_INFO'), self.tr('MSG_NO_VIDEO_FILES'))
            return
        
        # 过滤掉已存在的文件
        new_files = [f for f in files if f not in self.file_list]
        if not new_files:
            return
        
        # 添加到列表，初始状态为等待编码
        for file_path in new_files:
            self.file_list.append(file_path)
            self.file_status[file_path] = STATUS_WAITING
            # 先添加到表格（显示基本信息）
            self.add_file_to_table(file_path)
        
        # 如果文件数量较多，使用异步加载并显示进度对话框
        if len(new_files) > 5:
            self._load_file_info_async(new_files)
        else:
            # 文件数量少，直接同步加载
            for file_path in new_files:
                self._load_single_file_info(file_path)
                # 处理事件，保持界面响应
                QApplication.processEvents()
        
        # 记录最后一个文件的目录路径到配置
        if new_files:
            last_file_path = new_files[-1]
            last_file_dir = os.path.dirname(last_file_path)
            if last_file_dir and os.path.exists(last_file_dir):
                self.config_manager.set("last_file_dir", last_file_dir)
                self.config_manager.save_config()
        
        self.update_total_size_display()
        self.log(self.tr('LOG_FILES_ADDED').format(count=len(new_files)), "info")
    
    def _load_file_info_async(self, files: list):
        """异步加载文件信息（显示进度对话框）"""
        # 创建并显示加载对话框
        self.loading_dialog = LoadingDialog(self, tr_func=self.tr)
        
        # 创建工作线程
        self.file_info_worker = FileInfoWorker(self.ffmpeg_handler, files)
        self.file_info_worker.progress_updated.connect(self._on_file_info_progress)
        self.file_info_worker.file_info_ready.connect(self._on_file_info_ready)
        self.file_info_worker.finished.connect(self._on_file_info_finished)
        
        # 显示对话框并启动线程
        self.loading_dialog.show()
        self.file_info_worker.start()
    
    def _load_single_file_info(self, file_path: str):
        """同步加载单个文件信息"""
        row = self._find_file_row(file_path)
        if row < 0:
            return
        
        if self.ffmpeg_handler:
            try:
                info = self.ffmpeg_handler.get_detailed_video_info(file_path)
                self.file_info_dict[file_path] = info
                self.file_table.setSortingEnabled(False)
                self.update_file_info(row, file_path, info)
                self.file_table.setSortingEnabled(True)
            except Exception as e:
                filename = os.path.basename(file_path)
                self.log(f"获取文件信息失败 {filename}: {str(e)}", "error")
                self.file_table.setSortingEnabled(False)
                self.update_file_info(row, file_path, {})
                self.file_table.setSortingEnabled(True)
        else:
            # 如果没有FFmpeg，至少显示文件大小
            self.file_table.setSortingEnabled(False)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            size_str = self.format_file_size(file_size)
            size_item = NumericTableWidgetItem(size_str)
            size_item.setData(Qt.UserRole, file_size)
            size_item.setToolTip(size_str)
            self.file_table.setItem(row, COL_FILE_SIZE, size_item)
            self.update_file_info(row, file_path, {})
            self.file_table.setSortingEnabled(True)
    
    def _find_file_row(self, file_path: str) -> int:
        """查找文件在表格中的行号"""
        for row in range(self.file_table.rowCount()):
            path_item = self.file_table.item(row, COL_PATH)
            if path_item and path_item.text() == file_path:
                return row
        return -1
    
    def _on_file_info_progress(self, current: int, total: int, file_path: str):
        """文件信息获取进度更新"""
        if self.loading_dialog:
            self.loading_dialog.update_progress(current, total, file_path)
    
    def _on_file_info_ready(self, file_path: str, info: dict):
        """单个文件信息获取完成"""
        self.file_info_dict[file_path] = info
        row = self._find_file_row(file_path)
        if row >= 0:
            self.file_table.setSortingEnabled(False)
            self.update_file_info(row, file_path, info)
            self.file_table.setSortingEnabled(True)
    
    def _on_file_info_finished(self):
        """所有文件信息获取完成"""
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        self.file_info_worker = None
    
    def add_files(self):
        """添加文件"""
        # 获取上次保存的目录路径
        last_dir = self.config_manager.get("last_file_dir", "")
        if not last_dir or not os.path.exists(last_dir):
            last_dir = ""
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr('SELECT_VIDEO_FILES'),
            last_dir,
            self.tr('VIDEO_FILES_FILTER')
        )
        for file_path in files:
            self.add_path(file_path)
    
    def add_folder(self):
        """添加文件夹"""
        # 获取上次保存的目录路径
        last_dir = self.config_manager.get("last_file_dir", "")
        if not last_dir or not os.path.exists(last_dir):
            last_dir = ""
        
        folder = QFileDialog.getExistingDirectory(self, self.tr('SELECT_FOLDER'), last_dir)
        if folder:
            self.add_path(folder)
    
    def remove_selected(self):
        """移除选中的文件"""
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())
        
        # 从后往前删除，避免索引变化
        for row in sorted(selected_rows, reverse=True):
            if row < len(self.file_list):
                file_path = self.file_list.pop(row)
                if file_path in self.file_info_dict:
                    del self.file_info_dict[file_path]
                if file_path in self.file_status:
                    del self.file_status[file_path]
                self.file_table.removeRow(row)
        
        self.update_total_size_display()
    
    def clear_list(self):
        """清空列表"""
        self.file_list.clear()
        self.file_info_dict.clear()
        self.file_status.clear()
        self.file_table.setRowCount(0)
        self.update_total_size_display()

    def on_table_context_menu(self, pos):
        """文件列表右键菜单：用于修改状态（等待编码 / 挂起）、打开文件、定位文件"""
        indexes = self.file_table.selectedIndexes()
        if not indexes:
            return
        rows = sorted({idx.row() for idx in indexes})
        
        # 获取选中行的文件路径（只处理第一行，如果多选则只对第一行操作）
        if rows:
            path_item = self.file_table.item(rows[0], COL_PATH)
            if not path_item:
                return
            file_path = path_item.text()
        else:
            return
        
        # 构建菜单
        menu = QMenu(self)
        
        # 状态操作
        action_waiting = menu.addAction(self.tr('STATUS_WAITING'))
        action_paused = menu.addAction(self.tr('STATUS_PAUSED'))
        menu.addSeparator()
        
        # 文件操作
        action_open_file = menu.addAction(self.tr('OPEN_SOURCE_FILE'))
        action_reveal_file = menu.addAction(self.tr('REVEAL_SOURCE_FILE'))
        
        global_pos = self.file_table.viewport().mapToGlobal(pos)
        action = menu.exec_(global_pos)
        if not action:
            return

        # 处理文件操作
        if action == action_open_file:
            self._open_source_file(file_path)
        elif action == action_reveal_file:
            self._reveal_source_file(file_path)
        # 处理状态操作
        elif action == action_waiting:
            for row in rows:
                path_item = self.file_table.item(row, COL_PATH)
                if path_item:
                    self._set_file_status(path_item.text(), STATUS_WAITING)
        elif action == action_paused:
            for row in rows:
                path_item = self.file_table.item(row, COL_PATH)
                if path_item:
                    self._set_file_status(path_item.text(), STATUS_PAUSED)
    
    def _open_source_file(self, file_path: str):
        """使用系统默认程序打开源文件"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, self.tr('MSG_ERROR'), self.tr('MSG_FILE_NOT_FOUND'))
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, self.tr('MSG_ERROR'), 
                             self.tr('MSG_OPEN_FILE_FAILED').format(error=str(e)))
    
    def _reveal_source_file(self, file_path: str):
        """打开源文件所在目录并选中文件"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, self.tr('MSG_ERROR'), self.tr('MSG_FILE_NOT_FOUND'))
            return
        
        try:
            if sys.platform == 'win32':
                # Windows: 使用 explorer /select 命令
                subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            elif sys.platform == 'darwin':  # macOS
                # macOS: 使用 open -R 命令
                subprocess.run(['open', '-R', file_path])
            else:  # Linux
                # Linux: 打开文件所在目录
                file_dir = os.path.dirname(file_path)
                subprocess.run(['xdg-open', file_dir])
        except Exception as e:
            QMessageBox.warning(self, self.tr('MSG_ERROR'), 
                             self.tr('MSG_REVEAL_FILE_FAILED').format(error=str(e)))
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def format_bitrate(self, bitrate: int) -> str:
        """格式化码率（统一使用Mbps）"""
        if bitrate == 0:
            return "N/A"
        # 统一转换为Mbps显示
        mbps = bitrate / 1000000.0
        if mbps < 0.01:
            # 如果小于0.01 Mbps，显示Kbps
            kbps = bitrate / 1000.0
            return f"{kbps:.2f} Kbps"
        else:
            return f"{mbps:.2f} Mbps"
    
    def calculate_total_size(self) -> int:
        """计算列表中所有文件的总大小（字节）"""
        total_size = 0
        for file_path in self.file_list:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        return total_size
    
    def update_total_size_display(self, encoded_total_size: int = None):
        """更新文件大小总计显示
        
        Args:
            encoded_total_size: 编码后文件总大小（字节），None 表示仅显示源文件总大小
        """
        if encoded_total_size is not None:
            # 记录最近一次编码后的总大小，便于语言切换时刷新
            self._last_encoded_total_size = encoded_total_size
            original_total = self.calculate_total_size()
            encoded_size_str = self.format_file_size(encoded_total_size)
            original_size_str = self.format_file_size(original_total)
            self.total_size_label.setText(
                self.tr('TOTAL_SIZE_ENCODED').format(
                    original=original_size_str,
                    encoded=encoded_size_str
                )
            )
        else:
            # 只显示源文件总大小
            self._last_encoded_total_size = None
            total_size = self.calculate_total_size()
            size_str = self.format_file_size(total_size)
            self.total_size_label.setText(
                self.tr('TOTAL_SIZE').format(size=size_str)
            )
    
    def _find_row_by_path(self, file_path: str) -> int:
        """根据文件路径查找所在行索引，找不到返回 -1"""
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, self.file_table.columnCount() - 1)  # 路径列始终为最后一列
            if item and item.text() == file_path:
                return row
        return -1

    def _set_file_status(self, file_path: str, status_code: str):
        """设置文件状态并更新表格中的显示"""
        self.file_status[file_path] = status_code
        row = self._find_row_by_path(file_path)
        if row == -1:
            return
        status_key = STATUS_KEY_MAP.get(status_code, 'STATUS_WAITING')
        status_text = self.tr(status_key)
        item = self.file_table.item(row, COL_STATUS)
        if item is None:
            # 还没有状态单元格，创建并插入
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, COL_STATUS, item)
        # 更新已有单元格内容
        item.setText(status_text)
        item.setToolTip(status_text)
        item.setData(Qt.UserRole, status_code)

        # 设置整行背景色
        color = STATUS_BG_COLORS.get(status_code)
        brush = QBrush(color) if color is not None else QBrush()
        for col in range(self.file_table.columnCount()):
            cell = self.file_table.item(row, col)
            if cell is None:
                cell = QTableWidgetItem()
                self.file_table.setItem(row, col, cell)
            cell.setBackground(brush)
    
    def add_file_to_table(self, file_path: str):
        """添加文件到表格（仅显示基本信息，详细信息由异步加载）"""
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        
        # 先显示基本信息
        filename = os.path.basename(file_path)
        filename_item = QTableWidgetItem(filename)
        filename_item.setToolTip(filename)  # 设置tooltip显示完整文件名
        self.file_table.setItem(row, COL_FILENAME, filename_item)

        # 状态列（先插入占位，具体文字和颜色通过 _set_file_status 统一处理）
        status_code = self.file_status.get(file_path, STATUS_WAITING)
        self.file_status[file_path] = status_code
        status_item = QTableWidgetItem()
        status_item.setTextAlignment(Qt.AlignCenter)
        self.file_table.setItem(row, COL_STATUS, status_item)
        
        # 为其余列设置初始占位文本
        fetching_text = self.tr('FETCHING_INFO')
        for col in range(COL_RESOLUTION, COL_BITS_PER_PIXEL + 1):
            # 状态列已单独设置，这里只设置其它列
            if col in (COL_VIDEO_CODEC, COL_AUDIO_CODEC):
                item = QTableWidgetItem(fetching_text)
            else:
                item = NumericTableWidgetItem(fetching_text)
            item.setToolTip(fetching_text)
            self.file_table.setItem(row, col, item)
        
        path_item = QTableWidgetItem(file_path)
        path_item.setToolTip(file_path)  # 路径列的完整tooltip
        self.file_table.setItem(row, COL_PATH, path_item)

        # 应用当前状态的文本与颜色
        self._set_file_status(file_path, status_code)
        
        # 至少显示文件大小（即使没有FFmpeg）
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            size_str = self.format_file_size(file_size)
            size_item = NumericTableWidgetItem(size_str)
            size_item.setData(Qt.UserRole, file_size)
            size_item.setToolTip(size_str)
            self.file_table.setItem(row, COL_FILE_SIZE, size_item)
    
    def update_file_info(self, row: int, file_path: str, info: dict):
        """更新文件信息到表格"""
        na_text = self.tr('NA')
        if not info:
            # 如果信息为空，显示N/A
            for col in [COL_RESOLUTION, COL_BITRATE, COL_FRAMERATE, COL_DURATION, COL_AUDIO_BITRATE, COL_BITS_PER_PIXEL]:
                item = NumericTableWidgetItem(na_text)
                item.setToolTip(na_text)
                self.file_table.setItem(row, col, item)
            for col in [COL_VIDEO_CODEC, COL_AUDIO_CODEC]:
                item = QTableWidgetItem(na_text)
                item.setToolTip(na_text)
                self.file_table.setItem(row, col, item)
            # 至少显示文件大小
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            size_str = self.format_file_size(file_size)
            size_item = NumericTableWidgetItem(size_str)
            size_item.setData(Qt.UserRole, file_size)
            size_item.setToolTip(size_str)
            self.file_table.setItem(row, COL_FILE_SIZE, size_item)
            return
        
        # 分辨率 - 使用数字格式以便正确排序
        width = info.get('width', 0)
        height = info.get('height', 0)
        resolution = f"{width}x{height}" if width > 0 and height > 0 else "N/A"
        resolution_item = NumericTableWidgetItem(resolution)
        resolution_item.setData(Qt.UserRole, width * height)  # 存储像素总数用于排序
        resolution_item.setToolTip(resolution)  # 设置tooltip
        self.file_table.setItem(row, COL_RESOLUTION, resolution_item)
        
        # 码率（总码率）- 存储原始数值用于排序
        bitrate = info.get('format_bitrate', 0) or info.get('video_bitrate', 0)
        bitrate_str = self.format_bitrate(bitrate)
        bitrate_item = NumericTableWidgetItem(bitrate_str)
        bitrate_item.setData(Qt.UserRole, bitrate)  # 存储原始码率值
        bitrate_item.setToolTip(bitrate_str)  # 设置tooltip
        self.file_table.setItem(row, COL_BITRATE, bitrate_item)
        
        # 帧率 - 存储原始数值用于排序
        fps = info.get('fps', 0)
        fps_str = f"{fps:.2f} fps" if fps > 0 else "N/A"
        fps_item = NumericTableWidgetItem(fps_str)
        fps_item.setData(Qt.UserRole, fps)  # 存储原始帧率值
        fps_item.setToolTip(fps_str)  # 设置tooltip
        self.file_table.setItem(row, COL_FRAMERATE, fps_item)
        
        # 总时长 - 存储原始秒数用于排序
        duration = info.get('format_duration', 0) or info.get('video_duration', 0) or info.get('audio_duration', 0)
        duration_str = self.format_duration(duration)
        duration_item = NumericTableWidgetItem(duration_str)
        duration_item.setData(Qt.UserRole, duration)  # 存储原始秒数
        duration_item.setToolTip(duration_str)  # 设置tooltip
        self.file_table.setItem(row, COL_DURATION, duration_item)
        
        # 视频编码
        video_codec = info.get('video_codec', 'N/A')
        video_codec_item = QTableWidgetItem(video_codec)
        video_codec_item.setToolTip(video_codec)  # 设置tooltip
        self.file_table.setItem(row, COL_VIDEO_CODEC, video_codec_item)
        
        # 文件大小 - 存储原始字节数用于排序
        file_size = info.get('file_size', 0)
        if file_size == 0:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        size_str = self.format_file_size(file_size)
        size_item = NumericTableWidgetItem(size_str)
        size_item.setData(Qt.UserRole, file_size)  # 存储原始字节数
        size_item.setToolTip(size_str)  # 设置tooltip
        self.file_table.setItem(row, COL_FILE_SIZE, size_item)
        
        # 音频编码
        audio_codec = info.get('audio_codec', 'N/A')
        audio_codec_item = QTableWidgetItem(audio_codec)
        audio_codec_item.setToolTip(audio_codec)  # 设置tooltip
        self.file_table.setItem(row, COL_AUDIO_CODEC, audio_codec_item)
        
        # 音频码率 - 存储原始数值用于排序
        audio_bitrate = info.get('audio_bitrate', 0)
        audio_bitrate_str = self.format_bitrate(audio_bitrate)
        audio_bitrate_item = NumericTableWidgetItem(audio_bitrate_str)
        audio_bitrate_item.setData(Qt.UserRole, audio_bitrate)  # 存储原始音频码率值
        audio_bitrate_item.setToolTip(audio_bitrate_str)  # 设置tooltip
        self.file_table.setItem(row, COL_AUDIO_BITRATE, audio_bitrate_item)
        
        # 每帧每10000像素点所用的bit数 - 存储原始数值用于排序
        bits_per_10000 = info.get('bits_per_10000_pixels', 0)
        if bits_per_10000 > 0:
            bits_str = f"{bits_per_10000:.2f} bits"
        else:
            bits_str = "N/A"
        bits_item = NumericTableWidgetItem(bits_str)
        bits_item.setData(Qt.UserRole, bits_per_10000)  # 存储原始值
        bits_item.setToolTip(bits_str)  # 设置tooltip
        self.file_table.setItem(row, COL_BITS_PER_PIXEL, bits_item)

        # 更新完所有单元格后，重新应用状态对应的整行背景色
        status_code = self.file_status.get(file_path, STATUS_WAITING)
        self._set_file_status(file_path, status_code)
    
    def select_output_dir(self):
        """选择输出目录"""
        # 获取当前已设置的输出目录作为初始目录
        current_output_dir = self.config_manager.get("output_dir", "")
        # 如果目录不存在，使用其父目录；如果都没有，使用空字符串（系统默认）
        initial_dir = current_output_dir
        if current_output_dir and not os.path.exists(current_output_dir):
            # 如果目录不存在，尝试使用其父目录
            parent_dir = os.path.dirname(current_output_dir)
            if parent_dir and os.path.exists(parent_dir):
                initial_dir = parent_dir
            else:
                initial_dir = ""
        
        output_dir = QFileDialog.getExistingDirectory(
            self, 
            "选择输出目录",
            initial_dir  # 指定初始目录
        )
        if output_dir:
            self.config_manager.set("output_dir", output_dir)
            self.config_manager.save_config()
            self.output_dir_label.setText(output_dir)
            self.output_dir_label.setStyleSheet("")
    
    def load_output_dir(self):
        """加载输出目录"""
        output_dir = self.config_manager.get("output_dir", "")
        if output_dir:
            self.output_dir_label.setText(output_dir)
            self.output_dir_label.setStyleSheet("")
        else:
            self.output_dir_label.setText(self.tr('OUTPUT_DIR_NOT_SET'))
            self.output_dir_label.setStyleSheet("color: gray;")
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config_manager, self.i18n_manager, self)
        # 兼容不同Python版本的exec_()调用
        try:
            result = dialog.exec_()
        except AttributeError:
            # 如果exec_不存在，尝试exec（PyQt6使用exec）
            result = dialog.exec() if hasattr(dialog, 'exec') else QDialog.Rejected
        
        if result == QDialog.Accepted:
            # 重新初始化FFmpeg处理器
            try:
                ffmpeg_path = self.config_manager.get("ffmpeg_path", "")
                self.ffmpeg_handler = FFmpegHandler(ffmpeg_path if ffmpeg_path else "")
                self.file_processor = FileProcessor(self.ffmpeg_handler)
                self.log(self.tr('LOG_FFMPEG_UPDATED'), "success")
            except FileNotFoundError as e:
                QMessageBox.warning(self, self.tr('MSG_ERROR'), f"{self.tr('MSG_FFMPEG_INIT_FAILED')}: {str(e)}")
    
    def show_language_menu(self):
        """显示语言选择菜单"""
        menu = QMenu(self)
        languages = self.i18n_manager.get_available_languages()
        current_lang = self.i18n_manager.get_current_language()
        
        for lang_code, lang_name in languages.items():
            action = menu.addAction(lang_name)
            action.setCheckable(True)
            action.setChecked(lang_code == current_lang)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
        
        menu.exec_(self.language_btn.mapToGlobal(self.language_btn.rect().bottomLeft()))
    
    def change_language(self, lang_code: str):
        """切换语言"""
        if self.i18n_manager.set_language(lang_code):
            self.config_manager.set("language", lang_code)
            self.config_manager.save_config()
            self.retranslate_ui()
    
    def retranslate_ui(self):
        """重新翻译UI"""
        self.setWindowTitle(self.tr('MAIN_WINDOW_TITLE'))
        self.add_files_btn.setText(self.tr('ADD_FILES'))
        self.add_folder_btn.setText(self.tr('ADD_FOLDER'))
        self.remove_btn.setText(self.tr('REMOVE_SELECTED'))
        self.clear_btn.setText(self.tr('CLEAR_LIST'))
        self.language_btn.setText("Language")  # 固定显示为"Language"
        self.settings_btn.setText(self.tr('SETTINGS'))
        self.output_dir_btn.setText(self.tr('SELECT_OUTPUT_DIR'))
        self.start_btn.setText(self.tr('START_ENCODING'))
        self.stop_btn.setText(self.tr('STOP'))
        
        # 更新表格列标题
        self.file_table.setHorizontalHeaderLabels([
            self.tr('COL_FILENAME'), self.tr('COL_STATUS'), self.tr('COL_RESOLUTION'), self.tr('COL_BITRATE'),
            self.tr('COL_FRAMERATE'), self.tr('COL_DURATION'), self.tr('COL_VIDEO_CODEC'),
            self.tr('COL_FILE_SIZE'), self.tr('COL_AUDIO_CODEC'), self.tr('COL_AUDIO_BITRATE'),
            self.tr('COL_BITS_PER_PIXEL'), self.tr('COL_PATH')
        ])
        
        # 更新分组标题（使用保存的引用）
        if hasattr(self, 'list_group'):
            self.list_group.setTitle(self.tr('FILE_LIST_TITLE'))
        if hasattr(self, 'progress_group'):
            self.progress_group.setTitle(self.tr('ENCODING_PROGRESS'))
        if hasattr(self, 'log_group'):
            self.log_group.setTitle(self.tr('LOG_TITLE'))
        
        # 更新进度标签
        if hasattr(self, 'overall_label'):
            self.overall_label.setText(self.tr('OVERALL_PROGRESS') + ":")
        if hasattr(self, 'current_label'):
            self.current_label.setText(self.tr('CURRENT_FILE_PROGRESS') + ":")
        
        # 更新输出目录标签文本
        if hasattr(self, 'output_dir_text_label'):
            self.output_dir_text_label.setText(self.tr('OUTPUT_DIR') + ":")
        
        # 更新输出目录标签
        if self.output_dir_label.text() == self.tr('OUTPUT_DIR_NOT_SET') or not self.config_manager.get("output_dir", ""):
            self.output_dir_label.setText(self.tr('OUTPUT_DIR_NOT_SET'))
        else:
            self.output_dir_label.setText(self.config_manager.get("output_dir", ""))
        
        # 根据当前语言刷新文件大小总计显示
        if hasattr(self, '_last_encoded_total_size'):
            self.update_total_size_display(self._last_encoded_total_size)
        else:
            self.update_total_size_display()
    
    def start_encoding(self):
        """开始编码"""
        if not self.file_list:
            QMessageBox.warning(self, self.tr('MSG_WARNING'), self.tr('MSG_NO_FILES_ADDED'))
            return
        
        output_dir = self.config_manager.get("output_dir", "")
        if not output_dir:
            QMessageBox.warning(self, self.tr('MSG_WARNING'), self.tr('MSG_NO_OUTPUT_DIR'))
            return
        
        if not self.file_processor:
            QMessageBox.warning(self, self.tr('MSG_ERROR'), self.tr('MSG_FFMPEG_NOT_INIT'))
            return
        
        # 获取全局编码参数
        video_codec = self.config_manager.get("video_codec", "libx264")
        video_preset = self.config_manager.get("video_preset", "medium")
        video_crf = self.config_manager.get("video_crf", "23")
        video_bit_depth = self.config_manager.get("video_bit_depth", "8")
        video_resolution = self.config_manager.get("video_resolution", "")
        base_audio_codec = self.config_manager.get("audio_codec", "copy")
        base_audio_bitrate = self.config_manager.get("audio_bitrate", "")
        # 备用音频编码参数（当主编码为 copy 且不兼容 MP4 容器时使用）
        fallback_audio_codec = self.config_manager.get("fallback_audio_codec", "aac")
        fallback_audio_bitrate = self.config_manager.get("fallback_audio_bitrate", "192k")
        subtitle_mode = self.config_manager.get("subtitle_mode", "copy")
        custom_args = self.config_manager.get("custom_args", "")
        use_custom = self.config_manager.get("use_custom_command", False)
        custom_template = self.config_manager.get("custom_command_template", "")

        encode_kwargs = {
            "video_codec": video_codec,
            "video_preset": video_preset,
            "video_crf": video_crf,
            "video_bit_depth": video_bit_depth,
            "video_resolution": video_resolution,
            "audio_codec": base_audio_codec,
            "audio_bitrate": base_audio_bitrate,
            "subtitle_mode": subtitle_mode,
            "custom_args": custom_args,
            "use_custom": use_custom,
            "custom_template": custom_template
        }
        
        # 仅对状态为“等待编码”的文件进行编码
        files_to_encode = [
            path for path in self.file_list
            if self.file_status.get(path, STATUS_WAITING) == STATUS_WAITING
        ]
        if not files_to_encode:
            QMessageBox.information(self, self.tr('MSG_INFO'), self.tr('MSG_NO_FILES_ADDED'))
            return

        # 针对每个文件，根据源音频编码决定是否可以直接 copy，或需要使用备用音频编码方案
        per_file_options: Dict[str, Dict[str, object]] = {}
        for file_path in files_to_encode:
            info = self.file_info_dict.get(file_path, {})
            src_audio_codec = (info.get("audio_codec", "") or "").lower()

            audio_codec = base_audio_codec
            audio_bitrate = base_audio_bitrate

            # 仅当设置为 copy 时，才考虑是否需要启用备用方案
            if base_audio_codec == "copy":
                # 能够安全 copy 到 MP4 容器的常见音频编码
                safe_copy_codecs = {"aac", "mp3", "ac3", "eac3"}
                if src_audio_codec not in safe_copy_codecs:
                    # 使用备用音频编码器和码率
                    audio_codec = fallback_audio_codec or "aac"
                    audio_bitrate = fallback_audio_bitrate or "192k"
                    self.log(self.tr('LOG_AUDIO_CODEC_AUTO_AAC').format(bitrate=audio_bitrate), "warning")
            per_file_options[file_path] = {
                "audio_codec": audio_codec,
                "audio_bitrate": audio_bitrate,
            }

        # 创建编码工作线程
        self.encode_worker = EncodeWorker(
            self.file_processor,
            files_to_encode,
            output_dir,
            encode_kwargs,
            per_file_options=per_file_options
        )
        self.encode_worker.progress_updated.connect(self.on_progress_updated)
        self.encode_worker.file_started.connect(self.on_file_started)
        self.encode_worker.file_finished.connect(self.on_file_finished)
        self.encode_worker.finished.connect(self.on_encoding_finished)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.overall_progress_bar.setValue(0)
        self.current_file_progress_bar.setValue(0)
        self.overall_progress_label.setText(self.tr('PREPARING'))
        self.current_file_label.setText("")
        
        # 显示并重置任务栏进度条（仅 Windows）
        if HAS_WIN_TASKBAR and hasattr(self, 'taskbar_progress'):
            self.taskbar_progress.setValue(0)
            self.taskbar_progress.setVisible(True)
        
        # 启动编码
        self.encode_worker.start()
        self.log(self.tr('LOG_START_ENCODING').format(count=len(self.file_list)), "info")
    
    def stop_encoding(self):
        """停止编码"""
        if self.encode_worker:
            self.encode_worker.cancel()
            self.log(self.tr('STOPPING'), "warning")
            
            # 隐藏任务栏进度条（仅 Windows）
            if HAS_WIN_TASKBAR and hasattr(self, 'taskbar_progress'):
                self.taskbar_progress.setVisible(False)
    
    def on_file_started(self, current: int, total: int, file_path: str):
        """文件开始编码"""
        filename = os.path.basename(file_path)
        # 更新状态为"正在编码"
        self._set_file_status(file_path, STATUS_ENCODING)
        self.log(self.tr('LOG_FILE_STARTED').format(
            current=current, total=total, filename=filename
        ), "info")
    
    def on_file_finished(self, current: int, total: int, file_path: str, success: bool, message: str):
        """文件结束编码"""
        filename = os.path.basename(file_path)
        if success:
            # 更新状态为"编码完成"
            self._set_file_status(file_path, STATUS_DONE)
            self.log(self.tr('LOG_FILE_FINISHED_SUCCESS').format(
                current=current, total=total, filename=filename, message=message
            ), "success")
        else:
            # 更新状态为"编码失败"
            self._set_file_status(file_path, STATUS_FAILED)
            # 失败时输出详细错误信息（message中已包含详细错误）
            self.log(self.tr('LOG_FILE_FINISHED_FAILED').format(
                current=current, total=total, filename=filename, message=message
            ), "error")
    
    def on_progress_updated(self, current: int, total: int, file_path: str, progress: float, message: str):
        """进度更新"""
        # 更新当前文件进度条
        self.current_file_progress_bar.setValue(int(progress))
        self.current_file_label.setText(self.tr('CURRENT_FILE_FORMAT').format(
            filename=os.path.basename(file_path), message=message
        ))
        
        # 计算并更新总体进度条
        # 总体进度 = (已完成文件数 * 100 + 当前文件进度) / 总文件数
        overall_progress = ((current - 1) * 100 + progress) / total if total > 0 else 0
        overall_progress_int = int(overall_progress)
        self.overall_progress_bar.setValue(overall_progress_int)
        self.overall_progress_label.setText(self.tr('PROGRESS_FORMAT').format(
            current=current, total=total, percent=overall_progress_int
        ))
        
        # 更新任务栏进度条（仅 Windows）
        if HAS_WIN_TASKBAR and hasattr(self, 'taskbar_progress'):
            self.taskbar_progress.setValue(overall_progress_int)
    
    def on_encoding_finished(self, results: list):
        """编码完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 统计结果
        success_count = sum(1 for _, _, success, _ in results if success)
        total_count = len(results)

        # 计算编码后文件总大小
        encoded_total_size = 0
        for _, output_path, success, _ in results:
            if success and output_path and os.path.exists(output_path):
                try:
                    encoded_total_size += os.path.getsize(output_path)
                except OSError:
                    pass
        # 更新文件大小总计显示（源文件加编码后总大小）
        if encoded_total_size > 0:
            self.update_total_size_display(encoded_total_size)
        
        self.overall_progress_bar.setValue(100)
        self.current_file_progress_bar.setValue(100)
        self.overall_progress_label.setText(self.tr('ENCODING_COMPLETE_FORMAT').format(
            success=success_count, total=total_count
        ))
        self.current_file_label.setText("")
        
        # 隐藏任务栏进度条（仅 Windows）
        if HAS_WIN_TASKBAR and hasattr(self, 'taskbar_progress'):
            self.taskbar_progress.setValue(100)
            self.taskbar_progress.setVisible(False)
        
        # 队列完成后根据设置播放提示音（在显示消息框之前播放）
        self.play_completion_sound()
        
        # 显示结果（使用QMessageBox.information，确保不会导致程序退出）
        msg_box = QMessageBox(self)
        # 使用NoIcon避免触发Windows系统提示音
        msg_box.setIcon(QMessageBox.NoIcon)
        msg_box.setWindowTitle(self.tr('MSG_ENCODING_COMPLETE'))
        msg_box.setText(
            f"{self.tr('MSG_ENCODING_COMPLETE')}\n{self.tr('MSG_ENCODING_SUCCESS')}: {success_count}\n{self.tr('MSG_ENCODING_FAILED')}: {total_count - success_count}"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
        # 记录日志
        for file_path, _, success, msg in results:
            status = "✓" if success else "✗"
            log_type = "success" if success else "error"
            self.log(f"{status} {os.path.basename(file_path)}: {msg}", log_type)
    
    def log(self, message: str, log_type: str = "info"):
        """
        记录日志
        
        Args:
            message: 日志消息
            log_type: 日志类型 ("info", "success", "warning", "error")
        """
        # 定义不同日志类型的颜色
        colors = {
            "info": "#000000",      # 黑色（默认）
            "success": "#008000",    # 绿色
            "warning": "#FF8C00",   # 橙色
            "error": "#DC143C",      # 红色
        }
        
        color = colors.get(log_type, colors["info"])
        
        # 使用HTML格式设置颜色
        html_message = f'<span style="color: {color};">{self._escape_html(message)}</span>'
        self.log_text.append(html_message)
    
    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\"", "&quot;")
                    .replace("'", "&#39;")
                    .replace("\n", "<br>"))

    def play_completion_sound(self):
        """根据设置播放队列完成提示音"""
        if not self.config_manager.get("notification_sound_enabled", False):
            return
        sound_file = self.config_manager.get("notification_sound_file", "")
        if not sound_file or not os.path.exists(sound_file):
            return

        # 懒加载播放器，避免在未使用时初始化多媒体模块
        player = getattr(self, "_notification_player", None)
        if player is None:
            player = QMediaPlayer(self)
            self._notification_player = player
        url = QUrl.fromLocalFile(sound_file)
        player.setMedia(QMediaContent(url))
        player.setVolume(100)
        player.play()

    def showEvent(self, event):
        """窗口显示时关联任务栏按钮（仅 Windows）"""
        super().showEvent(event)
        if HAS_WIN_TASKBAR and hasattr(self, 'taskbar_button'):
            try:
                # 窗口显示后，将任务栏按钮关联到窗口
                self.taskbar_button.setWindow(self.windowHandle())
            except Exception:
                # 如果失败，忽略错误（可能在某些情况下窗口句柄还未准备好）
                pass
    
    def closeEvent(self, event):
        """窗口关闭时保存窗口大小和位置"""
        try:
            size = self.size()
            pos = self.pos()
            self.config_manager.set("window_width", size.width())
            self.config_manager.set("window_height", size.height())
            self.config_manager.set("window_pos_x", pos.x())
            self.config_manager.set("window_pos_y", pos.y())
            self.config_manager.save_config()
        except Exception:
            pass
        super().closeEvent(event)

