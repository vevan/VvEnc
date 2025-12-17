# Batch Video Encoder

A batch video encoding tool based on PyQt5 and FFmpeg, supporting drag & drop, batch processing, directory structure preservation, and more.

## Features

- ✅ Graphical user interface (PyQt5)
- ✅ Drag & drop support for single files and folders
- ✅ Video encoding using FFmpeg
- ✅ Custom encoding parameters
- ✅ Directory structure preservation
- ✅ Real-time progress display
- ✅ Audio stream direct copy
- ✅ Configuration file save/load
- ✅ Multi-language support (Simplified Chinese, Traditional Chinese, English, Japanese)
- ✅ Task status management
- ✅ Windows taskbar progress indicator
- ✅ Notification sound on completion

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system (or specify the path in settings)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

1. Make sure FFmpeg is installed on your system (or specify the FFmpeg path in settings)
2. Run `python main.py` to start the application
3. Drag and drop video files or folders into the window
4. Configure encoding parameters
5. Select output directory
6. Start encoding

## Configuration

The application automatically saves configuration to `config.json`, including:
- FFmpeg path
- Encoding parameter presets
- Output directory
- Window size and layout
- Language settings
- Other preferences

## Documentation

- [Usage Guide (English)](usage_en.md) - Detailed usage instructions
- [Usage Guide (Chinese)](usage_cn.md) - 详细使用说明
- [Building Executable](package_en.md) - How to build standalone executable

## Key Features

### Batch Encoding
- Support for multiple file formats (mp4, flv, webm, rm, rmvb, wmv, mov, etc.)
- All outputs are unified to `.mp4` format
- Preserves directory structure when processing folders

### Task Status Management
- Status indicators: Waiting, Encoding, Completed, Failed, Paused
- Automatically skips completed/failed/paused files in next run
- Right-click menu to change file status

### Multi-language Support
- Simplified Chinese (简体中文)
- Traditional Chinese (繁體中文)
- English
- Japanese (日本語)

### Advanced Features
- Windows taskbar progress indicator
- Notification sound on queue completion
- File information loading progress dialog
- Right-click to open source file or reveal in folder
- Remembers last used directory for file dialogs

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

