"""
主窗口 - 视频编码工具主界面
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QProgressBar, QLabel,
    QFileDialog, QMessageBox, QListWidgetItem, QGroupBox,
    QTextEdit, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMenu
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from core.config_manager import ConfigManager
from core.ffmpeg_handler import FFmpegHandler
from core.file_processor import FileProcessor
from gui.settings_dialog import SettingsDialog
from translations import LanguageManager


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


class EncodeWorker(QThread):
    """编码工作线程"""
    progress_updated = pyqtSignal(int, int, str, float, str)  # current, total, file, progress, message
    finished = pyqtSignal(list)  # results
    
    def __init__(self, file_processor: FileProcessor, files: list, output_dir: str, encode_kwargs: dict):
        super().__init__()
        self.file_processor = file_processor
        self.files = files
        self.output_dir = output_dir
        self.encode_kwargs = encode_kwargs
        self.cancelled = False
    
    def run(self):
        """执行编码任务"""
        results = self.file_processor.process_files(
            self.files,
            self.output_dir,
            progress_callback=self.on_progress,
            cancel_flag=lambda: self.cancelled,
            **self.encode_kwargs
        )
        if not self.cancelled:
            self.finished.emit(results)
        else:
            # 即使取消也发送结果
            self.finished.emit(results)
    
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
        list_group = QGroupBox(self.tr('FILE_LIST_TITLE'))
        list_layout = QVBoxLayout()
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(11)  # 增加总时长列
        self.file_table.setHorizontalHeaderLabels([
            self.tr('COL_FILENAME'), self.tr('COL_RESOLUTION'), self.tr('COL_BITRATE'),
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
        
        # 加载保存的列顺序和列宽
        self.load_table_settings()
        
        # 默认列宽（如果配置中没有）
        default_widths = {
            0: 200,  # 文件名
            1: 100,  # 分辨率
            2: 100,  # 码率
            3: 80,   # 帧率
            4: 100,  # 总时长
            5: 100,  # 视频编码
            6: 100,  # 文件大小
            7: 100,  # 音频编码
            8: 100,  # 音频码率
            9: 150,  # 每帧/10000像素bit数
        }
        
        # 应用列宽
        for col, width in default_widths.items():
            if self.file_table.columnWidth(col) == 100:  # 默认宽度，应用自定义宽度
                self.file_table.setColumnWidth(col, width)
        
        self.file_table.setColumnHidden(10, True)  # 隐藏路径列
        
        list_layout.addWidget(self.file_table)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel(self.tr('OUTPUT_DIR') + ":"))
        
        self.output_dir_label = QLabel(self.tr('OUTPUT_DIR_NOT_SET'))
        self.output_dir_label.setStyleSheet("color: gray;")
        output_layout.addWidget(self.output_dir_label)
        
        self.output_dir_btn = QPushButton(self.tr('SELECT_OUTPUT_DIR'))
        self.output_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_btn)
        
        layout.addLayout(output_layout)
        
        # 进度显示
        progress_group = QGroupBox(self.tr('ENCODING_PROGRESS'))
        progress_layout = QVBoxLayout()
        
        # 总体进度
        overall_label = QLabel(self.tr('OVERALL_PROGRESS') + ":")
        progress_layout.addWidget(overall_label)
        
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setRange(0, 100)
        self.overall_progress_bar.setValue(0)
        progress_layout.addWidget(self.overall_progress_bar)
        
        self.overall_progress_label = QLabel(self.tr('WAITING'))
        progress_layout.addWidget(self.overall_progress_label)
        
        # 分隔线
        progress_layout.addSpacing(10)
        
        # 当前文件进度
        current_label = QLabel(self.tr('CURRENT_FILE_PROGRESS') + ":")
        progress_layout.addWidget(current_label)
        
        self.current_file_progress_bar = QProgressBar()
        self.current_file_progress_bar.setRange(0, 100)
        self.current_file_progress_bar.setValue(0)
        progress_layout.addWidget(self.current_file_progress_bar)
        
        self.current_file_label = QLabel("")
        progress_layout.addWidget(self.current_file_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
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
        
        # 日志区域
        log_group = QGroupBox(self.tr('LOG_TITLE'))
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
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
        
        # 添加到列表并获取详细信息
        for file_path in files:
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                # 获取文件详细信息
                self.add_file_to_table(file_path)
        
        self.log(self.tr('LOG_FILES_ADDED').format(count=len(files)))
    
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr('SELECT_VIDEO_FILES'),
            "",
            self.tr('VIDEO_FILES_FILTER')
        )
        for file_path in files:
            self.add_path(file_path)
    
    def add_folder(self):
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(self, self.tr('SELECT_FOLDER'))
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
                self.file_table.removeRow(row)
    
    def clear_list(self):
        """清空列表"""
        self.file_list.clear()
        self.file_info_dict.clear()
        self.file_table.setRowCount(0)
    
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
    
    def add_file_to_table(self, file_path: str):
        """添加文件到表格并获取详细信息"""
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        
        # 先显示基本信息
        filename = os.path.basename(file_path)
        filename_item = QTableWidgetItem(filename)
        filename_item.setToolTip(filename)  # 设置tooltip显示完整文件名
        self.file_table.setItem(row, 0, filename_item)
        
        # 为所有列设置初始tooltip
        fetching_text = self.tr('FETCHING_INFO')
        for col in range(1, 10):
            item = NumericTableWidgetItem(fetching_text) if col not in [5, 7] else QTableWidgetItem(fetching_text)
            item.setToolTip(fetching_text)
            self.file_table.setItem(row, col, item)
        
        path_item = QTableWidgetItem(file_path)
        path_item.setToolTip(file_path)  # 路径列的完整tooltip
        self.file_table.setItem(row, 10, path_item)
        
        # 异步获取详细信息
        if self.ffmpeg_handler:
            try:
                info = self.ffmpeg_handler.get_detailed_video_info(file_path)
                self.file_info_dict[file_path] = info
                # 临时禁用排序，更新信息
                self.file_table.setSortingEnabled(False)
                self.update_file_info(row, file_path, info)
                self.file_table.setSortingEnabled(True)
            except Exception as e:
                self.log(f"获取文件信息失败 {filename}: {str(e)}")
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
            size_item.setToolTip(size_str)  # 设置tooltip
            self.file_table.setItem(row, 6, size_item)
            self.update_file_info(row, file_path, {})
            self.file_table.setSortingEnabled(True)
    
    def update_file_info(self, row: int, file_path: str, info: dict):
        """更新文件信息到表格"""
        na_text = self.tr('NA')
        if not info:
            # 如果信息为空，显示N/A
            for col in [1, 2, 3, 4, 8, 9]:
                item = NumericTableWidgetItem(na_text)
                item.setToolTip(na_text)
                self.file_table.setItem(row, col, item)
            for col in [5, 7]:
                item = QTableWidgetItem(na_text)
                item.setToolTip(na_text)
                self.file_table.setItem(row, col, item)
            # 至少显示文件大小
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            size_str = self.format_file_size(file_size)
            size_item = NumericTableWidgetItem(size_str)
            size_item.setData(Qt.UserRole, file_size)
            size_item.setToolTip(size_str)
            self.file_table.setItem(row, 6, size_item)
            return
        
        # 分辨率 - 使用数字格式以便正确排序
        width = info.get('width', 0)
        height = info.get('height', 0)
        resolution = f"{width}x{height}" if width > 0 and height > 0 else "N/A"
        resolution_item = NumericTableWidgetItem(resolution)
        resolution_item.setData(Qt.UserRole, width * height)  # 存储像素总数用于排序
        resolution_item.setToolTip(resolution)  # 设置tooltip
        self.file_table.setItem(row, 1, resolution_item)
        
        # 码率（总码率）- 存储原始数值用于排序
        bitrate = info.get('format_bitrate', 0) or info.get('video_bitrate', 0)
        bitrate_str = self.format_bitrate(bitrate)
        bitrate_item = NumericTableWidgetItem(bitrate_str)
        bitrate_item.setData(Qt.UserRole, bitrate)  # 存储原始码率值
        bitrate_item.setToolTip(bitrate_str)  # 设置tooltip
        self.file_table.setItem(row, 2, bitrate_item)
        
        # 帧率 - 存储原始数值用于排序
        fps = info.get('fps', 0)
        fps_str = f"{fps:.2f} fps" if fps > 0 else "N/A"
        fps_item = NumericTableWidgetItem(fps_str)
        fps_item.setData(Qt.UserRole, fps)  # 存储原始帧率值
        fps_item.setToolTip(fps_str)  # 设置tooltip
        self.file_table.setItem(row, 3, fps_item)
        
        # 总时长 - 存储原始秒数用于排序
        duration = info.get('format_duration', 0) or info.get('video_duration', 0) or info.get('audio_duration', 0)
        duration_str = self.format_duration(duration)
        duration_item = NumericTableWidgetItem(duration_str)
        duration_item.setData(Qt.UserRole, duration)  # 存储原始秒数
        duration_item.setToolTip(duration_str)  # 设置tooltip
        self.file_table.setItem(row, 4, duration_item)
        
        # 视频编码
        video_codec = info.get('video_codec', 'N/A')
        video_codec_item = QTableWidgetItem(video_codec)
        video_codec_item.setToolTip(video_codec)  # 设置tooltip
        self.file_table.setItem(row, 5, video_codec_item)
        
        # 文件大小 - 存储原始字节数用于排序
        file_size = info.get('file_size', 0)
        if file_size == 0:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        size_str = self.format_file_size(file_size)
        size_item = NumericTableWidgetItem(size_str)
        size_item.setData(Qt.UserRole, file_size)  # 存储原始字节数
        size_item.setToolTip(size_str)  # 设置tooltip
        self.file_table.setItem(row, 6, size_item)
        
        # 音频编码
        audio_codec = info.get('audio_codec', 'N/A')
        audio_codec_item = QTableWidgetItem(audio_codec)
        audio_codec_item.setToolTip(audio_codec)  # 设置tooltip
        self.file_table.setItem(row, 7, audio_codec_item)
        
        # 音频码率 - 存储原始数值用于排序
        audio_bitrate = info.get('audio_bitrate', 0)
        audio_bitrate_str = self.format_bitrate(audio_bitrate)
        audio_bitrate_item = NumericTableWidgetItem(audio_bitrate_str)
        audio_bitrate_item.setData(Qt.UserRole, audio_bitrate)  # 存储原始音频码率值
        audio_bitrate_item.setToolTip(audio_bitrate_str)  # 设置tooltip
        self.file_table.setItem(row, 8, audio_bitrate_item)
        
        # 每帧每10000像素点所用的bit数 - 存储原始数值用于排序
        bits_per_10000 = info.get('bits_per_10000_pixels', 0)
        if bits_per_10000 > 0:
            bits_str = f"{bits_per_10000:.2f} bits"
        else:
            bits_str = "N/A"
        bits_item = NumericTableWidgetItem(bits_str)
        bits_item.setData(Qt.UserRole, bits_per_10000)  # 存储原始值
        bits_item.setToolTip(bits_str)  # 设置tooltip
        self.file_table.setItem(row, 9, bits_item)
    
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
                self.log(self.tr('LOG_FFMPEG_UPDATED'))
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
            self.tr('COL_FILENAME'), self.tr('COL_RESOLUTION'), self.tr('COL_BITRATE'),
            self.tr('COL_FRAMERATE'), self.tr('COL_DURATION'), self.tr('COL_VIDEO_CODEC'),
            self.tr('COL_FILE_SIZE'), self.tr('COL_AUDIO_CODEC'), self.tr('COL_AUDIO_BITRATE'),
            self.tr('COL_BITS_PER_PIXEL'), self.tr('COL_PATH')
        ])
        
        # 更新分组标题
        for widget in self.findChildren(QGroupBox):
            if widget.title() == "待编码文件列表" or widget.title() == "Files to Encode":
                widget.setTitle(self.tr('FILE_LIST_TITLE'))
            elif "编码进度" in widget.title() or "Encoding Progress" in widget.title():
                widget.setTitle(self.tr('ENCODING_PROGRESS'))
        
        # 更新输出目录标签
        if self.output_dir_label.text() == self.tr('OUTPUT_DIR_NOT_SET') or not self.config_manager.get("output_dir", ""):
            self.output_dir_label.setText(self.tr('OUTPUT_DIR_NOT_SET'))
        else:
            self.output_dir_label.setText(self.config_manager.get("output_dir", ""))
    
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
        
        # 获取编码参数
        encode_kwargs = {
            "video_codec": self.config_manager.get("video_codec", "libx264"),
            "video_preset": self.config_manager.get("video_preset", "medium"),
            "video_crf": self.config_manager.get("video_crf", "23"),
            "video_bit_depth": self.config_manager.get("video_bit_depth", "8"),
            "video_resolution": self.config_manager.get("video_resolution", ""),
            "audio_codec": self.config_manager.get("audio_codec", "copy"),
            "audio_bitrate": self.config_manager.get("audio_bitrate", ""),
            "subtitle_mode": self.config_manager.get("subtitle_mode", "copy"),
            "custom_args": self.config_manager.get("custom_args", ""),
            "use_custom": self.config_manager.get("use_custom_command", False),
            "custom_template": self.config_manager.get("custom_command_template", "")
        }
        
        # 创建编码工作线程
        self.encode_worker = EncodeWorker(
            self.file_processor,
            self.file_list.copy(),
            output_dir,
            encode_kwargs
        )
        self.encode_worker.progress_updated.connect(self.on_progress_updated)
        self.encode_worker.finished.connect(self.on_encoding_finished)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.overall_progress_bar.setValue(0)
        self.current_file_progress_bar.setValue(0)
        self.overall_progress_label.setText(self.tr('PREPARING'))
        self.current_file_label.setText("")
        
        # 启动编码
        self.encode_worker.start()
        self.log(self.tr('LOG_START_ENCODING').format(count=len(self.file_list)))
    
    def stop_encoding(self):
        """停止编码"""
        if self.encode_worker:
            self.encode_worker.cancel()
            self.log(self.tr('STOPPING'))
    
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
        self.overall_progress_bar.setValue(int(overall_progress))
        self.overall_progress_label.setText(self.tr('PROGRESS_FORMAT').format(
            current=current, total=total, percent=int(overall_progress)
        ))
    
    def on_encoding_finished(self, results: list):
        """编码完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 统计结果
        success_count = sum(1 for _, success, _ in results if success)
        total_count = len(results)
        
        self.overall_progress_bar.setValue(100)
        self.current_file_progress_bar.setValue(100)
        self.overall_progress_label.setText(self.tr('ENCODING_COMPLETE_FORMAT').format(
            success=success_count, total=total_count
        ))
        self.current_file_label.setText("")
        
        # 显示结果
        QMessageBox.information(
            self,
            self.tr('MSG_ENCODING_COMPLETE'),
            f"{self.tr('MSG_ENCODING_COMPLETE')}\n{self.tr('MSG_ENCODING_SUCCESS')}: {success_count}\n{self.tr('MSG_ENCODING_FAILED')}: {total_count - success_count}"
        )
        
        # 记录日志
        for file_path, success, msg in results:
            status = "✓" if success else "✗"
            self.log(f"{status} {os.path.basename(file_path)}: {msg}")
    
    def log(self, message: str):
        """记录日志"""
        self.log_text.append(message)

