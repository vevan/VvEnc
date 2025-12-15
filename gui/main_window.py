"""
主窗口 - 视频编码工具主界面
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QProgressBar, QLabel,
    QFileDialog, QMessageBox, QListWidgetItem, QGroupBox,
    QTextEdit, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from core.config_manager import ConfigManager
from core.ffmpeg_handler import FFmpegHandler
from core.file_processor import FileProcessor
from gui.settings_dialog import SettingsDialog


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
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.ffmpeg_handler = None
        self.file_processor = None
        self.encode_worker = None
        self.file_list = []  # 待编码文件列表
        self.init_ffmpeg()
        self.init_ui()
        self.load_output_dir()
    
    def init_ffmpeg(self):
        """初始化FFmpeg处理器"""
        try:
            ffmpeg_path = self.config_manager.get("ffmpeg_path", "")
            self.ffmpeg_handler = FFmpegHandler(ffmpeg_path if ffmpeg_path else "")
            self.file_processor = FileProcessor(self.ffmpeg_handler)
        except FileNotFoundError as e:
            QMessageBox.warning(
                self,
                "FFmpeg未找到",
                f"{str(e)}\n\n请在设置中指定FFmpeg路径。"
            )
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("批量视频编码工具")
        self.setMinimumSize(800, 600)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("添加文件")
        self.add_files_btn.clicked.connect(self.add_files)
        toolbar_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_folder)
        toolbar_layout.addWidget(self.add_folder_btn)
        
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        toolbar_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_list)
        toolbar_layout.addWidget(self.clear_btn)
        
        toolbar_layout.addStretch()
        
        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.show_settings)
        toolbar_layout.addWidget(self.settings_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 文件列表
        list_group = QGroupBox("待编码文件列表")
        list_layout = QVBoxLayout()
        
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        list_layout.addWidget(self.file_list_widget)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        
        self.output_dir_label = QLabel("未设置")
        self.output_dir_label.setStyleSheet("color: gray;")
        output_layout.addWidget(self.output_dir_label)
        
        self.output_dir_btn = QPushButton("选择输出目录")
        self.output_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_btn)
        
        layout.addLayout(output_layout)
        
        # 进度显示
        progress_group = QGroupBox("编码进度")
        progress_layout = QVBoxLayout()
        
        # 总体进度
        overall_label = QLabel("总体进度:")
        progress_layout.addWidget(overall_label)
        
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setRange(0, 100)
        self.overall_progress_bar.setValue(0)
        progress_layout.addWidget(self.overall_progress_bar)
        
        self.overall_progress_label = QLabel("等待开始...")
        progress_layout.addWidget(self.overall_progress_label)
        
        # 分隔线
        progress_layout.addSpacing(10)
        
        # 当前文件进度
        current_label = QLabel("当前文件进度:")
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
        
        self.start_btn = QPushButton("开始编码")
        self.start_btn.clicked.connect(self.start_encoding)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_encoding)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 日志区域
        log_group = QGroupBox("日志")
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
            QMessageBox.warning(self, "错误", "FFmpeg未初始化，请检查设置")
            return
        
        files = self.file_processor.scan_files(path)
        if not files:
            QMessageBox.information(self, "提示", "未找到视频文件")
            return
        
        # 添加到列表
        for file_path in files:
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                item = QListWidgetItem(file_path)
                self.file_list_widget.addItem(item)
        
        self.log(f"添加了 {len(files)} 个文件")
    
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.3gp *.ts *.mts);;所有文件 (*.*)"
        )
        for file_path in files:
            self.add_path(file_path)
    
    def add_folder(self):
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.add_path(folder)
    
    def remove_selected(self):
        """移除选中的文件"""
        selected_items = self.file_list_widget.selectedItems()
        for item in selected_items:
            row = self.file_list_widget.row(item)
            self.file_list.pop(row)
            self.file_list_widget.takeItem(row)
    
    def clear_list(self):
        """清空列表"""
        self.file_list.clear()
        self.file_list_widget.clear()
    
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
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
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
                self.log("FFmpeg设置已更新")
            except FileNotFoundError as e:
                QMessageBox.warning(self, "错误", f"FFmpeg初始化失败: {str(e)}")
    
    def start_encoding(self):
        """开始编码"""
        if not self.file_list:
            QMessageBox.warning(self, "警告", "请先添加要编码的文件")
            return
        
        output_dir = self.config_manager.get("output_dir", "")
        if not output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return
        
        if not self.file_processor:
            QMessageBox.warning(self, "错误", "FFmpeg未初始化")
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
        self.overall_progress_label.setText("准备开始...")
        self.current_file_label.setText("")
        
        # 启动编码
        self.encode_worker.start()
        self.log(f"开始编码 {len(self.file_list)} 个文件")
    
    def stop_encoding(self):
        """停止编码"""
        if self.encode_worker:
            self.encode_worker.cancel()
            self.log("正在停止编码...")
    
    def on_progress_updated(self, current: int, total: int, file_path: str, progress: float, message: str):
        """进度更新"""
        # 更新当前文件进度条
        self.current_file_progress_bar.setValue(int(progress))
        self.current_file_label.setText(f"{os.path.basename(file_path)} - {message}")
        
        # 计算并更新总体进度条
        # 总体进度 = (已完成文件数 * 100 + 当前文件进度) / 总文件数
        overall_progress = ((current - 1) * 100 + progress) / total if total > 0 else 0
        self.overall_progress_bar.setValue(int(overall_progress))
        self.overall_progress_label.setText(f"总体进度: {current}/{total} 个文件 ({int(overall_progress)}%)")
    
    def on_encoding_finished(self, results: list):
        """编码完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 统计结果
        success_count = sum(1 for _, success, _ in results if success)
        total_count = len(results)
        
        self.overall_progress_bar.setValue(100)
        self.current_file_progress_bar.setValue(100)
        self.overall_progress_label.setText(f"编码完成: {success_count}/{total_count} 成功")
        self.current_file_label.setText("")
        
        # 显示结果
        QMessageBox.information(
            self,
            "编码完成",
            f"编码完成！\n成功: {success_count}\n失败: {total_count - success_count}"
        )
        
        # 记录日志
        for file_path, success, msg in results:
            status = "✓" if success else "✗"
            self.log(f"{status} {os.path.basename(file_path)}: {msg}")
    
    def log(self, message: str):
        """记录日志"""
        self.log_text.append(message)

