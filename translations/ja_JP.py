"""
日本語翻訳
"""
class Translations:
    """日本語翻訳クラス"""
    
    # ========== メインウィンドウ ==========
    MAIN_WINDOW_TITLE = "バッチ動画エンコーダー"
    
    # ツールバーボタン
    ADD_FILES = "ファイルを追加"
    ADD_FOLDER = "フォルダを追加"
    REMOVE_SELECTED = "選択を削除"
    CLEAR_LIST = "リストをクリア"
    SETTINGS = "設定"
    LANGUAGE = "言語"
    
    # ファイルリスト
    FILE_LIST_TITLE = "エンコード対象ファイル"
    COL_FILENAME = "ファイル名"
    COL_STATUS = "状態"
    COL_RESOLUTION = "解像度"
    COL_BITRATE = "ビットレート"
    COL_FRAMERATE = "フレームレート"
    COL_DURATION = "総時間"
    COL_VIDEO_CODEC = "動画コーデック"
    COL_FILE_SIZE = "ファイルサイズ"
    COL_AUDIO_CODEC = "音声コーデック"
    COL_AUDIO_BITRATE = "音声ビットレート"
    COL_BITS_PER_PIXEL = "10000ピクセル/フレームあたりのビット数"
    COL_PATH = "パス"
    FETCHING_INFO = "取得中..."
    NA = "N/A"
    
    # 出力設定
    OUTPUT_DIR = "出力ディレクトリ"
    OUTPUT_DIR_NOT_SET = "未設定"
    SELECT_OUTPUT_DIR = "出力ディレクトリを選択"
    
    # 進捗表示
    ENCODING_PROGRESS = "エンコード進捗"
    OVERALL_PROGRESS = "全体進捗"
    CURRENT_FILE_PROGRESS = "現在のファイル進捗"
    WAITING = "開始待ち..."
    PREPARING = "準備中..."
    ENCODING_COMPLETE = "エンコード完了"
    STOPPING = "エンコードを停止中..."
    LOG_TITLE = "ログ"
    LOADING_FILES = "読み込み中..."
    LOADING_FILES_INIT = "ファイル情報を読み込んでいます..."
    LOADING_FILES_PROGRESS = "読み込み中 {current}/{total} ファイル"
    
    # 制御ボタン
    START_ENCODING = "エンコード開始"
    STOP = "停止"
    
    # コンテキストメニュー
    OPEN_SOURCE_FILE = "ソースファイルを開く"
    REVEAL_SOURCE_FILE = "ファイルの場所を表示"
    
    # メッセージボックス
    MSG_ERROR = "エラー"
    MSG_WARNING = "警告"
    MSG_INFO = "情報"
    MSG_SUCCESS = "成功"
    
    MSG_FFMPEG_NOT_FOUND = "FFmpegが見つかりません"
    MSG_FFMPEG_NOT_INIT = "FFmpegが初期化されていません。設定を確認してください"
    MSG_FFMPEG_INIT_FAILED = "FFmpegの初期化に失敗しました"
    MSG_NO_VIDEO_FILES = "動画ファイルが見つかりません"
    MSG_NO_FILES_ADDED = "まずエンコードするファイルを追加してください"
    MSG_NO_OUTPUT_DIR = "まず出力ディレクトリを選択してください"
    MSG_ENCODING_COMPLETE = "エンコード完了！"
    MSG_ENCODING_SUCCESS = "成功"
    MSG_ENCODING_FAILED = "失敗"
    MSG_FILE_NOT_FOUND = "ファイルが見つかりません"
    MSG_OPEN_FILE_FAILED = "ファイルを開くのに失敗しました: {error}"
    MSG_REVEAL_FILE_FAILED = "ファイルの場所を表示するのに失敗しました: {error}"
    
    # ファイルダイアログ
    SELECT_VIDEO_FILES = "動画ファイルを選択"
    SELECT_FOLDER = "フォルダを選択"
    VIDEO_FILES_FILTER = "動画ファイル (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.3gp *.ts *.mts);;すべてのファイル (*.*)"
    
    # ログメッセージ
    LOG_FILES_ADDED = "{count} 個のファイルを追加しました"
    LOG_START_ENCODING = "{count} 個のファイルのエンコードを開始します"
    LOG_FFMPEG_UPDATED = "FFmpeg設定を更新しました"
    LOG_FILE_STARTED = "エンコード開始 {current}/{total}: {filename}"
    LOG_FILE_FINISHED_SUCCESS = "エンコード完了 {current}/{total}: {filename} - {message}"
    LOG_FILE_FINISHED_FAILED = "エンコード失敗 {current}/{total}: {filename} - {message}"
    LOG_AUDIO_CODEC_AUTO_AAC = "入力音声コーデックがMP4コンテナと互換性がない可能性があるため、音声をAAC（{bitrate}）で自動変換しました"

    # サイズ合計
    TOTAL_SIZE = "元ファイル合計サイズ：{size}"
    TOTAL_SIZE_ENCODED = "元ファイル合計サイズ：{original}、エンコード後合計サイズ：{encoded}"

    # リスト状態
    STATUS_WAITING = "エンコード待ち"
    STATUS_ENCODING = "エンコード中"
    STATUS_DONE = "エンコード完了"
    STATUS_FAILED = "エンコード失敗"
    STATUS_PAUSED = "一時停止"
    
    # ========== 設定ダイアログ ==========
    SETTINGS_TITLE = "エンコード設定"
    
    # FFmpeg設定
    FFMPEG_SETTINGS = "FFmpeg設定"
    FFMPEG_PATH = "FFmpegパス"
    FFMPEG_PATH_TOOLTIP = (
        "FFmpeg実行ファイルの完全パス。\n"
        "空欄の場合、プログラムはシステムPATH環境変数からFFmpegを検索します。\n"
        "システムPATHにFFmpegがない場合は、ここに完全パスを指定してください。"
    )
    BROWSE = "参照..."
    
    # 動画エンコードパラメータ
    VIDEO_ENCODING_PARAMS = "動画エンコードパラメータ"
    VIDEO_CODEC = "動画コーデック"
    VIDEO_CODEC_TOOLTIP = (
        "動画コーデックを選択：\n"
        "• libx264: H.264ソフトウェアエンコード、互換性良好、中程度の速度\n"
        "• libx265: HEVCソフトウェアエンコード、高圧縮率、速度が遅い\n"
        "• libsvtav1: AV1ソフトウェアエンコード、最新標準、最高圧縮率、最も遅い\n"
        "• av1_nvenc: AV1ハードウェアエンコード（NVIDIA GPU）、RTX 40シリーズ以降が必要\n"
        "• h264_nvenc: H.264ハードウェアエンコード（NVIDIA GPU）、高速\n"
        "• hevc_nvenc: HEVCハードウェアエンコード（NVIDIA GPU）、高速、高圧縮率\n"
        "• copy: 動画ストリームを直接コピー、再エンコードなし"
    )
    ENCODING_PRESET = "エンコードプリセット"
    ENCODING_PRESET_TOOLTIP = (
        "エンコードプリセット（速度と品質のバランス）：\n"
        "• ultrafast ~ faster: エンコード速度が速い、ファイルが大きい、品質がやや低い\n"
        "• medium: バランスの取れた選択（推奨）\n"
        "• slow ~ veryslow: エンコード速度が遅い、ファイルが小さい、品質が高い\n"
        "注意：NVencコーデックはp1-p7プリセットを使用（p1が最速、p7が最遅）"
    )
    CRF_QUALITY = "CRF品質 (0-51)"
    CRF_QUALITY_TOOLTIP = (
        "CRF（一定レートファクター）品質パラメータ：\n"
        "• 0: 最高品質、最大ファイル（ロスレス）\n"
        "• 18-23: 高品質範囲（23を推奨）\n"
        "• 28-32: 中品質、小さいファイル\n"
        "• 51: 最低品質、最小ファイル\n"
        "注意：NVencコーデックはCQパラメータ（0-51）を使用、意味は類似"
    )
    BIT_DEPTH = "ビット深度"
    BIT_DEPTH_TOOLTIP = (
        "動画ビット深度：\n"
        "• 8bit: 標準ビット深度、互換性良好、小さいファイル\n"
        "• 10bit: 高精度、色のグラデーションが滑らか、暗部の詳細が良い\n"
        "注意：10bitエンコードにはコーデックサポートが必要、ファイルが大きくなる、エンコード時間が長くなる"
    )
    RESOLUTION = "解像度 (幅:高さ)"
    RESOLUTION_PLACEHOLDER = "例: 1920:1080 または空欄で元の解像度を維持"
    RESOLUTION_TOOLTIP = (
        "出力動画解像度（幅:高さ）：\n"
        "• 形式：幅:高さ、例 1920:1080（1080p）\n"
        "• 空欄：元の解像度を維持\n"
        "• 一般的な解像度：\n"
        "  - 4K: 3840:2160\n"
        "  - 1080p: 1920:1080\n"
        "  - 720p: 1280:720\n"
        "  - 480p: 854:480"
    )
    
    # 音声エンコードパラメータ
    AUDIO_ENCODING_PARAMS = "音声エンコードパラメータ"
    AUDIO_CODEC = "音声コーデック"
    AUDIO_CODEC_TOOLTIP = (
        "音声コーデック：\n"
        "• copy: 音声ストリームを直接コピー、再エンコードなし（推奨、高速）\n"
        "• aac: AACエンコード、互換性良好、高品質\n"
        "• mp3: MP3エンコード、最高の互換性\n"
        "• opus: Opusエンコード、高圧縮率、高品質"
    )
    AUDIO_BITRATE = "音声ビットレート"
    AUDIO_BITRATE_PLACEHOLDER = "例: 128k"
    AUDIO_BITRATE_TOOLTIP = (
        "音声ビットレート（再エンコード時のみ有効）：\n"
        "• 形式：数値+k、例 128k, 192k, 256k\n"
        "• 推奨値：\n"
        "  - 音声: 64k-96k\n"
        "  - 音楽: 128k-192k\n"
        "  - 高品質: 256k-320k\n"
        "• 'copy'を選択した場合、このパラメータは無効"
    )
    # フォールバック音声エンコード
    FALLBACK_AUDIO_SETTINGS = "フォールバック音声エンコード"
    FALLBACK_AUDIO_CODEC = "フォールバック音声コーデック"
    FALLBACK_AUDIO_CODEC_TOOLTIP = (
        "メインの音声コーデックが copy に設定されており、ソース音声が MP4 コンテナに\n"
        "そのまま多重化できない場合、ここで指定したコーデックで再エンコードします：\n"
        "• aac: 互換性と品質のバランスが良い（推奨）\n"
        "• opus: 高圧縮率、サイズ重視の用途に適する\n"
        "• mp3: 互換性が最も高い"
    )
    FALLBACK_AUDIO_BITRATE = "フォールバック音声ビットレート"
    FALLBACK_AUDIO_BITRATE_PLACEHOLDER = "例: 192k"
    FALLBACK_AUDIO_BITRATE_TOOLTIP = (
        "フォールバック音声エンコードに使用するビットレート：\n"
        "• メインコーデックが copy で、かつソース音声が MP4 と非互換な場合にのみ有効\n"
        "• 未入力の場合、既定値 192k を使用"
    )
    
    # 字幕設定
    SUBTITLE_SETTINGS = "字幕設定"
    SUBTITLE_MODE = "字幕処理"
    SUBTITLE_MODE_TOOLTIP = (
        "字幕処理方法：\n"
        "• copy: 字幕ストリームを直接コピー（推奨）\n"
        "• embed: 字幕を動画に埋め込む（ソースファイルのサポートが必要）\n"
        "• none: 字幕を処理せず、字幕ストリームを削除"
    )
    
    # カスタムパラメータ
    CUSTOM_PARAMS = "カスタムパラメータ"
    USE_CUSTOM_COMMAND = "カスタムFFmpegコマンドラインを使用"
    USE_CUSTOM_COMMAND_TOOLTIP = "有効にすると、以下のカスタムコマンドテンプレートを使用し、他のエンコードパラメータ設定を無視します"
    CUSTOM_COMMAND_PLACEHOLDER = (
        "{input} と {output} をプレースホルダーとして使用\n"
        "例: ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}"
    )
    CUSTOM_COMMAND_TOOLTIP = (
        "カスタムFFmpegコマンドテンプレート：\n"
        "• {input}: 入力ファイルパス（自動置換）\n"
        "• {output}: 出力ファイルパス（自動置換）\n"
        "• 例：ffmpeg -i {input} -c:v libx264 -crf 23 -c:a copy {output}\n"
        "注意：このオプションを有効にすると、他のエンコードパラメータは無視されます"
    )
    CUSTOM_ARGS_PLACEHOLDER = "追加のFFmpegパラメータ（スペース区切り）"
    CUSTOM_ARGS_TOOLTIP = (
        "追加のFFmpegパラメータ（標準パラメータの後に追加）：\n"
        "• 形式：スペース区切りのパラメータ、例 '-threads 4 -movflags +faststart'\n"
        "• これらのパラメータは自動生成されたFFmpegコマンドの末尾に追加されます\n"
        "• カスタムコマンドが有効でない場合のみ有効"
    )
    
    # 通知音設定
    NOTIFICATION_SETTINGS = "通知音設定"
    ENABLE_NOTIFICATION_SOUND = "キュー完了時に通知音を再生する"
    NOTIFICATION_SOUND_FILE = "通知音ファイル"
    NOTIFICATION_SOUND_FILE_PLACEHOLDER = "音声ファイルを選択（例: wav, mp3）"
    MSG_SELECT_SOUND_FILE = "通知音の音声ファイルを選択"
    SOUND_FILES_FILTER = "音声ファイル (*.wav *.mp3 *.flac *.ogg *.m4a *.aac);;すべてのファイル (*.*)"
    
    # ボタン
    SAVE = "保存"
    CANCEL = "キャンセル"
    
    # 設定ダイアログメッセージ
    MSG_SELECT_FFMPEG = "FFmpeg実行ファイルを選択"
    MSG_EXECUTABLE_FILES = "実行ファイル (*.exe);;すべてのファイル (*.*)"
    MSG_FFMPEG_PATH_NOT_EXISTS = "指定されたFFmpegパスが存在しません。システムPATHのFFmpegを使用します"
    MSG_SETTINGS_SAVED = "設定を保存しました"
    MSG_SETTINGS_SAVE_FAILED = "設定の保存に失敗しました"
    
    # 進捗メッセージ形式
    PROGRESS_FORMAT = "全体進捗: {current}/{total} ファイル ({percent}%)"
    ENCODING_COMPLETE_FORMAT = "エンコード完了: {success}/{total} 成功"
    CURRENT_FILE_FORMAT = "{filename} - {message}"

