# Batch Video Encoder

A batch video encoding tool based on PyQt5 and FFmpeg, supporting drag & drop, batch processing, directory structure preservation, multi-language UI, and more.

> Note: This project is developed with the help of AI under the author's supervision, mainly for the author's personal needs. Feature requests are welcome but may not always be accepted.

## ✨ Features

- **GUI**: Modern user interface based on PyQt5
- **Drag & drop**: Support for files and folders
- **Batch encoding**: Supports multiple formats (mp4, flv, webm, rm, rmvb, wmv, mov, etc.)
- **Unified output**: All outputs are encoded and packaged as `.mp4`
- **Directory structure preservation**: Keeps original folder structure when outputting
- **Task status management**: Waiting, Encoding, Completed, Failed, Paused
- **Real-time progress**: Overall and per-file progress, Windows taskbar progress indicator
- **Multi-language UI**: Simplified Chinese, Traditional Chinese, English, Japanese
- **File info loading dialog**: Progress dialog when loading a large number of files
- **Context menu**: Open source file, reveal in folder, change task status
- **Notification sound**: Optional custom sound when the queue finishes
- **Configuration memory**: Remembers window size, encoding options, last used directory, etc.

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- FFmpeg installed and available in `PATH`, or configured manually in the application's settings

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vevan/VvEnc.git
   cd VvEnc
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage

### Basic workflow

1. Start the program: `python main.py`
- Add files:
  - Click "Add Files" / "Add Folder", or
  - Drag & drop files/folders into the main window
- Configure encoding options through the "Settings" dialog
- Choose an output directory
- Click "Start Encoding" to begin

### Main features

- **Batch encoding**: Drag in multiple files or whole folders for batch processing.
- **Unified `.mp4` output**: All input formats are re-encoded and muxed into `.mp4`.
- **Directory preservation**: When dragging folder `A` and selecting output folder `B`, the tool will create `B/A/...` structure automatically.
- **Task status management**:
  - Status: Waiting, Encoding, Completed, Failed, Paused
  - Completed/failed/paused files are automatically skipped in the next run
  - Status can be changed from the context menu
- **Multi-language UI**: Switch between Simplified Chinese, Traditional Chinese, English, and Japanese.

## 📚 Documentation

- [Usage Guide (English)](usage_en.md) - Detailed usage instructions
- [Usage Guide (Chinese)](usage_cn.md) - Detailed usage guide in Chinese
- [Building Executable (English)](package_en.md) - How to build a standalone executable
- [打包说明（中文）](package.md) - 如何打包成独立可执行文件
- [GitHub Actions Auto Build (English)](github_actions_en.md) - Auto build with GitHub Actions
- [GitHub Actions 自动打包（中文）](github_actions.md) - 使用 GitHub Actions 自动构建

## ⚙️ Configuration

The application automatically saves settings to `config.json`, including:

- **FFmpeg path**: If FFmpeg is not in `PATH`, you can specify it manually
- **Encoding options**: Video codec, CRF, preset, resolution, bit depth, etc.
- **Audio options**: Audio codec, bitrate, fallback audio codec/bitrate
- **Window settings**: Window size, table column widths and order
- **Other settings**: Language, notification sound, last used directory, etc.

## 🔐 Code Signing & Security Notice

- The prebuilt Windows/macOS executables for this project are **not code-signed** and will appear as software from an "unknown publisher".
- On Windows, the first launch may trigger **SmartScreen** (e.g., "Windows protected your PC"):
  - Please make sure you downloaded the program from the official GitHub release page;
  - Click "More info" → "Run anyway" if you trust the source.
- This project is fully open source. If you are concerned about security, you are encouraged to build the executable yourself from source.

## 📄 License

This project is licensed under the **GNU General Public License (GPL)**.

- You are free to use, study, modify, and distribute this software;
- However, any redistributed modified version must also comply with the GPL;
- For full details, please refer to the [LICENSES](../LICENSES) file in the repository root or the official GNU website.

## 🤝 Contributing

Pull requests and issue reports are welcome.

## 🔗 Related Links

- [FFmpeg Official Site](https://ffmpeg.org/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [GNU Official Site (GPL)](https://www.gnu.org/licenses/gpl-3.0.en.html)



