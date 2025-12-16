"""
配置管理器 - 使用JSON格式存储设置
"""
import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "ffmpeg_path": "",  # 空字符串表示使用系统PATH中的ffmpeg
            "output_dir": "",
            "video_codec": "libx264",
            "video_preset": "medium",
            "video_crf": "23",
            "video_resolution": "",  # 空字符串表示保持原分辨率
            "video_bit_depth": "8",  # "8", "10" 位深度
            "audio_codec": "copy",  # "copy"表示直接复制音频流
            "audio_bitrate": "",
            # 备用音频编码参数：当主音频编码为 copy 且与 MP4 容器不兼容时使用
            "fallback_audio_codec": "aac",   # 可选: aac / opus / mp3
            "fallback_audio_bitrate": "192k",
            # 窗口尺寸
            "window_width": 1024,
            "window_height": 720,
            # 编码完成提示音
            "notification_sound_enabled": False,
            "notification_sound_file": "",
            "subtitle_mode": "copy",  # "copy", "embed", "none"
            "custom_args": "",  # 自定义FFmpeg参数
            "use_custom_command": False,  # 是否使用自定义命令行
            "custom_command_template": "",
            "language": "zh_CN"  # 语言设置
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有键都存在
                    merged = self.default_config.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """批量更新配置"""
        self.config.update(updates)

