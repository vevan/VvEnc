"""
FFmpeg处理器 - 封装FFmpeg调用和进度解析
"""
import subprocess
import re
import os
import shutil
import sys
from typing import Optional, Callable, Tuple
from pathlib import Path

# Windows上隐藏控制台窗口的标志
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


class FFmpegHandler:
    """FFmpeg处理器"""
    
    def __init__(self, ffmpeg_path: str = ""):
        """
        初始化FFmpeg处理器
        
        Args:
            ffmpeg_path: FFmpeg可执行文件路径，空字符串表示使用系统PATH
        """
        self.ffmpeg_path = self._find_ffmpeg(ffmpeg_path)
        if not self.ffmpeg_path:
            raise FileNotFoundError("未找到FFmpeg，请确保已安装或在设置中指定路径")
    
    def _find_ffmpeg(self, custom_path: str = "") -> Optional[str]:
        """查找FFmpeg可执行文件"""
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        # 检查系统PATH
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg
        
        # Windows常见路径
        if os.name == 'nt':
            common_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def get_video_info(self, video_path: str) -> dict:
        """获取视频信息（简化版，用于获取时长）"""
        if not self.ffmpeg_path:
            return {}
        
        try:
            # 使用ffprobe获取视频信息
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if not os.path.exists(ffprobe_path):
                ffprobe_path = shutil.which("ffprobe")
            
            if not ffprobe_path:
                return {}
            
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration,r_frame_rate,codec_name",
                "-show_entries", "format=duration",
                "-of", "json",
                video_path
            ]
            
            # Windows上隐藏控制台窗口
            run_kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
            if sys.platform == 'win32':
                run_kwargs['creationflags'] = CREATE_NO_WINDOW
            result = subprocess.run(cmd, **run_kwargs)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception as e:
            print(f"获取视频信息失败: {e}")
        
        return {}
    
    def get_detailed_video_info(self, video_path: str) -> dict:
        """获取详细的视频信息"""
        if not self.ffmpeg_path:
            return {}
        
        try:
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if not os.path.exists(ffprobe_path):
                ffprobe_path = shutil.which("ffprobe")
            
            if not ffprobe_path:
                return {}
            
            # 获取视频和音频流信息，以及格式信息
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "stream=width,height,codec_name,codec_type,bit_rate,r_frame_rate,duration",
                "-show_entries", "format=duration,size,bit_rate",
                "-of", "json",
                video_path
            ]
            
            run_kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
            if sys.platform == 'win32':
                run_kwargs['creationflags'] = CREATE_NO_WINDOW
            result = subprocess.run(cmd, **run_kwargs)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                info = {
                    'file_path': video_path,
                    'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
                }
                
                # 解析流信息
                if 'streams' in data:
                    video_stream = None
                    audio_stream = None
                    
                    for stream in data['streams']:
                        if stream.get('codec_type') == 'video' and not video_stream:
                            video_stream = stream
                        elif stream.get('codec_type') == 'audio' and not audio_stream:
                            audio_stream = stream
                    
                    # 视频信息
                    if video_stream:
                        info['width'] = int(video_stream.get('width', 0))
                        info['height'] = int(video_stream.get('height', 0))
                        info['video_codec'] = video_stream.get('codec_name', 'unknown')
                        info['video_bitrate'] = int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else 0
                        
                        # 帧率
                        r_frame_rate = video_stream.get('r_frame_rate', '0/1')
                        if '/' in r_frame_rate:
                            num, den = map(int, r_frame_rate.split('/'))
                            info['fps'] = num / den if den > 0 else 0
                        else:
                            info['fps'] = float(r_frame_rate) if r_frame_rate else 0
                        
                        # 视频时长
                        info['video_duration'] = float(video_stream.get('duration', 0)) if video_stream.get('duration') else 0
                    
                    # 音频信息
                    if audio_stream:
                        info['audio_codec'] = audio_stream.get('codec_name', 'unknown')
                        info['audio_bitrate'] = int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else 0
                        info['audio_duration'] = float(audio_stream.get('duration', 0)) if audio_stream.get('duration') else 0
                
                # 格式信息
                if 'format' in data:
                    format_info = data['format']
                    info['format_duration'] = float(format_info.get('duration', 0)) if format_info.get('duration') else 0
                    info['format_bitrate'] = int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else 0
                    info['format_size'] = int(format_info.get('size', 0)) if format_info.get('size') else 0
                
                # 计算每帧每10000像素点所用的bit数
                if 'width' in info and 'height' in info and 'fps' in info and 'format_bitrate' in info:
                    width = info['width']
                    height = info['height']
                    fps = info['fps']
                    bitrate = info['format_bitrate']  # 总码率（bps）
                    
                    if width > 0 and height > 0 and fps > 0:
                        pixels = width * height
                        bits_per_frame = bitrate / fps if fps > 0 else 0
                        bits_per_10000_pixels = (bits_per_frame / pixels * 10000) if pixels > 0 else 0
                        info['bits_per_10000_pixels'] = bits_per_10000_pixels
                
                return info
        except Exception as e:
            print(f"获取详细视频信息失败: {e}")
        
        return {}
    
    def get_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        info = self.get_video_info(video_path)
        try:
            if "format" in info and "duration" in info["format"]:
                return float(info["format"]["duration"])
            if "streams" in info and len(info["streams"]) > 0:
                if "duration" in info["streams"][0]:
                    return float(info["streams"][0]["duration"])
        except:
            pass
        return 0.0
    
    def build_command(
        self,
        input_path: str,
        output_path: str,
        video_codec: str = "libx264",
        video_preset: str = "medium",
        video_crf: str = "23",
        video_resolution: str = "",
        video_bit_depth: str = "8",
        audio_codec: str = "copy",
        audio_bitrate: str = "",
        subtitle_mode: str = "copy",
        custom_args: str = "",
        use_custom: bool = False,
        custom_template: str = ""
    ) -> list:
        """构建FFmpeg命令"""
        if use_custom and custom_template:
            # 使用自定义命令模板
            cmd_str = custom_template.replace("{input}", input_path).replace("{output}", output_path)
            # 简单的命令解析（不支持复杂引号处理）
            return cmd_str.split()
        
        cmd = [self.ffmpeg_path, "-i", input_path, "-y"]  # -y表示覆盖输出文件
        
        # 视频编码参数
        if video_codec:
            cmd.extend(["-c:v", video_codec])
            if video_codec != "copy":
                # NVenc编码器使用不同的参数
                if video_codec in ["av1_nvenc", "h264_nvenc", "hevc_nvenc"]:
                    if video_preset:
                        cmd.extend(["-preset", video_preset])
                    # NVenc使用-cq参数而不是-crf
                    if video_crf:
                        cmd.extend(["-cq", str(video_crf)])
                    # NVenc通常使用VBR模式
                    cmd.extend(["-rc", "vbr"])
                else:
                    # 软件编码器使用标准参数
                    if video_preset:
                        cmd.extend(["-preset", video_preset])
                    if video_crf:
                        cmd.extend(["-crf", str(video_crf)])
                
                # 10bit编码处理
                pix_fmt_value = None
                if video_bit_depth == "10":
                    if video_codec == "av1_nvenc":
                        # AV1 NVenc 10bit使用p010le像素格式
                        pix_fmt_value = "p010le"
                    elif video_codec == "libsvtav1":
                        # SVT-AV1 10bit使用yuv420p10le
                        pix_fmt_value = "yuv420p10le"
                    elif video_codec == "libx265":
                        # x265 10bit使用yuv420p10le
                        pix_fmt_value = "yuv420p10le"
                    elif video_codec in ["h264_nvenc", "hevc_nvenc"]:
                        # NVenc H.264/HEVC 10bit使用p010le
                        pix_fmt_value = "p010le"
                
                # 处理分辨率和像素格式
                if video_resolution or pix_fmt_value:
                    vf_filters = []
                    if video_resolution:
                        vf_filters.append(f"scale={video_resolution}")
                    if pix_fmt_value:
                        vf_filters.append(f"format={pix_fmt_value}")
                    if vf_filters:
                        cmd.extend(["-vf", ",".join(vf_filters)])
                elif pix_fmt_value:
                    # 只有像素格式，没有分辨率
                    cmd.extend(["-pix_fmt", pix_fmt_value])
        
        # 音频编码参数
        if audio_codec:
            cmd.extend(["-c:a", audio_codec])
            if audio_codec != "copy" and audio_bitrate:
                cmd.extend(["-b:a", audio_bitrate])
        
        # 字幕处理
        if subtitle_mode == "copy":
            cmd.extend(["-c:s", "copy"])
        elif subtitle_mode == "embed":
            # 嵌入字幕需要更复杂的处理，这里简化处理
            pass
        
        # 自定义参数
        if custom_args:
            cmd.extend(custom_args.split())
        
        cmd.append(output_path)
        return cmd
    
    def encode(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        cancel_flag: Optional[Callable[[], bool]] = None,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        执行编码
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            progress_callback: 进度回调函数 (progress: float, message: str) -> None
            cancel_flag: 取消标志函数 () -> bool
            **kwargs: 编码参数
        
        Returns:
            (success: bool, message: str)
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        cmd = self.build_command(input_path, output_path, **kwargs)
        
        process = None
        try:
            # 获取视频时长用于计算进度
            duration = self.get_duration(input_path)
            
            # Windows上隐藏控制台窗口
            popen_kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'universal_newlines': True,
                'bufsize': 1
            }
            if sys.platform == 'win32':
                popen_kwargs['creationflags'] = CREATE_NO_WINDOW
            process = subprocess.Popen(cmd, **popen_kwargs)
            
            # 解析进度
            time_pattern = re.compile(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})')
            last_progress = 0.0
            
            while True:
                # 检查取消标志
                if cancel_flag and cancel_flag():
                    if process:
                        try:
                            process.terminate()  # 先尝试优雅终止
                            import time
                            time.sleep(1)  # 等待1秒
                            if process.poll() is None:  # 如果还在运行
                                process.kill()  # 强制终止
                            # 等待进程结束（最多2秒）
                            try:
                                process.wait(timeout=2)
                            except:
                                pass
                        except Exception:
                            try:
                                if process.poll() is None:
                                    process.kill()
                            except:
                                pass
                    return False, "Cancelled"
                
                line = process.stderr.readline()
                if not line:
                    # 检查进程是否已结束
                    if process.poll() is not None:
                        break
                    # 短暂等待避免CPU占用过高
                    import time
                    time.sleep(0.05)
                    continue
                
                # 解析时间戳
                match = time_pattern.search(line)
                if match:
                    hours, minutes, seconds, centiseconds = map(int, match.groups())
                    current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
                    
                    if duration > 0:
                        progress = min(current_time / duration * 100, 99.0)  # 最多99%，最后完成时设为100%
                        if progress > last_progress:
                            last_progress = progress
                            if progress_callback:
                                progress_callback(progress, f"Encoding: {progress:.1f}%")
            
            process.wait()
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(100.0, "Encoding finished")
                return True, "Success"
            elif process.returncode == -15 or process.returncode == -9:  # SIGTERM 或 SIGKILL
                return False, "Cancelled"
            else:
                error_msg = process.stderr.read() if process.stderr else "Unknown error"
                return False, f"Failed: {error_msg}"
        
        except KeyboardInterrupt:
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    if process.poll() is None:
                        process.kill()
            return False, "Interrupted"
        except Exception as e:
            if process:
                try:
                    process.terminate()
                except:
                    pass
            return False, f"Error: {str(e)}"

