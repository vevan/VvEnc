## 简介 / Introduction

**简体中文：**  
这是一个基于 PyQt5 的**批量视频编码工具**，用于把多个视频统一转换为指定编码（默认 H.264）并输出为 `.mp4` 文件。  
支持目录拖放、保留目录结构、多语言界面、任务状态管理、尺寸统计和队列完成提示音等功能。

**English:**  
This is a PyQt5-based **batch video encoder** that converts multiple videos to a specified codec (H.264 by default) and outputs them as `.mp4` files.  
It supports folder drag & drop, directory structure preserving, multi-language UI, task status management, size summaries, and a notification sound when the queue is finished.

---

## 主要特性 / Key Features

**简体中文：**

- **批量编码**：支持拖入多个文件或整个文件夹进行批量编码。  
- **统一输出 `.mp4`**：无论输入格式（mp4/flv/webm/rm/rmvb/wmv/mov…），输出一律为 `.mp4`。  
- **目录结构保留**：拖入目录 `A` 输出到目录 `B` 时，自动生成 `B/A/...` 结构。  
- **任务状态管理**：  
  - 状态：等待编码、正在编码、编码完成、编码失败、挂起。  
  - 已完成/失败/挂起的文件会在下一次编码时自动跳过。  
  - 可通过右键菜单把行改为“等待编码”或“挂起”。  
  - 不同状态使用浅黄/浅蓝/浅绿/浅红/浅紫作为行背景色。  
- **列表统计**：显示源文件总大小，编码完成后会同时显示编码后总大小。  
- **详细进度与日志**：  
  - 显示整体进度和当前文件进度。  
  - 每个文件开始/结束编码都会写入日志（含成功/失败信息）。  
- **多语言支持**：简体中文 / 繁体中文 / 英语 / 日语，语言可在界面右上角按钮中切换。  
- **自定义编码参数**：  
  - 视频编码器（libx264、libx265、NVENC、AV1 等）  
  - CRF、预设、分辨率、位深  
  - 音频编码器与码率（copy / aac / mp3 / opus）  
  - 备用音频编码参数（当 `copy` 不适合 MP4 容器时自动改用 AAC/Opus/MP3）  
  - 自定义 FFmpeg 参数或完整命令模板。  
- **拖放支持**：直接把文件或文件夹拖到窗口中即可添加。  
- **提示音**：队列全部完成后，可选择是否播放自定义音频提示。  
- **窗口布局记忆**：记住窗口大小、表格列宽/顺序等设置。

**English:**

- **Batch encoding**: Drag & drop multiple files or folders to encode them in batch.  
- **Unified `.mp4` output**: All supported input formats (mp4, flv, webm, rm, rmvb, wmv, mov, etc.) are converted to `.mp4`.  
- **Directory structure preserving**: When dragging folder `A` and choosing output `B`, the tool outputs into `B/A/...`.  
- **Task status management**:  
  - Status: waiting, encoding, done, failed, paused.  
  - Files with status done/failed/paused are skipped in the next run.  
  - You can right-click rows to set status to “waiting” or “paused”.  
  - Different statuses are indicated by light yellow / blue / green / red / purple row backgrounds.  
- **Size summary**: Shows total size of source files, and total size of encoded files after completion.  
- **Progress & logs**:  
  - Shows overall progress and per-file progress.  
  - Logs each file when encoding starts and finishes, including success or failure messages.  
- **Multi-language UI**: Simplified Chinese, Traditional Chinese, English, and Japanese; language can be switched from the “Language” button.  
- **Custom encoding parameters**:  
  - Video codec (libx264, libx265, NVENC, AV1, etc.)  
  - CRF, preset, resolution, bit depth  
  - Audio codec & bitrate (copy / aac / mp3 / opus)  
  - Fallback audio codec settings used when `copy` is incompatible with MP4  
  - Extra FFmpeg arguments or full custom command template.  
- **Drag & drop**: Simply drag files or folders into the main window to add them.  
- **Notification sound**: Optionally play a custom audio file when the whole queue is finished.  
- **Layout persistence**: Remembers window size and table column widths/order.

---

## 基本使用方法 / Basic Usage

### 1. 启动程序 / Start the Application

**中文：**

- 在命令行中进入程序目录，激活虚拟环境（如有），运行：  
  `python main.py`  
- 或使用你打包好的可执行文件（如 `VideoEncoder.exe`）直接启动。

**English:**

- In a terminal, go to the project directory, activate your virtual environment if any, and run:  
  `python main.py`  
- Or launch your packaged executable (e.g. `VideoEncoder.exe`) directly.

---

### 2. 添加待编码文件 / Add Files to Encode

**中文：**

- 点击工具栏上的：  
  - **“添加文件”**：从文件对话框中选择一个或多个视频文件。  
  - **“添加文件夹”**：选择包含视频的文件夹，程序会递归扫描其中的视频文件。  
- 或者：**直接把文件/文件夹拖到主窗口**。  
- 表格中会显示：文件名、状态、分辨率、码率、帧率、总时长、视频/音频编码、文件大小等信息。  
- 左下角会显示**源文件总大小**。

**English:**

- Use toolbar buttons:  
  - **“Add Files”**: choose one or more video files.  
  - **“Add Folder”**: select a folder; the tool scans it recursively for video files.  
- Or **drag & drop** files/folders into the main window.  
- The table will show filename, status, resolution, bitrate, frame rate, duration, codecs, file size, etc.  
- The total source size is shown at the bottom-left.

