"""
设置对话框 - 编码参数配置
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QComboBox, QSpinBox,
    QCheckBox, QTextEdit, QFileDialog, QGroupBox,
    QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from core.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("编码设置")
        self.setMinimumWidth(600)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # FFmpeg路径设置
        ffmpeg_group = QGroupBox("FFmpeg设置")
        ffmpeg_layout = QFormLayout()
        
        self.ffmpeg_path_edit = QLineEdit()
        self.ffmpeg_path_edit.setToolTip(
            "FFmpeg可执行文件的完整路径。\n"
            "如果留空，程序将尝试从系统PATH环境变量中查找FFmpeg。\n"
            "如果系统PATH中没有FFmpeg，请在此处指定完整路径。"
        )
        self.ffmpeg_browse_btn = QPushButton("浏览...")
        self.ffmpeg_browse_btn.clicked.connect(self.browse_ffmpeg)
        ffmpeg_path_layout = QHBoxLayout()
        ffmpeg_path_layout.addWidget(self.ffmpeg_path_edit)
        ffmpeg_path_layout.addWidget(self.ffmpeg_browse_btn)
        ffmpeg_layout.addRow("FFmpeg路径:", ffmpeg_path_layout)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        # 视频编码参数
        video_group = QGroupBox("视频编码参数")
        video_layout = QFormLayout()
        
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems([
            "libx264", 
            "libx265", 
            "libsvtav1",  # AV1软件编码
            "av1_nvenc",  # AV1 NVenc硬件编码
            "h264_nvenc",  # H.264 NVenc
            "hevc_nvenc",  # HEVC NVenc
            "copy"
        ])
        self.video_codec_combo.setToolTip(
            "选择视频编码器：\n"
            "• libx264: H.264软件编码，兼容性好，速度中等\n"
            "• libx265: HEVC软件编码，压缩率高，速度较慢\n"
            "• libsvtav1: AV1软件编码，最新标准，压缩率最高，速度最慢\n"
            "• av1_nvenc: AV1硬件编码（NVIDIA GPU），需要RTX 40系列或更新\n"
            "• h264_nvenc: H.264硬件编码（NVIDIA GPU），速度快\n"
            "• hevc_nvenc: HEVC硬件编码（NVIDIA GPU），速度快，压缩率高\n"
            "• copy: 直接复制视频流，不进行重新编码"
        )
        self.video_codec_combo.currentTextChanged.connect(self.on_codec_changed)
        video_layout.addRow("视频编码器:", self.video_codec_combo)
        
        self.video_preset_combo = QComboBox()
        self.video_preset_combo.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
        self.video_preset_combo.setToolTip(
            "编码预设（速度与质量平衡）：\n"
            "• ultrafast ~ faster: 编码速度快，文件较大，质量略低\n"
            "• medium: 平衡选择（推荐）\n"
            "• slow ~ veryslow: 编码速度慢，文件较小，质量更高\n"
            "注意：NVenc编码器使用p1-p7预设（p1最快，p7最慢）"
        )
        video_layout.addRow("编码预设:", self.video_preset_combo)
        
        self.video_crf_spin = QSpinBox()
        self.video_crf_spin.setRange(0, 51)
        self.video_crf_spin.setValue(23)
        self.video_crf_spin.setToolTip(
            "CRF（恒定速率因子）质量参数：\n"
            "• 0: 最高质量，文件最大（无损）\n"
            "• 18-23: 高质量范围（推荐23）\n"
            "• 28-32: 中等质量，文件较小\n"
            "• 51: 最低质量，文件最小\n"
            "注意：NVenc编码器使用CQ参数（0-51），含义类似"
        )
        video_layout.addRow("CRF质量 (0-51):", self.video_crf_spin)
        
        self.video_bit_depth_combo = QComboBox()
        self.video_bit_depth_combo.addItems(["8", "10"])
        self.video_bit_depth_combo.setCurrentText("8")
        self.video_bit_depth_combo.setToolTip(
            "视频位深度：\n"
            "• 8bit: 标准位深度，兼容性好，文件较小\n"
            "• 10bit: 高精度，色彩渐变更平滑，暗部细节更好\n"
            "注意：10bit编码需要编码器支持，文件会更大，编码时间更长"
        )
        video_layout.addRow("位深度:", self.video_bit_depth_combo)
        
        self.video_resolution_edit = QLineEdit()
        self.video_resolution_edit.setPlaceholderText("例如: 1920:1080 或留空保持原分辨率")
        self.video_resolution_edit.setToolTip(
            "输出视频分辨率（宽度:高度）：\n"
            "• 格式：宽度:高度，例如 1920:1080（1080p）\n"
            "• 留空：保持原始分辨率\n"
            "• 常用分辨率：\n"
            "  - 4K: 3840:2160\n"
            "  - 1080p: 1920:1080\n"
            "  - 720p: 1280:720\n"
            "  - 480p: 854:480"
        )
        video_layout.addRow("分辨率 (宽:高):", self.video_resolution_edit)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # 音频编码参数
        audio_group = QGroupBox("音频编码参数")
        audio_layout = QFormLayout()
        
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["copy", "aac", "mp3", "opus"])
        self.audio_codec_combo.setToolTip(
            "音频编码器：\n"
            "• copy: 直接复制音频流，不重新编码（推荐，速度快）\n"
            "• aac: AAC编码，兼容性好，质量高\n"
            "• mp3: MP3编码，兼容性最好\n"
            "• opus: Opus编码，压缩率高，质量好"
        )
        audio_layout.addRow("音频编码器:", self.audio_codec_combo)
        
        self.audio_bitrate_edit = QLineEdit()
        self.audio_bitrate_edit.setPlaceholderText("例如: 128k")
        self.audio_bitrate_edit.setToolTip(
            "音频码率（仅在重新编码时有效）：\n"
            "• 格式：数值+k，例如 128k, 192k, 256k\n"
            "• 推荐值：\n"
            "  - 语音: 64k-96k\n"
            "  - 音乐: 128k-192k\n"
            "  - 高质量: 256k-320k\n"
            "• 选择'copy'时此参数无效"
        )
        audio_layout.addRow("音频码率:", self.audio_bitrate_edit)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 字幕设置
        subtitle_group = QGroupBox("字幕设置")
        subtitle_layout = QFormLayout()
        
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.addItems(["copy", "embed", "none"])
        self.subtitle_combo.setToolTip(
            "字幕处理方式：\n"
            "• copy: 直接复制字幕流（推荐）\n"
            "• embed: 嵌入字幕到视频（需要源文件支持）\n"
            "• none: 不处理字幕，移除字幕流"
        )
        subtitle_layout.addRow("字幕处理:", self.subtitle_combo)
        
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        # 自定义参数
        custom_group = QGroupBox("自定义参数")
        custom_layout = QVBoxLayout()
        
        self.use_custom_check = QCheckBox("使用自定义FFmpeg命令行")
        self.use_custom_check.setToolTip(
            "启用后，将使用下方自定义命令模板，忽略其他编码参数设置"
        )
        custom_layout.addWidget(self.use_custom_check)
        
        self.custom_command_edit = QTextEdit()
        self.custom_command_edit.setPlaceholderText(
            "使用 {input} 和 {output} 作为占位符\n"
            "例如: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}"
        )
        self.custom_command_edit.setMaximumHeight(100)
        self.custom_command_edit.setToolTip(
            "自定义FFmpeg命令模板：\n"
            "• {input}: 输入文件路径（自动替换）\n"
            "• {output}: 输出文件路径（自动替换）\n"
            "• 示例：ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}\n"
            "注意：启用此选项后，其他编码参数将被忽略"
        )
        custom_layout.addWidget(self.custom_command_edit)
        
        self.custom_args_edit = QLineEdit()
        self.custom_args_edit.setPlaceholderText("额外的FFmpeg参数（空格分隔）")
        self.custom_args_edit.setToolTip(
            "额外的FFmpeg参数（在标准参数之后添加）：\n"
            "• 格式：空格分隔的参数，例如 '-threads 4 -movflags +faststart'\n"
            "• 这些参数会追加到自动生成的FFmpeg命令末尾\n"
            "• 仅在未启用自定义命令时有效"
        )
        custom_layout.addWidget(self.custom_args_edit)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def on_codec_changed(self, codec: str):
        """编码器改变时的处理"""
        # NVenc编码器使用不同的预设选项
        if codec in ["av1_nvenc", "h264_nvenc", "hevc_nvenc"]:
            self.video_preset_combo.clear()
            self.video_preset_combo.addItems([
                "p1",  # 最快（最低质量）
                "p2",
                "p3",
                "p4",  # 默认
                "p5",
                "p6",
                "p7"   # 最慢（最高质量）
            ])
            self.video_preset_combo.setCurrentText("p4")
        else:
            # 软件编码器使用标准预设
            current_preset = self.video_preset_combo.currentText()
            self.video_preset_combo.clear()
            self.video_preset_combo.addItems([
                "ultrafast", "superfast", "veryfast", "faster", 
                "fast", "medium", "slow", "slower", "veryslow"
            ])
            # 尝试恢复之前的预设，如果不存在则使用medium
            if current_preset in ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]:
                self.video_preset_combo.setCurrentText(current_preset)
            else:
                self.video_preset_combo.setCurrentText("medium")
    
    def browse_ffmpeg(self):
        """浏览FFmpeg路径"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择FFmpeg可执行文件",
            "",
            "可执行文件 (*.exe);;所有文件 (*.*)"
        )
        if path:
            self.ffmpeg_path_edit.setText(path)
    
    def load_settings(self):
        """加载设置"""
        self.ffmpeg_path_edit.setText(self.config_manager.get("ffmpeg_path", ""))
        video_codec = self.config_manager.get("video_codec", "libx264")
        self.video_codec_combo.setCurrentText(video_codec)
        # 触发编码器改变事件以更新预设选项
        self.on_codec_changed(video_codec)
        self.video_preset_combo.setCurrentText(self.config_manager.get("video_preset", "medium"))
        self.video_crf_spin.setValue(int(self.config_manager.get("video_crf", "23")))
        self.video_bit_depth_combo.setCurrentText(self.config_manager.get("video_bit_depth", "8"))
        self.video_resolution_edit.setText(self.config_manager.get("video_resolution", ""))
        self.audio_codec_combo.setCurrentText(self.config_manager.get("audio_codec", "copy"))
        self.audio_bitrate_edit.setText(self.config_manager.get("audio_bitrate", ""))
        self.subtitle_combo.setCurrentText(self.config_manager.get("subtitle_mode", "copy"))
        self.use_custom_check.setChecked(self.config_manager.get("use_custom_command", False))
        self.custom_command_edit.setPlainText(self.config_manager.get("custom_command_template", ""))
        self.custom_args_edit.setText(self.config_manager.get("custom_args", ""))
    
    def save_settings(self):
        """保存设置"""
        # 验证FFmpeg路径（如果指定了）
        ffmpeg_path = self.ffmpeg_path_edit.text().strip()
        if ffmpeg_path:
            import os
            if not os.path.exists(ffmpeg_path):
                QMessageBox.warning(self, "警告", "指定的FFmpeg路径不存在，将尝试使用系统PATH中的FFmpeg")
        
        # 保存配置
        self.config_manager.update({
            "ffmpeg_path": ffmpeg_path,
            "video_codec": self.video_codec_combo.currentText(),
            "video_preset": self.video_preset_combo.currentText(),
            "video_crf": str(self.video_crf_spin.value()),
            "video_bit_depth": self.video_bit_depth_combo.currentText(),
            "video_resolution": self.video_resolution_edit.text().strip(),
            "audio_codec": self.audio_codec_combo.currentText(),
            "audio_bitrate": self.audio_bitrate_edit.text().strip(),
            "subtitle_mode": self.subtitle_combo.currentText(),
            "use_custom_command": self.use_custom_check.isChecked(),
            "custom_command_template": self.custom_command_edit.toPlainText().strip(),
            "custom_args": self.custom_args_edit.text().strip()
        })
        
        if self.config_manager.save_config():
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "保存设置失败")

