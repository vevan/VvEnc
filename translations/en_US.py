"""
English translations
"""
class Translations:
    """English translation class"""
    
    # ========== Main Window ==========
    MAIN_WINDOW_TITLE = "Batch Video Encoder"
    
    # Toolbar buttons
    ADD_FILES = "Add Files"
    ADD_FOLDER = "Add Folder"
    REMOVE_SELECTED = "Remove Selected"
    CLEAR_LIST = "Clear List"
    SETTINGS = "Settings"
    LANGUAGE = "Language"
    
    # File list
    FILE_LIST_TITLE = "Files to Encode"
    COL_FILENAME = "Filename"
    COL_STATUS = "Status"
    COL_RESOLUTION = "Resolution"
    COL_BITRATE = "Bitrate"
    COL_FRAMERATE = "Frame Rate"
    COL_DURATION = "Duration"
    COL_VIDEO_CODEC = "Video Codec"
    COL_FILE_SIZE = "File Size"
    COL_AUDIO_CODEC = "Audio Codec"
    COL_AUDIO_BITRATE = "Audio Bitrate"
    COL_BITS_PER_PIXEL = "Bits per 10000px/frame"
    COL_PATH = "Path"
    FETCHING_INFO = "Fetching..."
    NA = "N/A"
    
    # Output settings
    OUTPUT_DIR = "Output Directory"
    OUTPUT_DIR_NOT_SET = "Not set"
    SELECT_OUTPUT_DIR = "Select Output Directory"
    
    # Progress display
    ENCODING_PROGRESS = "Encoding Progress"
    OVERALL_PROGRESS = "Overall Progress"
    CURRENT_FILE_PROGRESS = "Current File Progress"
    WAITING = "Waiting..."
    PREPARING = "Preparing..."
    ENCODING_COMPLETE = "Encoding Complete"
    STOPPING = "Stopping encoding..."
    LOG_TITLE = "Log"
    
    # Control buttons
    START_ENCODING = "Start Encoding"
    STOP = "Stop"
    
    # Message boxes
    MSG_ERROR = "Error"
    MSG_WARNING = "Warning"
    MSG_INFO = "Information"
    MSG_SUCCESS = "Success"
    
    MSG_FFMPEG_NOT_FOUND = "FFmpeg not found"
    MSG_FFMPEG_NOT_INIT = "FFmpeg not initialized, please check settings"
    MSG_FFMPEG_INIT_FAILED = "FFmpeg initialization failed"
    MSG_NO_VIDEO_FILES = "No video files found"
    MSG_NO_FILES_ADDED = "Please add files to encode first"
    MSG_NO_OUTPUT_DIR = "Please select output directory first"
    MSG_ENCODING_COMPLETE = "Encoding Complete!"
    MSG_ENCODING_SUCCESS = "Success"
    MSG_ENCODING_FAILED = "Failed"
    
    # File dialogs
    SELECT_VIDEO_FILES = "Select Video Files"
    SELECT_FOLDER = "Select Folder"
    VIDEO_FILES_FILTER = "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.3gp *.ts *.mts);;All Files (*.*)"
    
    # Log messages
    LOG_FILES_ADDED = "Added {count} files"
    LOG_START_ENCODING = "Starting encoding {count} files"
    LOG_FFMPEG_UPDATED = "FFmpeg settings updated"
    LOG_FILE_STARTED = "Start encoding {current}/{total}: {filename}"
    LOG_FILE_FINISHED_SUCCESS = "Finished {current}/{total}: {filename} - {message}"
    LOG_FILE_FINISHED_FAILED = "Failed {current}/{total}: {filename} - {message}"
    LOG_AUDIO_CODEC_AUTO_AAC = "Input audio codec may be incompatible with MP4 container, switched to AAC audio encoding ({bitrate}) automatically"

    # Size summary
    TOTAL_SIZE = "Original total size: {size}"
    TOTAL_SIZE_ENCODED = "Original total size: {original}, Encoded total size: {encoded}"

    # List item status
    STATUS_WAITING = "Waiting"
    STATUS_ENCODING = "Encoding"
    STATUS_DONE = "Completed"
    STATUS_FAILED = "Failed"
    STATUS_PAUSED = "Paused"
    
    # ========== Settings Dialog ==========
    SETTINGS_TITLE = "Encoding Settings"
    
    # FFmpeg settings
    FFMPEG_SETTINGS = "FFmpeg Settings"
    FFMPEG_PATH = "FFmpeg Path"
    FFMPEG_PATH_TOOLTIP = (
        "Full path to FFmpeg executable.\n"
        "If left empty, the program will try to find FFmpeg from system PATH.\n"
        "If FFmpeg is not in system PATH, please specify the full path here."
    )
    BROWSE = "Browse..."
    
    # Video encoding parameters
    VIDEO_ENCODING_PARAMS = "Video Encoding Parameters"
    VIDEO_CODEC = "Video Codec"
    VIDEO_CODEC_TOOLTIP = (
        "Select video codec:\n"
        "• libx264: H.264 software encoding, good compatibility, medium speed\n"
        "• libx265: HEVC software encoding, high compression, slower speed\n"
        "• libsvtav1: AV1 software encoding, latest standard, highest compression, slowest speed\n"
        "• av1_nvenc: AV1 hardware encoding (NVIDIA GPU), requires RTX 40 series or newer\n"
        "• h264_nvenc: H.264 hardware encoding (NVIDIA GPU), fast speed\n"
        "• hevc_nvenc: HEVC hardware encoding (NVIDIA GPU), fast speed, high compression\n"
        "• copy: Copy video stream directly without re-encoding"
    )
    ENCODING_PRESET = "Encoding Preset"
    ENCODING_PRESET_TOOLTIP = (
        "Encoding preset (speed vs quality balance):\n"
        "• ultrafast ~ faster: Fast encoding, larger files, slightly lower quality\n"
        "• medium: Balanced choice (recommended)\n"
        "• slow ~ veryslow: Slow encoding, smaller files, higher quality\n"
        "Note: NVenc codecs use p1-p7 presets (p1 fastest, p7 slowest)"
    )
    CRF_QUALITY = "CRF Quality (0-51)"
    CRF_QUALITY_TOOLTIP = (
        "CRF (Constant Rate Factor) quality parameter:\n"
        "• 0: Highest quality, largest files (lossless)\n"
        "• 18-23: High quality range (recommended 23)\n"
        "• 28-32: Medium quality, smaller files\n"
        "• 51: Lowest quality, smallest files\n"
        "Note: NVenc codecs use CQ parameter (0-51), similar meaning"
    )
    BIT_DEPTH = "Bit Depth"
    BIT_DEPTH_TOOLTIP = (
        "Video bit depth:\n"
        "• 8bit: Standard bit depth, good compatibility, smaller files\n"
        "• 10bit: High precision, smoother color gradients, better dark details\n"
        "Note: 10bit encoding requires codec support, larger files, longer encoding time"
    )
    RESOLUTION = "Resolution (width:height)"
    RESOLUTION_PLACEHOLDER = "e.g.: 1920:1080 or leave empty to keep original resolution"
    RESOLUTION_TOOLTIP = (
        "Output video resolution (width:height):\n"
        "• Format: width:height, e.g. 1920:1080 (1080p)\n"
        "• Leave empty: Keep original resolution\n"
        "• Common resolutions:\n"
        "  - 4K: 3840:2160\n"
        "  - 1080p: 1920:1080\n"
        "  - 720p: 1280:720\n"
        "  - 480p: 854:480"
    )
    
    # Audio encoding parameters
    AUDIO_ENCODING_PARAMS = "Audio Encoding Parameters"
    AUDIO_CODEC = "Audio Codec"
    AUDIO_CODEC_TOOLTIP = (
        "Audio codec:\n"
        "• copy: Copy audio stream directly without re-encoding (recommended, fast)\n"
        "• aac: AAC encoding, good compatibility, high quality\n"
        "• mp3: MP3 encoding, best compatibility\n"
        "• opus: Opus encoding, high compression, good quality"
    )
    AUDIO_BITRATE = "Audio Bitrate"
    AUDIO_BITRATE_PLACEHOLDER = "e.g.: 128k"
    AUDIO_BITRATE_TOOLTIP = (
        "Audio bitrate (only effective when re-encoding):\n"
        "• Format: number+k, e.g. 128k, 192k, 256k\n"
        "• Recommended values:\n"
        "  - Speech: 64k-96k\n"
        "  - Music: 128k-192k\n"
        "  - High quality: 256k-320k\n"
        "• This parameter is ignored when 'copy' is selected"
    )
    # Fallback audio encoding
    FALLBACK_AUDIO_SETTINGS = "Fallback Audio Encoding"
    FALLBACK_AUDIO_CODEC = "Fallback Audio Codec"
    FALLBACK_AUDIO_CODEC_TOOLTIP = (
        "When the main audio codec is set to copy but the source audio cannot be muxed into MP4,\n"
        "the audio will be re-encoded using this codec:\n"
        "• aac: Good compatibility and quality (recommended)\n"
        "• opus: High compression, suitable for size-sensitive scenarios\n"
        "• mp3: Best compatibility"
    )
    FALLBACK_AUDIO_BITRATE = "Fallback Audio Bitrate"
    FALLBACK_AUDIO_BITRATE_PLACEHOLDER = "e.g.: 192k"
    FALLBACK_AUDIO_BITRATE_TOOLTIP = (
        "Bitrate used when applying fallback audio encoding:\n"
        "• Takes effect only when main codec is copy and source audio is incompatible with MP4\n"
        "• If left empty, defaults to 192k"
    )
    
    # Subtitle settings
    SUBTITLE_SETTINGS = "Subtitle Settings"
    SUBTITLE_MODE = "Subtitle Mode"
    SUBTITLE_MODE_TOOLTIP = (
        "Subtitle processing mode:\n"
        "• copy: Copy subtitle stream directly (recommended)\n"
        "• embed: Embed subtitles into video (requires source file support)\n"
        "• none: Do not process subtitles, remove subtitle stream"
    )
    
    # Custom parameters
    CUSTOM_PARAMS = "Custom Parameters"
    USE_CUSTOM_COMMAND = "Use Custom FFmpeg Command"
    USE_CUSTOM_COMMAND_TOOLTIP = "When enabled, use the custom command template below, ignoring other encoding parameter settings"
    CUSTOM_COMMAND_PLACEHOLDER = (
        "Use {input} and {output} as placeholders\n"
        "e.g.: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}"
    )
    CUSTOM_COMMAND_TOOLTIP = (
        "Custom FFmpeg command template:\n"
        "• {input}: Input file path (automatically replaced)\n"
        "• {output}: Output file path (automatically replaced)\n"
        "• Example: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}\n"
        "Note: When this option is enabled, other encoding parameters will be ignored"
    )
    CUSTOM_ARGS_PLACEHOLDER = "Additional FFmpeg parameters (space-separated)"
    CUSTOM_ARGS_TOOLTIP = (
        "Additional FFmpeg parameters (added after standard parameters):\n"
        "• Format: space-separated parameters, e.g. '-threads 4 -movflags +faststart'\n"
        "• These parameters will be appended to the end of the auto-generated FFmpeg command\n"
        "• Only effective when custom command is not enabled"
    )
    
    # Notification sound settings
    NOTIFICATION_SETTINGS = "Notification Sound"
    ENABLE_NOTIFICATION_SOUND = "Play sound when queue is finished"
    NOTIFICATION_SOUND_FILE = "Sound File"
    NOTIFICATION_SOUND_FILE_PLACEHOLDER = "Select an audio file (e.g.: wav, mp3)"
    MSG_SELECT_SOUND_FILE = "Select notification sound file"
    SOUND_FILES_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a *.aac);;All Files (*.*)"
    
    # Buttons
    SAVE = "Save"
    CANCEL = "Cancel"
    
    # Settings dialog messages
    MSG_SELECT_FFMPEG = "Select FFmpeg Executable"
    MSG_EXECUTABLE_FILES = "Executable Files (*.exe);;All Files (*.*)"
    MSG_FFMPEG_PATH_NOT_EXISTS = "The specified FFmpeg path does not exist, will try to use FFmpeg from system PATH"
    MSG_SETTINGS_SAVED = "Settings saved"
    MSG_SETTINGS_SAVE_FAILED = "Failed to save settings"
    
    # Progress message formats
    PROGRESS_FORMAT = "Overall Progress: {current}/{total} files ({percent}%)"
    ENCODING_COMPLETE_FORMAT = "Encoding Complete: {success}/{total} successful"
    CURRENT_FILE_FORMAT = "{filename} - {message}"