---

### 3. 设置输出目录 / Set Output Directory

**中文：**

- 在主窗口中部的“输出目录”一栏：  
  - 点击 **“选择输出目录”** 按钮，选择一个文件夹作为输出位置。  
- 所有编码后的视频都会输出到这个目录下，并按拖入的目录结构生成子目录。

**English:**

- In the “Output Directory” section:  
  - Click **“Select Output Directory”** and choose a folder.  
- All encoded videos will be written into this folder, preserving the input directory structure.

---

### 4. 配置编码参数 / Configure Encoding Settings

**中文：**

1. 点击工具栏右侧的 **“设置”** 打开设置对话框。  
2. 在“视频编码参数”中选择：  
   - 视频编码器（如 `libx264` / `libx265` / `h264_nvenc`）；  
   - 编码预设（速度 vs 质量）；  
   - CRF 质量、分辨率、位深。  
3. 在“音频编码参数”中：  
   - 选择音频编码器：`copy` / `aac` / `mp3` / `opus`；  
   - 根据需要填写音频码率（如 `192k`）。  
4. 在“备用音频编码参数”中：  
   - 设置备用音频编码器（默认 `aac`）；  
   - 设置备用码率（默认 `192k`）。  
   - 当主音频编码为 `copy` 且源音频与 MP4 容器不兼容时，会自动使用这里的设置转码。  
5. 如需高级控制，可在“自定义参数”中填写额外 FFmpeg 参数或完整命令模板。  
6. 点击 **“保存”** 后设置生效。

**English:**

1. Click **“Settings”** on the right side of the toolbar.  
2. In “Video Encoding Parameters”:  
   - Choose the video codec (e.g. `libx264`, `libx265`, `h264_nvenc`);  
   - Select encoding preset, CRF, resolution, and bit depth.  
3. In “Audio Encoding Parameters”:  
   - Choose audio codec: `copy`, `aac`, `mp3`, or `opus`;  
   - Optionally set audio bitrate (e.g. `192k`).  
4. In “Fallback Audio Encoding”:  
   - Set a fallback codec (default `aac`);  
   - Set fallback bitrate (default `192k`).  
   - When the main codec is `copy` and source audio is incompatible with MP4, this fallback is used.  
5. For advanced control, add extra FFmpeg args or a full custom command template.  
6. Click **“Save”** to apply settings.

---

### 5. 管理任务状态 / Manage Task Status

**中文：**

- 默认新加入的文件状态为 **“等待编码”**（浅黄底）。  
- 点击 **“开始编码”** 时：  
  - 仅对状态为“等待编码”的文件进行编码；  
  - 当前编码中的文件状态为“正在编码”（浅蓝）；  
  - 成功后变为“编码完成”（浅绿）；  
  - 失败则为“编码失败”（浅红）。  
- 编码结束后，如需重新编码某些文件：  
  - 在列表中选中行，右键 → 选择 **“设为等待编码”**；  
  - 对不想再编码的文件可设置为 **“挂起”**（浅紫），后续会被自动跳过。

**English:**

- Newly added files start with status **“Waiting”** (light yellow).  
- When you click **“Start Encoding”**:  
  - Only files with status “Waiting” are processed;  
  - The current file becomes “Encoding” (light blue);  
  - On success it turns to “Completed” (light green);  
  - On failure it becomes “Failed” (light red).  
- To re-encode specific files after a run:  
  - Select rows, right-click → set to **“Waiting”**;  
  - For files you want to skip in future, set them to **“Paused”** (light purple).

---

### 6. 查看进度与日志 / Check Progress & Logs

**中文：**

- 中间的信息区域分为左右两部分：  
  - 左侧：总体进度条、当前文件进度条和文字说明。  
  - 右侧：日志窗口（固定约 6 行高度）。  
- 日志会记录：  
  - 添加文件的数量；  
  - 每个文件开始编码 / 结束编码的消息；  
  - FFmpeg 返回的成功/失败信息；  
  - 自动切换备用音频编码时的提示。

**English:**

- The middle information area has:  
  - Left: overall progress bar, current file progress bar and labels;  
  - Right: a fixed-height log window (around 6 lines).  
- Logs include:  
  - Number of files added;  
  - Start/finish messages for each file;  
  - FFmpeg success/failure messages;  
  - Notifications when fallback audio encoding is used.

---

### 7. 队列完成与提示音 / Queue Completion & Notification Sound

**中文：**

- 当整个队列编码完成后：  
  - 会弹出一个结果对话框，显示成功/失败数量；  
  - 如果在设置中勾选了 **“队列完成后播放提示音”** 并选择了音频文件，  
    则会自动播放该提示音一次。

**English:**

- When the whole queue is finished:  
  - A message box pops up showing how many files succeeded/failed;  
  - If **“Play sound when queue is finished”** is enabled and a sound file is set,  
    that audio file will be played once as a notification.

---

### 8. 多语言切换 / Language Switching

**中文：**

- 窗口右上方有一个 **“Language”** 按钮：  
  - 点击后选择 `简体中文 / 繁體中文 / English / 日本語`；  
  - 绝大部分界面文字会立即更新，无需重启；  
  - “Language” 按钮本身在所有语言下都显示为英文 “Language”。

**English:**

- On the top-right, click the **“Language”** button:  
  - Choose among Simplified Chinese, Traditional Chinese, English, or Japanese;  
  - Most UI texts update immediately without restarting;  
  - The button label itself is always “Language” in all languages.


