"""
简体中文翻译
"""
class Translations:
    """简体中文翻译类"""
    
    # ========== 主窗口 ==========
    MAIN_WINDOW_TITLE = "批量视频编码工具"
    
    # 工具栏按钮
    ADD_FILES = "添加文件"
    ADD_FOLDER = "添加文件夹"
    REMOVE_SELECTED = "移除选中"
    CLEAR_LIST = "清空列表"
    SETTINGS = "设置"
    LANGUAGE = "语言"
    
    # 文件列表
    FILE_LIST_TITLE = "待编码文件列表"
    COL_FILENAME = "文件名"
    COL_STATUS = "状态"
    COL_RESOLUTION = "分辨率"
    COL_BITRATE = "码率"
    COL_FRAMERATE = "帧率"
    COL_DURATION = "总时长"
    COL_VIDEO_CODEC = "视频编码"
    COL_FILE_SIZE = "文件大小"
    COL_AUDIO_CODEC = "音频编码"
    COL_AUDIO_BITRATE = "音频码率"
    COL_BITS_PER_PIXEL = "每帧/10000像素bit数"
    COL_PATH = "路径"
    FETCHING_INFO = "获取中..."
    NA = "N/A"
    
    # 输出设置
    OUTPUT_DIR = "输出目录"
    OUTPUT_DIR_NOT_SET = "未设置"
    SELECT_OUTPUT_DIR = "选择输出目录"
    
    # 进度显示
    ENCODING_PROGRESS = "编码进度"
    OVERALL_PROGRESS = "总体进度"
    CURRENT_FILE_PROGRESS = "当前文件进度"
    WAITING = "等待开始..."
    PREPARING = "准备开始..."
    ENCODING_COMPLETE = "编码完成"
    STOPPING = "正在停止编码..."
    LOG_TITLE = "日志"
    
    # 控制按钮
    START_ENCODING = "开始编码"
    STOP = "停止"
    
    # 消息框
    MSG_ERROR = "错误"
    MSG_WARNING = "警告"
    MSG_INFO = "提示"
    MSG_SUCCESS = "成功"
    
    MSG_FFMPEG_NOT_FOUND = "FFmpeg未找到"
    MSG_FFMPEG_NOT_INIT = "FFmpeg未初始化，请检查设置"
    MSG_FFMPEG_INIT_FAILED = "FFmpeg初始化失败"
    MSG_NO_VIDEO_FILES = "未找到视频文件"
    MSG_NO_FILES_ADDED = "请先添加要编码的文件"
    MSG_NO_OUTPUT_DIR = "请先选择输出目录"
    MSG_ENCODING_COMPLETE = "编码完成！"
    MSG_ENCODING_SUCCESS = "成功"
    MSG_ENCODING_FAILED = "失败"
    
    # 文件对话框
    SELECT_VIDEO_FILES = "选择视频文件"
    SELECT_FOLDER = "选择文件夹"
    VIDEO_FILES_FILTER = "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.3gp *.ts *.mts);;所有文件 (*.*)"
    
    # 日志消息
    LOG_FILES_ADDED = "添加了 {count} 个文件"
    LOG_START_ENCODING = "开始编码 {count} 个文件"
    LOG_FFMPEG_UPDATED = "FFmpeg设置已更新"
    LOG_FILE_STARTED = "开始编码 {current}/{total}: {filename}"
    LOG_FILE_FINISHED_SUCCESS = "完成 {current}/{total}: {filename} - {message}"
    LOG_FILE_FINISHED_FAILED = "失败 {current}/{total}: {filename} - {message}"
    LOG_AUDIO_CODEC_AUTO_AAC = "检测到音频编码与 MP4 容器可能不兼容，已自动使用 AAC 编码音频（码率 {bitrate}）"

    # 大小总计
    TOTAL_SIZE = "源文件总大小：{size}"
    TOTAL_SIZE_ENCODED = "源文件总大小：{original}，编码后总大小：{encoded}"

    # 列表状态
    STATUS_WAITING = "等待编码"
    STATUS_ENCODING = "正在编码"
    STATUS_DONE = "编码完成"
    STATUS_FAILED = "编码失败"
    STATUS_PAUSED = "挂起"
    
    # ========== 设置对话框 ==========
    SETTINGS_TITLE = "编码设置"
    
    # FFmpeg设置
    FFMPEG_SETTINGS = "FFmpeg设置"
    FFMPEG_PATH = "FFmpeg路径"
    FFMPEG_PATH_TOOLTIP = (
        "FFmpeg可执行文件的完整路径。\n"
        "如果留空，程序将尝试从系统PATH环境变量中查找FFmpeg。\n"
        "如果系统PATH中没有FFmpeg，请在此处指定完整路径。"
    )
    BROWSE = "浏览..."
    
    # 视频编码参数
    VIDEO_ENCODING_PARAMS = "视频编码参数"
    VIDEO_CODEC = "视频编码器"
    VIDEO_CODEC_TOOLTIP = (
        "选择视频编码器：\n"
        "• libx264: H.264软件编码，兼容性好，速度中等\n"
        "• libx265: HEVC软件编码，压缩率高，速度较慢\n"
        "• libsvtav1: AV1软件编码，最新标准，压缩率最高，速度最慢\n"
        "• av1_nvenc: AV1硬件编码（NVIDIA GPU），需要RTX 40系列或更新\n"
        "• h264_nvenc: H.264硬件编码（NVIDIA GPU），速度快\n"
        "• hevc_nvenc: HEVC硬件编码（NVIDIA GPU），速度快，压缩率高\n"
        "• copy: 直接复制视频流，不进行重新编码"
    )
    ENCODING_PRESET = "编码预设"
    ENCODING_PRESET_TOOLTIP = (
        "编码预设（速度与质量平衡）：\n"
        "• ultrafast ~ faster: 编码速度快，文件较大，质量略低\n"
        "• medium: 平衡选择（推荐）\n"
        "• slow ~ veryslow: 编码速度慢，文件较小，质量更高\n"
        "注意：NVenc编码器使用p1-p7预设（p1最快，p7最慢）"
    )
    CRF_QUALITY = "CRF质量 (0-51)"
    CRF_QUALITY_TOOLTIP = (
        "CRF（恒定速率因子）质量参数：\n"
        "• 0: 最高质量，文件最大（无损）\n"
        "• 18-23: 高质量范围（推荐23）\n"
        "• 28-32: 中等质量，文件较小\n"
        "• 51: 最低质量，文件最小\n"
        "注意：NVenc编码器使用CQ参数（0-51），含义类似"
    )
    BIT_DEPTH = "位深度"
    BIT_DEPTH_TOOLTIP = (
        "视频位深度：\n"
        "• 8bit: 标准位深度，兼容性好，文件较小\n"
        "• 10bit: 高精度，色彩渐变更平滑，暗部细节更好\n"
        "注意：10bit编码需要编码器支持，文件会更大，编码时间更长"
    )
    RESOLUTION = "分辨率 (宽:高)"
    RESOLUTION_PLACEHOLDER = "例如: 1920:1080 或留空保持原分辨率"
    RESOLUTION_TOOLTIP = (
        "输出视频分辨率（宽度:高度）：\n"
        "• 格式：宽度:高度，例如 1920:1080（1080p）\n"
        "• 留空：保持原始分辨率\n"
        "• 常用分辨率：\n"
        "  - 4K: 3840:2160\n"
        "  - 1080p: 1920:1080\n"
        "  - 720p: 1280:720\n"
        "  - 480p: 854:480"
    )
    
    # 音频编码参数
    AUDIO_ENCODING_PARAMS = "音频编码参数"
    AUDIO_CODEC = "音频编码器"
    AUDIO_CODEC_TOOLTIP = (
        "音频编码器：\n"
        "• copy: 直接复制音频流，不重新编码（推荐，速度快）\n"
        "• aac: AAC编码，兼容性好，质量高\n"
        "• mp3: MP3编码，兼容性最好\n"
        "• opus: Opus编码，压缩率高，质量好"
    )
    AUDIO_BITRATE = "音频码率"
    AUDIO_BITRATE_PLACEHOLDER = "例如: 128k"
    AUDIO_BITRATE_TOOLTIP = (
        "音频码率（仅在重新编码时有效）：\n"
        "• 格式：数值+k，例如 128k, 192k, 256k\n"
        "• 推荐值：\n"
        "  - 语音: 64k-96k\n"
        "  - 音乐: 128k-192k\n"
        "  - 高质量: 256k-320k\n"
        "• 选择'copy'时此参数无效"
    )
    # 备用音频编码参数
    FALLBACK_AUDIO_SETTINGS = "备用音频编码参数"
    FALLBACK_AUDIO_CODEC = "备用音频编码器"
    FALLBACK_AUDIO_CODEC_TOOLTIP = (
        "当主音频编码设置为 copy 且与 MP4 容器不兼容时，使用此编码器重新编码音频：\n"
        "• aac: 兼容性好，质量高（推荐）\n"
        "• opus: 压缩率高，适合体积敏感场景\n"
        "• mp3: 兼容性最好"
    )
    FALLBACK_AUDIO_BITRATE = "备用音频码率"
    FALLBACK_AUDIO_BITRATE_PLACEHOLDER = "例如: 192k"
    FALLBACK_AUDIO_BITRATE_TOOLTIP = (
        "备用音频编码时使用的码率：\n"
        "• 当主音频编码为 copy 且源音频不能直接封装到 MP4 时生效\n"
        "• 不填写时默认使用 192k"
    )
    
    # 字幕设置
    SUBTITLE_SETTINGS = "字幕设置"
    SUBTITLE_MODE = "字幕处理"
    SUBTITLE_MODE_TOOLTIP = (
        "字幕处理方式：\n"
        "• copy: 直接复制字幕流（推荐）\n"
        "• embed: 嵌入字幕到视频（需要源文件支持）\n"
        "• none: 不处理字幕，移除字幕流"
    )
    
    # 自定义参数
    CUSTOM_PARAMS = "自定义参数"
    USE_CUSTOM_COMMAND = "使用自定义FFmpeg命令行"
    USE_CUSTOM_COMMAND_TOOLTIP = "启用后，将使用下方自定义命令模板，忽略其他编码参数设置"
    CUSTOM_COMMAND_PLACEHOLDER = (
        "使用 {input} 和 {output} 作为占位符\n"
        "例如: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}"
    )
    CUSTOM_COMMAND_TOOLTIP = (
        "自定义FFmpeg命令模板：\n"
        "• {input}: 输入文件路径（自动替换）\n"
        "• {output}: 输出文件路径（自动替换）\n"
        "• 示例：ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}\n"
        "注意：启用此选项后，其他编码参数将被忽略"
    )
    CUSTOM_ARGS_PLACEHOLDER = "额外的FFmpeg参数（空格分隔）"
    CUSTOM_ARGS_TOOLTIP = (
        "额外的FFmpeg参数（在标准参数之后添加）：\n"
        "• 格式：空格分隔的参数，例如 '-threads 4 -movflags +faststart'\n"
        "• 这些参数会追加到自动生成的FFmpeg命令末尾\n"
        "• 仅在未启用自定义命令时有效"
    )
    
    # 提示音设置
    NOTIFICATION_SETTINGS = "提示音设置"
    ENABLE_NOTIFICATION_SOUND = "队列完成后播放提示音"
    NOTIFICATION_SOUND_FILE = "提示音文件"
    NOTIFICATION_SOUND_FILE_PLACEHOLDER = "选择一个音频文件（例如: wav, mp3）"
    MSG_SELECT_SOUND_FILE = "选择提示音音频文件"
    SOUND_FILES_FILTER = "音频文件 (*.wav *.mp3 *.flac *.ogg *.m4a *.aac);;所有文件 (*.*)"
    
    # 按钮
    SAVE = "保存"
    CANCEL = "取消"
    
    # 设置对话框消息
    MSG_SELECT_FFMPEG = "选择FFmpeg可执行文件"
    MSG_EXECUTABLE_FILES = "可执行文件 (*.exe);;所有文件 (*.*)"
    MSG_FFMPEG_PATH_NOT_EXISTS = "指定的FFmpeg路径不存在，将尝试使用系统PATH中的FFmpeg"
    MSG_SETTINGS_SAVED = "设置已保存"
    MSG_SETTINGS_SAVE_FAILED = "保存设置失败"
    
    # 进度消息格式
    PROGRESS_FORMAT = "总体进度: {current}/{total} 个文件 ({percent}%)"
    ENCODING_COMPLETE_FORMAT = "编码完成: {success}/{total} 成功"
    CURRENT_FILE_FORMAT = "{filename} - {message}"

