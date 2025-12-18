"""
文件处理器 - 处理文件扫描、目录结构保留等
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable, Dict
from core.ffmpeg_handler import FFmpegHandler


class FileProcessor:
    """文件处理器"""
    
    # 支持的视频格式
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm','.m2ts', '.m2v', '.m4v', '.3gp', '.ts', '.mts', '.rm', '.rmvb', '.ts', '.mpg', '.mpeg', '.vob', '.dat'}
    
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
        
        # 无论输入格式如何，统一将输出扩展名设置为 .mp4
        relative_path = relative_path.with_suffix(".mp4")
        
        # 构建输出路径（保留目录结构，但始终使用 .mp4 容器）
        output_path = output_base_obj / relative_path
        
        return str(output_path)
    
    def process_files(
        self,
        input_paths: List[str],
        output_base: str,
        progress_callback: Optional[Callable[[int, int, str, float, str], None]] = None,
        file_started_callback: Optional[Callable[[int, int, str], None]] = None,
        file_finished_callback: Optional[Callable[[int, int, str, bool, str], None]] = None,
        cancel_flag: Optional[Callable[[], bool]] = None,
        per_file_options: Optional[Dict[str, Dict[str, object]]] = None,
        **encode_kwargs
    ) -> List[Tuple[str, str, bool, str]]:
        """
        批量处理文件
        
        Args:
            input_paths: 输入文件路径列表
            output_base: 输出基础目录
            progress_callback: 进度回调 (current: int, total: int, file_path: str, progress: float, message: str) -> None
            file_started_callback: 文件开始回调 (current: int, total: int, file_path: str) -> None
            file_finished_callback: 文件结束回调 (current: int, total: int, file_path: str, success: bool, message: str) -> None
            **encode_kwargs: 编码参数
        
        Returns:
            [(输入文件路径, 输出文件路径, 成功标志, 消息), ...]
        """
        results = []
        total = len(input_paths)
        
        # 确定输入基础路径（用于保留目录结构）
        if len(input_paths) == 1:
            input_base = os.path.dirname(input_paths[0])
            common_path = input_base
        else:
            # 找到所有文件的公共父目录
            common_path = os.path.commonpath(input_paths) if input_paths else ""
            input_base = common_path if common_path else os.path.dirname(input_paths[0])

        # 判断是否需要强制保留拖入的主目录名称：
        # 只要存在直接位于主目录 A 下的文件（relative parts 长度为 1），
        # 就在输出目录 B 中强制创建 A 这一层，无论是否还有子目录。
        preserve_root_dir_for_flat_folder = False
        if common_path and os.path.isdir(common_path):
            try:
                # 检查是否存在相对于 common_path 只有一层路径的文件
                rel_parts_lengths = []
                for p in input_paths:
                    rel = Path(p).relative_to(common_path)
                    rel_parts_lengths.append(len(rel.parts))
                if rel_parts_lengths and any(length == 1 for length in rel_parts_lengths):
                    preserve_root_dir_for_flat_folder = True
            except Exception:
                preserve_root_dir_for_flat_folder = False
        
        for idx, input_path in enumerate(input_paths, 1):
            # 检查取消标志
            if cancel_flag and cancel_flag():
                # 取消时输出路径未知，使用空字符串占位
                results.append((input_path, "", False, "已取消"))
                break
            
            # 计算基础输出路径（已统一为 .mp4 扩展名）
            output_path = Path(self.calculate_output_path(input_path, input_base, output_base))

            # 如果是“扁平目录”场景，强制在输出目录下保留主目录名称
            if preserve_root_dir_for_flat_folder and common_path:
                root_name = os.path.basename(common_path)
                rel = Path(input_path).relative_to(common_path)
                # 保持文件名不变，但统一为 .mp4 扩展名
                rel = rel.with_suffix(".mp4")
                out_rel = Path(root_name) / rel
                output_path = Path(output_base) / out_rel
            
            # 文件开始回调
            if file_started_callback:
                file_started_callback(idx, total, input_path)
            
            # 文件级进度回调
            def file_progress(progress: float, message: str):
                if progress_callback:
                    progress_callback(idx, total, input_path, progress, message)
            
            # 针对当前文件合并通用编码参数与文件级别的重写参数
            current_kwargs = dict(encode_kwargs)
            if per_file_options and input_path in per_file_options:
                current_kwargs.update(per_file_options[input_path])

            # 执行编码
            success, msg = self.ffmpeg_handler.encode(
                input_path,
                str(output_path),
                progress_callback=file_progress,
                cancel_flag=cancel_flag,
                **current_kwargs
            )
            
            results.append((input_path, output_path, success, msg))
            
            # 文件结束回调
            if file_finished_callback:
                file_finished_callback(idx, total, input_path, success, msg)
            
            # 如果编码失败或被取消，停止后续处理
            if not success and (cancel_flag and cancel_flag()):
                break
        
        return results

