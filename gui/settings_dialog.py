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
from translations import LanguageManager


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager: ConfigManager, i18n_manager: LanguageManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.i18n_manager = i18n_manager or LanguageManager()
        self.setWindowTitle(self.tr('SETTINGS_TITLE'))
        self.setMinimumWidth(600)
        self.init_ui()
        self.load_settings()
    
    def tr(self, key: str, default: str = None) -> str:
        """翻译函数"""
        return self.i18n_manager.tr(key, default)
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # FFmpeg路径设置
        ffmpeg_group = QGroupBox(self.tr('FFMPEG_SETTINGS'))
        ffmpeg_layout = QFormLayout()
        
        self.ffmpeg_path_edit = QLineEdit()
        self.ffmpeg_path_edit.setToolTip(self.tr('FFMPEG_PATH_TOOLTIP'))
        self.ffmpeg_browse_btn = QPushButton(self.tr('BROWSE'))
        self.ffmpeg_browse_btn.clicked.connect(self.browse_ffmpeg)
        ffmpeg_path_layout = QHBoxLayout()
        ffmpeg_path_layout.addWidget(self.ffmpeg_path_edit)
        ffmpeg_path_layout.addWidget(self.ffmpeg_browse_btn)
        ffmpeg_layout.addRow(self.tr('FFMPEG_PATH') + ":", ffmpeg_path_layout)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        # 视频编码参数
        video_group = QGroupBox(self.tr('VIDEO_ENCODING_PARAMS'))
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
        self.video_codec_combo.setToolTip(self.tr('VIDEO_CODEC_TOOLTIP'))
        self.video_codec_combo.currentTextChanged.connect(self.on_codec_changed)
        video_layout.addRow(self.tr('VIDEO_CODEC') + ":", self.video_codec_combo)
        
        self.video_preset_combo = QComboBox()
        self.video_preset_combo.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
        self.video_preset_combo.setToolTip(self.tr('ENCODING_PRESET_TOOLTIP'))
        video_layout.addRow(self.tr('ENCODING_PRESET') + ":", self.video_preset_combo)
        
        self.video_crf_spin = QSpinBox()
        self.video_crf_spin.setRange(0, 51)
        self.video_crf_spin.setValue(23)
        self.video_crf_spin.setToolTip(self.tr('CRF_QUALITY_TOOLTIP'))
        video_layout.addRow(self.tr('CRF_QUALITY') + ":", self.video_crf_spin)
        
        self.video_bit_depth_combo = QComboBox()
        self.video_bit_depth_combo.addItems(["8", "10"])
        self.video_bit_depth_combo.setCurrentText("8")
        self.video_bit_depth_combo.setToolTip(self.tr('BIT_DEPTH_TOOLTIP'))
        video_layout.addRow(self.tr('BIT_DEPTH') + ":", self.video_bit_depth_combo)
        
        self.video_resolution_edit = QLineEdit()
        self.video_resolution_edit.setPlaceholderText(self.tr('RESOLUTION_PLACEHOLDER'))
        self.video_resolution_edit.setToolTip(self.tr('RESOLUTION_TOOLTIP'))
        video_layout.addRow(self.tr('RESOLUTION') + ":", self.video_resolution_edit)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # 音频编码参数
        audio_group = QGroupBox(self.tr('AUDIO_ENCODING_PARAMS'))
        audio_layout = QFormLayout()
        
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["copy", "aac", "mp3", "opus"])
        self.audio_codec_combo.setToolTip(self.tr('AUDIO_CODEC_TOOLTIP'))
        self.audio_codec_combo.currentTextChanged.connect(self.on_audio_codec_changed)
        audio_layout.addRow(self.tr('AUDIO_CODEC') + ":", self.audio_codec_combo)
        
        self.audio_bitrate_edit = QLineEdit()
        self.audio_bitrate_edit.setPlaceholderText(self.tr('AUDIO_BITRATE_PLACEHOLDER'))
        self.audio_bitrate_edit.setToolTip(self.tr('AUDIO_BITRATE_TOOLTIP'))
        audio_layout.addRow(self.tr('AUDIO_BITRATE') + ":", self.audio_bitrate_edit)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # 备用音频编码参数
        self.fallback_audio_group = QGroupBox(self.tr('FALLBACK_AUDIO_SETTINGS'))
        fallback_layout = QFormLayout()

        self.fallback_audio_codec_combo = QComboBox()
        self.fallback_audio_codec_combo.addItems(["aac", "opus", "mp3"])
        self.fallback_audio_codec_combo.setToolTip(self.tr('FALLBACK_AUDIO_CODEC_TOOLTIP'))
        fallback_layout.addRow(self.tr('FALLBACK_AUDIO_CODEC') + ":", self.fallback_audio_codec_combo)

        self.fallback_audio_bitrate_edit = QLineEdit()
        self.fallback_audio_bitrate_edit.setPlaceholderText(self.tr('FALLBACK_AUDIO_BITRATE_PLACEHOLDER'))
        self.fallback_audio_bitrate_edit.setToolTip(self.tr('FALLBACK_AUDIO_BITRATE_TOOLTIP'))
        fallback_layout.addRow(self.tr('FALLBACK_AUDIO_BITRATE') + ":", self.fallback_audio_bitrate_edit)

        self.fallback_audio_group.setLayout(fallback_layout)
        layout.addWidget(self.fallback_audio_group)

        # 编码完成提示音
        notify_group = QGroupBox(self.tr('NOTIFICATION_SETTINGS'))
        notify_layout = QFormLayout()

        self.notify_sound_check = QCheckBox(self.tr('ENABLE_NOTIFICATION_SOUND'))
        notify_layout.addRow(self.notify_sound_check)

        self.notify_sound_edit = QLineEdit()
        self.notify_sound_edit.setPlaceholderText(self.tr('NOTIFICATION_SOUND_FILE_PLACEHOLDER'))
        self.notify_sound_browse = QPushButton(self.tr('BROWSE'))
        self.notify_sound_browse.clicked.connect(self.browse_notify_sound)
        sound_path_layout = QHBoxLayout()
        sound_path_layout.addWidget(self.notify_sound_edit)
        sound_path_layout.addWidget(self.notify_sound_browse)
        notify_layout.addRow(self.tr('NOTIFICATION_SOUND_FILE') + ":", sound_path_layout)

        notify_group.setLayout(notify_layout)
        layout.addWidget(notify_group)
        
        # 字幕设置
        subtitle_group = QGroupBox(self.tr('SUBTITLE_SETTINGS'))
        subtitle_layout = QFormLayout()
        
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.addItems(["copy", "embed", "none"])
        self.subtitle_combo.setToolTip(self.tr('SUBTITLE_MODE_TOOLTIP'))
        subtitle_layout.addRow(self.tr('SUBTITLE_MODE') + ":", self.subtitle_combo)
        
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        # 自定义参数
        custom_group = QGroupBox(self.tr('CUSTOM_PARAMS'))
        custom_layout = QVBoxLayout()
        
        self.use_custom_check = QCheckBox(self.tr('USE_CUSTOM_COMMAND'))
        self.use_custom_check.setToolTip(self.tr('USE_CUSTOM_COMMAND_TOOLTIP'))
        custom_layout.addWidget(self.use_custom_check)
        
        self.custom_command_edit = QTextEdit()
        self.custom_command_edit.setPlaceholderText(self.tr('CUSTOM_COMMAND_PLACEHOLDER'))
        self.custom_command_edit.setMaximumHeight(100)
        self.custom_command_edit.setToolTip(self.tr('CUSTOM_COMMAND_TOOLTIP'))
        custom_layout.addWidget(self.custom_command_edit)
        
        self.custom_args_edit = QLineEdit()
        self.custom_args_edit.setPlaceholderText(self.tr('CUSTOM_ARGS_PLACEHOLDER'))
        self.custom_args_edit.setToolTip(self.tr('CUSTOM_ARGS_TOOLTIP'))
        custom_layout.addWidget(self.custom_args_edit)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_btn = QPushButton(self.tr('SAVE'))
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton(self.tr('CANCEL'))
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

    def on_audio_codec_changed(self, codec: str):
        """音频编码器改变时，控制备用音频编码参数的可见性/可用性"""
        # 只有当主音频编码选择为 copy 时，备用音频编码参数才有意义
        enabled = (codec == "copy")
        self.fallback_audio_group.setEnabled(enabled)
        self.fallback_audio_group.setVisible(enabled)
    
    def browse_ffmpeg(self):
        """浏览FFmpeg路径"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('MSG_SELECT_FFMPEG'),
            "",
            self.tr('MSG_EXECUTABLE_FILES')
        )
        if path:
            self.ffmpeg_path_edit.setText(path)

    def browse_notify_sound(self):
        """选择提示音文件"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('MSG_SELECT_SOUND_FILE'),
            "",
            self.tr('SOUND_FILES_FILTER')
        )
        if path:
            self.notify_sound_edit.setText(path)
    
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
        self.fallback_audio_codec_combo.setCurrentText(self.config_manager.get("fallback_audio_codec", "aac"))
        self.fallback_audio_bitrate_edit.setText(self.config_manager.get("fallback_audio_bitrate", "192k"))
        # 根据当前音频编码设置更新备用参数区域状态
        self.on_audio_codec_changed(self.audio_codec_combo.currentText())
        self.notify_sound_check.setChecked(self.config_manager.get("notification_sound_enabled", False))
        self.notify_sound_edit.setText(self.config_manager.get("notification_sound_file", ""))
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
                QMessageBox.warning(self, self.tr('MSG_WARNING'), self.tr('MSG_FFMPEG_PATH_NOT_EXISTS'))
        
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
            "fallback_audio_codec": self.fallback_audio_codec_combo.currentText(),
            "fallback_audio_bitrate": self.fallback_audio_bitrate_edit.text().strip(),
            "notification_sound_enabled": self.notify_sound_check.isChecked(),
            "notification_sound_file": self.notify_sound_edit.text().strip(),
            "subtitle_mode": self.subtitle_combo.currentText(),
            "use_custom_command": self.use_custom_check.isChecked(),
            "custom_command_template": self.custom_command_edit.toPlainText().strip(),
            "custom_args": self.custom_args_edit.text().strip()
        })
        
        if self.config_manager.save_config():
            QMessageBox.information(self, self.tr('MSG_SUCCESS'), self.tr('MSG_SETTINGS_SAVED'))
            self.accept()
        else:
            QMessageBox.warning(self, self.tr('MSG_ERROR'), self.tr('MSG_SETTINGS_SAVE_FAILED'))

