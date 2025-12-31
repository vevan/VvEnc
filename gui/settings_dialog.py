"""
设置对话框 - 编码参数配置
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QComboBox, QSpinBox,
    QCheckBox, QTextEdit, QFileDialog, QGroupBox,
    QLabel, QMessageBox, QFrame, QApplication
)
from PyQt5.QtCore import Qt
import os
import subprocess
import re
from typing import Optional
from core.config_manager import ConfigManager
from core.ffmpeg_handler import FFmpegHandler
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
    
    def _get_version(self) -> str:
        """获取版本号（从 version 文件读取，格式统一为 v0.x.x）"""
        # 从 version 文件读取版本号（版本文件格式统一为带 v 前缀，如 v0.8.6）
        try:
            version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                    # 版本文件统一格式为带 'v' 前缀，显示时移除 'v' 前缀
                    if version.startswith('v'):
                        version = version[1:]
                    if version:
                        return version
        except Exception:
            pass
        
        # 如果无法读取版本文件，返回默认版本（不带 v 前缀，用于显示）
        return "0.8.6"
    
    def _check_ffmpeg_in_path(self) -> tuple[bool, str]:
        """
        检查 FFmpeg 是否在系统 PATH 中
        
        Returns:
            (是否在PATH中, FFmpeg路径或None)
        """
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return True, ffmpeg_path
        return False, None
    
    def _update_ffmpeg_path_status(self):
        """更新 FFmpeg 路径状态提示"""
        # 如果用户手动指定了路径，检查该路径是否存在
        manual_path = self.ffmpeg_path_edit.text().strip()
        if manual_path and os.path.exists(manual_path):
            # 用户已手动指定路径，显示绿色提示
            self.ffmpeg_path_status_label.setText(
                self.tr('FFMPEG_MANUAL_PATH_MSG', '已手动指定 FFmpeg 路径。')
            )
            self.ffmpeg_path_status_label.setStyleSheet("color: #008000; padding: 5px;")
        else:
            # 检查系统 PATH
            in_path, path = self._check_ffmpeg_in_path()
            if in_path:
                # 绿色提示：FFmpeg 已在系统路径中
                self.ffmpeg_path_status_label.setText(
                    self.tr('FFMPEG_IN_PATH_MSG', 'FFmpeg 已添加到系统路径，无需设置。如有需要可指定其它版本。')
                )
                self.ffmpeg_path_status_label.setStyleSheet("color: #008000; padding: 5px;")
            else:
                # 红色提示：FFmpeg 未在系统路径中
                self.ffmpeg_path_status_label.setText(
                    self.tr('FFMPEG_NOT_IN_PATH_MSG', 'FFmpeg 未添加到系统路径，请添加系统路径或手动指定路径。')
                )
                self.ffmpeg_path_status_label.setStyleSheet("color: #DC143C; padding: 5px;")
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # FFmpeg路径设置
        ffmpeg_group = QGroupBox(self.tr('FFMPEG_SETTINGS'))
        ffmpeg_layout = QFormLayout()
        
        self.ffmpeg_path_edit = QLineEdit()
        self.ffmpeg_path_edit.setToolTip(self.tr('FFMPEG_PATH_TOOLTIP'))
        self.ffmpeg_path_edit.textChanged.connect(self._update_ffmpeg_path_status)
        self.ffmpeg_browse_btn = QPushButton(self.tr('BROWSE'))
        self.ffmpeg_browse_btn.clicked.connect(self.browse_ffmpeg)
        ffmpeg_path_layout = QHBoxLayout()
        ffmpeg_path_layout.addWidget(self.ffmpeg_path_edit)
        ffmpeg_path_layout.addWidget(self.ffmpeg_browse_btn)
        ffmpeg_layout.addRow(self.tr('FFMPEG_PATH') + ":", ffmpeg_path_layout)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        # FFmpeg 路径状态提示
        self.ffmpeg_path_status_label = QLabel()
        self.ffmpeg_path_status_label.setWordWrap(True)
        self._update_ffmpeg_path_status()
        layout.addWidget(self.ffmpeg_path_status_label)
        
        # FFmpeg 下载链接
        ffmpeg_download_label = QLabel()
        ffmpeg_download_label.setOpenExternalLinks(True)
        ffmpeg_download_label.setText(
            '<a href="https://ffmpeg.org/download.html" style="color: #0066cc;">'
            + self.tr('FFMPEG_DOWNLOAD_LINK', '下载 FFmpeg') + '</a>'
        )
        ffmpeg_download_label.setAlignment(Qt.AlignRight)
        layout.addWidget(ffmpeg_download_label)
        
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
        
        self.video_framerate_edit = QLineEdit()
        self.video_framerate_edit.setPlaceholderText(self.tr('FRAMERATE_PLACEHOLDER', '例如: 30 或 29.97，留空保持原始帧率'))
        self.video_framerate_edit.setToolTip(self.tr('FRAMERATE_TOOLTIP', '视频帧率（fps）。留空则保持原始帧率。例如: 30, 29.97, 24'))
        video_layout.addRow(self.tr('FRAMERATE', '帧率') + ":", self.video_framerate_edit)
        
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
        
        # 复制命令按钮
        copy_command_btn = QPushButton(self.tr('COPY_COMMAND', '复制 FFmpeg 命令'))
        copy_command_btn.setToolTip(self.tr('COPY_COMMAND_TOOLTIP', '复制当前设置的 FFmpeg 命令到剪贴板'))
        copy_command_btn.clicked.connect(self.copy_ffmpeg_command)
        custom_layout.addWidget(copy_command_btn)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # 添加分隔线
        layout.addSpacing(10)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 版本信息和链接区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # 版本信息
        version = self._get_version()
        version_label = QLabel(f"VvEnc {version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666666; font-size: 10pt;")
        info_layout.addWidget(version_label)
        
        # 链接区域
        links_layout = QHBoxLayout()
        links_layout.addStretch()
        
        # FFmpeg 官网链接
        ffmpeg_website_label = QLabel()
        ffmpeg_website_label.setOpenExternalLinks(True)
        ffmpeg_website_label.setText(
            '<a href="https://ffmpeg.org/" style="color: #0066cc;">FFmpeg</a>'
        )
        links_layout.addWidget(ffmpeg_website_label)
        
        # 分隔符
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #999999;")
        links_layout.addWidget(separator)
        
        # GPL 协议链接
        gpl_label = QLabel()
        gpl_label.setOpenExternalLinks(True)
        gpl_label.setText(
            '<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: #0066cc;">GPL-3.0</a>'
        )
        links_layout.addWidget(gpl_label)
        
        links_layout.addStretch()
        info_layout.addLayout(links_layout)
        
        layout.addLayout(info_layout)
        layout.addSpacing(5)
        
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
            # 路径改变时会自动触发 _update_ffmpeg_path_status

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
        self.video_framerate_edit.setText(self.config_manager.get("video_framerate", ""))
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
            "video_framerate": self.video_framerate_edit.text().strip(),
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
    
    def copy_ffmpeg_command(self):
        """复制当前设置的 FFmpeg 命令到剪贴板"""
        try:
            # 获取当前设置
            ffmpeg_path = self.ffmpeg_path_edit.text().strip()
            if not ffmpeg_path:
                # 尝试从系统 PATH 查找
                import shutil
                ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
            
            # 创建临时 FFmpegHandler 实例
            # 如果找不到 FFmpeg，仍然可以生成命令（使用默认路径）
            try:
                handler = FFmpegHandler(ffmpeg_path if ffmpeg_path else "")
            except FileNotFoundError:
                # 如果找不到 FFmpeg，创建一个临时对象来生成命令
                # 这种情况下，我们仍然可以生成命令字符串
                import shutil
                # 尝试查找 FFmpeg，如果找不到就使用默认名称
                found_ffmpeg = shutil.which("ffmpeg")
                if found_ffmpeg:
                    handler = FFmpegHandler(found_ffmpeg)
                else:
                    # 创建一个最小化的处理器，只用于生成命令
                    handler = FFmpegHandler.__new__(FFmpegHandler)
                    handler.ffmpeg_path = ffmpeg_path or "ffmpeg"
            
            # 获取当前设置值
            video_codec = self.video_codec_combo.currentText()
            video_preset = self.video_preset_combo.currentText()
            video_crf = str(self.video_crf_spin.value())
            video_bit_depth = self.video_bit_depth_combo.currentText()
            video_resolution = self.video_resolution_edit.text().strip()
            video_framerate = self.video_framerate_edit.text().strip()
            audio_codec = self.audio_codec_combo.currentText()
            audio_bitrate = self.audio_bitrate_edit.text().strip()
            subtitle_mode = self.subtitle_combo.currentText()
            custom_args = self.custom_args_edit.text().strip()
            use_custom = self.use_custom_check.isChecked()
            custom_template = self.custom_command_edit.toPlainText().strip()
            
            # 使用示例路径
            example_input = "input.mp4"
            example_output = "output.mp4"
            
            # 构建命令
            cmd = handler.build_command(
                input_path=example_input,
                output_path=example_output,
                video_codec=video_codec,
                video_preset=video_preset,
                video_crf=video_crf,
                video_resolution=video_resolution,
                video_bit_depth=video_bit_depth,
                video_framerate=video_framerate,
                audio_codec=audio_codec,
                audio_bitrate=audio_bitrate,
                subtitle_mode=subtitle_mode,
                custom_args=custom_args,
                use_custom=use_custom,
                custom_template=custom_template
            )
            
            # 将 FFmpeg 路径替换为 ffmpeg.exe（Windows）或 ffmpeg（其他系统）
            # build_command 返回的第一个元素是 FFmpeg 路径
            if cmd and len(cmd) > 0:
                import sys
                # 根据操作系统选择命令名称
                if sys.platform == 'win32':
                    cmd[0] = 'ffmpeg.exe'
                else:
                    cmd[0] = 'ffmpeg'
            
            # 将命令列表转换为字符串
            # 对于包含空格的参数，需要加引号
            cmd_str_parts = []
            for arg in cmd:
                if ' ' in arg or '\t' in arg:
                    # 如果参数包含空格，用引号包裹
                    cmd_str_parts.append(f'"{arg}"')
                else:
                    cmd_str_parts.append(arg)
            
            cmd_str = ' '.join(cmd_str_parts)
            
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(cmd_str)
            
            # 显示成功消息
            QMessageBox.information(
                self,
                self.tr('MSG_SUCCESS', '成功'),
                self.tr('MSG_COMMAND_COPIED', 'FFmpeg 命令已复制到剪贴板')
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.tr('MSG_ERROR', '错误'),
                self.tr('MSG_COMMAND_COPY_FAILED', '复制命令失败') + f": {str(e)}"
            )

