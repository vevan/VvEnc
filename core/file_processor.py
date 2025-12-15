"""
文件处理器 - 处理文件扫描、目录结构保留等
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from core.ffmpeg_handler import FFmpegHandler


class FileProcessor:
    """文件处理器"""
    
    # 支持的视频格式
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ts', '.mts'}
    
    def __init__(self, ffmpeg_handler: FFmpegHandler):
        self.ffmpeg_handler = ffmpeg_handler
    
    def is_video_file(self, file_path: str) -> bool:
        """判断是否为视频文件"""
        return Path(file_path).suffix.lower() in self.VIDEO_EXTENSIONS
    
    def scan_files(self, path: str) -> List[str]:
        """
        扫描文件（支持单个文件和文件夹）
        
        Args:
            path: 文件或文件夹路径
        
        Returns:
            视频文件路径列表
        """
        files = []
        path_obj = Path(path)
        
        if path_obj.is_file():
            if self.is_video_file(str(path_obj)):
                files.append(str(path_obj))
        elif path_obj.is_dir():
            # 递归扫描文件夹
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if self.is_video_file(file_path):
                        files.append(file_path)
        
        return files
    
    def calculate_output_path(
        self,
        input_path: str,
        input_base: str,
        output_base: str
    ) -> str:
        """
        计算输出路径，保留目录结构
        
        Args:
            input_path: 输入文件完整路径
            input_base: 输入基础路径（拖入的文件夹路径或文件所在目录）
            output_base: 输出基础路径
        
        Returns:
            输出文件完整路径
        """
        input_path_obj = Path(input_path)
        input_base_obj = Path(input_base)
        output_base_obj = Path(output_base)
        
        # 计算相对路径
        try:
            relative_path = input_path_obj.relative_to(input_base_obj)
        except ValueError:
            # 如果不在同一路径下，使用文件名
            relative_path = Path(input_path_obj.name)
        
        # 构建输出路径
        output_path = output_base_obj / relative_path
        
        # 保持文件扩展名（或根据配置修改）
        return str(output_path)
    
    def process_files(
        self,
        input_paths: List[str],
        output_base: str,
        progress_callback: Optional[Callable[[int, int, str, float, str], None]] = None,
        cancel_flag: Optional[Callable[[], bool]] = None,
        **encode_kwargs
    ) -> List[Tuple[str, bool, str]]:
        """
        批量处理文件
        
        Args:
            input_paths: 输入文件路径列表
            output_base: 输出基础目录
            progress_callback: 进度回调 (current: int, total: int, file_path: str, progress: float, message: str) -> None
            **encode_kwargs: 编码参数
        
        Returns:
            [(文件路径, 成功标志, 消息), ...]
        """
        results = []
        total = len(input_paths)
        
        # 确定输入基础路径（用于保留目录结构）
        if len(input_paths) == 1:
            input_base = os.path.dirname(input_paths[0])
        else:
            # 找到所有文件的公共父目录
            common_path = os.path.commonpath(input_paths) if input_paths else ""
            input_base = common_path if common_path else os.path.dirname(input_paths[0])
        
        for idx, input_path in enumerate(input_paths, 1):
            # 检查取消标志
            if cancel_flag and cancel_flag():
                results.append((input_path, False, "已取消"))
                break
            
            # 计算输出路径
            output_path = self.calculate_output_path(input_path, input_base, output_base)
            
            # 文件级进度回调
            def file_progress(progress: float, message: str):
                if progress_callback:
                    progress_callback(idx, total, input_path, progress, message)
            
            # 执行编码
            success, msg = self.ffmpeg_handler.encode(
                input_path,
                output_path,
                progress_callback=file_progress,
                cancel_flag=cancel_flag,
                **encode_kwargs
            )
            
            results.append((input_path, success, msg))
            
            # 如果编码失败或被取消，停止后续处理
            if not success and (cancel_flag and cancel_flag()):
                break
        
        return results

