"""
繁體中文翻譯
"""
class Translations:
    """繁體中文翻譯類"""
    
    # ========== 主視窗 ==========
    MAIN_WINDOW_TITLE = "批量視頻編碼工具"
    
    # 工具列按鈕
    ADD_FILES = "添加檔案"
    ADD_FOLDER = "添加資料夾"
    REMOVE_SELECTED = "移除選中"
    CLEAR_LIST = "清空列表"
    SETTINGS = "設定"
    LANGUAGE = "語言"
    
    # 檔案列表
    FILE_LIST_TITLE = "待編碼檔案列表"
    COL_FILENAME = "檔案名稱"
    COL_STATUS = "狀態"
    COL_RESOLUTION = "解析度"
    COL_BITRATE = "碼率"
    COL_FRAMERATE = "幀率"
    COL_DURATION = "總時長"
    COL_VIDEO_CODEC = "視頻編碼"
    COL_FILE_SIZE = "檔案大小"
    COL_AUDIO_CODEC = "音頻編碼"
    COL_AUDIO_BITRATE = "音頻碼率"
    COL_BITS_PER_PIXEL = "每幀/10000像素bit數"
    COL_PATH = "路徑"
    FETCHING_INFO = "獲取中..."
    NA = "N/A"
    
    # 輸出設定
    OUTPUT_DIR = "輸出目錄"
    OUTPUT_DIR_NOT_SET = "未設定"
    SELECT_OUTPUT_DIR = "選擇輸出目錄"
    
    # 進度顯示
    ENCODING_PROGRESS = "編碼進度"
    OVERALL_PROGRESS = "總體進度"
    CURRENT_FILE_PROGRESS = "當前檔案進度"
    WAITING = "等待開始..."
    PREPARING = "準備開始..."
    ENCODING_COMPLETE = "編碼完成"
    STOPPING = "正在停止編碼..."
    LOG_TITLE = "日誌"
    
    # 控制按鈕
    START_ENCODING = "開始編碼"
    STOP = "停止"
    
    # 訊息框
    MSG_ERROR = "錯誤"
    MSG_WARNING = "警告"
    MSG_INFO = "提示"
    MSG_SUCCESS = "成功"
    
    MSG_FFMPEG_NOT_FOUND = "FFmpeg未找到"
    MSG_FFMPEG_NOT_INIT = "FFmpeg未初始化，請檢查設定"
    MSG_FFMPEG_INIT_FAILED = "FFmpeg初始化失敗"
    MSG_NO_VIDEO_FILES = "未找到視頻檔案"
    MSG_NO_FILES_ADDED = "請先添加要編碼的檔案"
    MSG_NO_OUTPUT_DIR = "請先選擇輸出目錄"
    MSG_ENCODING_COMPLETE = "編碼完成！"
    MSG_ENCODING_SUCCESS = "成功"
    MSG_ENCODING_FAILED = "失敗"
    
    # 檔案對話框
    SELECT_VIDEO_FILES = "選擇視頻檔案"
    SELECT_FOLDER = "選擇資料夾"
    VIDEO_FILES_FILTER = "視頻檔案 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.3gp *.ts *.mts);;所有檔案 (*.*)"
    
    # 日誌訊息
    LOG_FILES_ADDED = "添加了 {count} 個檔案"
    LOG_START_ENCODING = "開始編碼 {count} 個檔案"
    LOG_FFMPEG_UPDATED = "FFmpeg設定已更新"
    LOG_FILE_STARTED = "開始編碼 {current}/{total}: {filename}"
    LOG_FILE_FINISHED_SUCCESS = "完成 {current}/{total}: {filename} - {message}"
    LOG_FILE_FINISHED_FAILED = "失敗 {current}/{total}: {filename} - {message}"
    LOG_AUDIO_CODEC_AUTO_AAC = "檢測到音頻編碼與 MP4 容器可能不相容，已自動使用 AAC 編碼音頻（碼率 {bitrate}）"

    # 大小總計
    TOTAL_SIZE = "源檔案總大小：{size}"
    TOTAL_SIZE_ENCODED = "源檔案總大小：{original}，編碼後總大小：{encoded}"

    # 列表狀態
    STATUS_WAITING = "等待編碼"
    STATUS_ENCODING = "正在編碼"
    STATUS_DONE = "編碼完成"
    STATUS_FAILED = "編碼失敗"
    STATUS_PAUSED = "掛起"
    
    # ========== 設定對話框 ==========
    SETTINGS_TITLE = "編碼設定"
    
    # FFmpeg設定
    FFMPEG_SETTINGS = "FFmpeg設定"
    FFMPEG_PATH = "FFmpeg路徑"
    FFMPEG_PATH_TOOLTIP = (
        "FFmpeg可執行檔案的完整路徑。\n"
        "如果留空，程式將嘗試從系統PATH環境變數中查找FFmpeg。\n"
        "如果系統PATH中沒有FFmpeg，請在此處指定完整路徑。"
    )
    BROWSE = "瀏覽..."
    
    # 視頻編碼參數
    VIDEO_ENCODING_PARAMS = "視頻編碼參數"
    VIDEO_CODEC = "視頻編碼器"
    VIDEO_CODEC_TOOLTIP = (
        "選擇視頻編碼器：\n"
        "• libx264: H.264軟體編碼，相容性好，速度中等\n"
        "• libx265: HEVC軟體編碼，壓縮率高，速度較慢\n"
        "• libsvtav1: AV1軟體編碼，最新標準，壓縮率最高，速度最慢\n"
        "• av1_nvenc: AV1硬體編碼（NVIDIA GPU），需要RTX 40系列或更新\n"
        "• h264_nvenc: H.264硬體編碼（NVIDIA GPU），速度快\n"
        "• hevc_nvenc: HEVC硬體編碼（NVIDIA GPU），速度快，壓縮率高\n"
        "• copy: 直接複製視頻流，不進行重新編碼"
    )
    ENCODING_PRESET = "編碼預設"
    ENCODING_PRESET_TOOLTIP = (
        "編碼預設（速度與質量平衡）：\n"
        "• ultrafast ~ faster: 編碼速度快，檔案較大，質量略低\n"
        "• medium: 平衡選擇（推薦）\n"
        "• slow ~ veryslow: 編碼速度慢，檔案較小，質量更高\n"
        "注意：NVenc編碼器使用p1-p7預設（p1最快，p7最慢）"
    )
    CRF_QUALITY = "CRF質量 (0-51)"
    CRF_QUALITY_TOOLTIP = (
        "CRF（恆定速率因子）質量參數：\n"
        "• 0: 最高質量，檔案最大（無損）\n"
        "• 18-23: 高質量範圍（推薦23）\n"
        "• 28-32: 中等質量，檔案較小\n"
        "• 51: 最低質量，檔案最小\n"
        "注意：NVenc編碼器使用CQ參數（0-51），含義類似"
    )
    BIT_DEPTH = "位深度"
    BIT_DEPTH_TOOLTIP = (
        "視頻位深度：\n"
        "• 8bit: 標準位深度，相容性好，檔案較小\n"
        "• 10bit: 高精度，色彩漸變更平滑，暗部細節更好\n"
        "注意：10bit編碼需要編碼器支援，檔案會更大，編碼時間更長"
    )
    RESOLUTION = "解析度 (寬:高)"
    RESOLUTION_PLACEHOLDER = "例如: 1920:1080 或留空保持原解析度"
    RESOLUTION_TOOLTIP = (
        "輸出視頻解析度（寬度:高度）：\n"
        "• 格式：寬度:高度，例如 1920:1080（1080p）\n"
        "• 留空：保持原始解析度\n"
        "• 常用解析度：\n"
        "  - 4K: 3840:2160\n"
        "  - 1080p: 1920:1080\n"
        "  - 720p: 1280:720\n"
        "  - 480p: 854:480"
    )
    
    # 音頻編碼參數
    AUDIO_ENCODING_PARAMS = "音頻編碼參數"
    AUDIO_CODEC = "音頻編碼器"
    AUDIO_CODEC_TOOLTIP = (
        "音頻編碼器：\n"
        "• copy: 直接複製音頻流，不重新編碼（推薦，速度快）\n"
        "• aac: AAC編碼，相容性好，質量高\n"
        "• mp3: MP3編碼，相容性最好\n"
        "• opus: Opus編碼，壓縮率高，質量好"
    )
    AUDIO_BITRATE = "音頻碼率"
    AUDIO_BITRATE_PLACEHOLDER = "例如: 128k"
    AUDIO_BITRATE_TOOLTIP = (
        "音頻碼率（僅在重新編碼時有效）：\n"
        "• 格式：數值+k，例如 128k, 192k, 256k\n"
        "• 推薦值：\n"
        "  - 語音: 64k-96k\n"
        "  - 音樂: 128k-192k\n"
        "  - 高質量: 256k-320k\n"
        "• 選擇'copy'時此參數無效"
    )
    # 備用音頻編碼參數
    FALLBACK_AUDIO_SETTINGS = "備用音頻編碼參數"
    FALLBACK_AUDIO_CODEC = "備用音頻編碼器"
    FALLBACK_AUDIO_CODEC_TOOLTIP = (
        "當主音頻編碼設定為 copy 且與 MP4 容器不相容時，使用此編碼器重新編碼音頻：\n"
        "• aac: 相容性好，質量高（推薦）\n"
        "• opus: 壓縮率高，適合體積敏感場景\n"
        "• mp3: 相容性最好"
    )
    FALLBACK_AUDIO_BITRATE = "備用音頻碼率"
    FALLBACK_AUDIO_BITRATE_PLACEHOLDER = "例如: 192k"
    FALLBACK_AUDIO_BITRATE_TOOLTIP = (
        "備用音頻編碼時使用的碼率：\n"
        "• 僅在主音頻編碼為 copy 且源音頻不能直接封裝到 MP4 時生效\n"
        "• 不填寫時預設使用 192k"
    )
    
    # 字幕設定
    SUBTITLE_SETTINGS = "字幕設定"
    SUBTITLE_MODE = "字幕處理"
    SUBTITLE_MODE_TOOLTIP = (
        "字幕處理方式：\n"
        "• copy: 直接複製字幕流（推薦）\n"
        "• embed: 嵌入字幕到視頻（需要源檔案支援）\n"
        "• none: 不處理字幕，移除字幕流"
    )
    
    # 自訂參數
    CUSTOM_PARAMS = "自訂參數"
    USE_CUSTOM_COMMAND = "使用自訂FFmpeg命令行"
    USE_CUSTOM_COMMAND_TOOLTIP = "啟用後，將使用下方自訂命令範本，忽略其他編碼參數設定"
    CUSTOM_COMMAND_PLACEHOLDER = (
        "使用 {input} 和 {output} 作為佔位符\n"
        "例如: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}"
    )
    CUSTOM_COMMAND_TOOLTIP = (
        "自訂FFmpeg命令範本：\n"
        "• {input}: 輸入檔案路徑（自動替換）\n"
        "• {output}: 輸出檔案路徑（自動替換）\n"
        "• 範例：ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}\n"
        "注意：啟用此選項後，其他編碼參數將被忽略"
    )
    CUSTOM_ARGS_PLACEHOLDER = "額外的FFmpeg參數（空格分隔）"
    CUSTOM_ARGS_TOOLTIP = (
        "額外的FFmpeg參數（在標準參數之後添加）：\n"
        "• 格式：空格分隔的參數，例如 '-threads 4 -movflags +faststart'\n"
        "• 這些參數會追加到自動生成的FFmpeg命令末尾\n"
        "• 僅在未啟用自訂命令時有效"
    )
    
    # 提示音設定
    NOTIFICATION_SETTINGS = "提示音設定"
    ENABLE_NOTIFICATION_SOUND = "佇列完成後播放提示音"
    NOTIFICATION_SOUND_FILE = "提示音檔案"
    NOTIFICATION_SOUND_FILE_PLACEHOLDER = "選擇一個音訊檔（例如: wav, mp3）"
    MSG_SELECT_SOUND_FILE = "選擇提示音音訊檔"
    SOUND_FILES_FILTER = "音訊檔 (*.wav *.mp3 *.flac *.ogg *.m4a *.aac);;所有檔案 (*.*)"
    
    # 按鈕
    SAVE = "儲存"
    CANCEL = "取消"
    
    # 設定對話框訊息
    MSG_SELECT_FFMPEG = "選擇FFmpeg可執行檔案"
    MSG_EXECUTABLE_FILES = "可執行檔案 (*.exe);;所有檔案 (*.*)"
    MSG_FFMPEG_PATH_NOT_EXISTS = "指定的FFmpeg路徑不存在，將嘗試使用系統PATH中的FFmpeg"
    MSG_SETTINGS_SAVED = "設定已儲存"
    MSG_SETTINGS_SAVE_FAILED = "儲存設定失敗"
    
    # 進度訊息格式
    PROGRESS_FORMAT = "總體進度: {current}/{total} 個檔案 ({percent}%)"
    ENCODING_COMPLETE_FORMAT = "編碼完成: {success}/{total} 成功"
    CURRENT_FILE_FORMAT = "{filename} - {message}"

