## Introduction

This is a PyQt5-based **batch video encoder** that converts multiple videos to a specified codec (H.264 by default) and outputs them as `.mp4` files.  
It supports folder drag & drop, directory structure preserving, multi-language UI, task status management, size summaries, and a notification sound when the queue is finished.

---

## Environment & FFmpeg Configuration

- **FFmpeg** must be installed on your system.  
- There are two ways for the program to locate FFmpeg:
  1. **Add FFmpeg to the system `PATH` (recommended)**  
     - Add the directory containing the FFmpeg executable (e.g. `C:\ffmpeg\bin`) to your system `PATH`;  
     - The program will automatically find `ffmpeg.exe` from `PATH`.
  2. **Set the FFmpeg path manually in “Settings”**  
     - Open **“Settings”** on the right side of the toolbar;  
     - In the top “FFmpeg Settings” section, select the full path to `ffmpeg.exe`;  
     - After saving, the program will prefer this path.
- If FFmpeg is neither in `PATH` nor configured in Settings, the program will show messages like “FFmpeg not initialized, please check settings” when starting or encoding.

---

## Key Features

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
  - Video codec (libx264, libx265, NVENC, AV1, etc.);  
  - CRF, preset, resolution, bit depth;  
  - Audio codec & bitrate (copy / aac / mp3 / opus);  
  - Fallback audio codec settings used when `copy` is incompatible with MP4;  
  - Extra FFmpeg arguments or a full custom command template.  
- **Drag & drop**: Simply drag files or folders into the main window to add them.  
- **Notification sound**: Optionally play a custom audio file when the whole queue is finished.  
- **Layout persistence**: Remembers window size and table column widths/order.

---

## Basic Usage

### 1. Start the Application

- In a terminal, go to the project directory, activate your virtual environment if any, and run:  
  `python main.py`  
- Or launch your packaged executable (e.g. `VideoEncoder.exe`) directly.

### 2. Add Files to Encode

- Use toolbar buttons:  
  - **“Add Files”**: choose one or more video files;  
  - **“Add Folder”**: select a folder; the tool scans it recursively for video files.  
- Or **drag & drop** files/folders into the main window.  
- The table will show filename, status, resolution, bitrate, frame rate, duration, codecs, file size, etc.  
- The total source size is shown at the bottom-left.

### 3. Set Output Directory

- In the “Output Directory” section:  
  - Click **“Select Output Directory”** and choose a folder.  
- All encoded videos will be written into this folder, preserving the input directory structure.

### 4. Configure Encoding Settings

1. Click **“Settings”** on the right side of the toolbar.  
2. In “Video Encoding Parameters”:  
   - Choose the video codec (e.g. `libx264`, `libx265`, `h264_nvenc`);  
   - Select encoding preset, CRF, resolution, and bit depth.  
3. In “Audio Encoding Parameters”:  
   - Choose audio codec: `copy`, `aac`, `mp3`, or `opus`;  
   - Optionally set audio bitrate (e.g. `192k`).  
4. In “Fallback Audio Encoding”:  
   - Set a fallback codec (default `aac`);  
   - Set fallback bitrate (default `192k`);  
   - When the main codec is `copy` and source audio is incompatible with MP4, this fallback is used.  
5. For advanced control, add extra FFmpeg args or a full custom command template.  
6. Click **“Save”** to apply settings.

### 5. Manage Task Status

- Newly added files start with status **“Waiting”** (light yellow).  
- When you click **“Start Encoding”**:  
  - Only files with status “Waiting” are processed;  
  - The current file becomes “Encoding” (light blue);  
  - On success it turns to “Completed” (light green);  
  - On failure it becomes “Failed” (light red).  
- To re-encode specific files after a run:  
  - Select rows, right-click → set to **“Waiting”**;  
  - For files you want to skip in future, set them to **“Paused”** (light purple).

### 6. Check Progress & Logs

- The middle information area has:  
  - Left: overall progress bar, current file progress bar and labels;  
  - Right: a fixed-height log window (around 6 lines).  
- Logs include:  
  - Number of files added;  
  - Start/finish messages for each file;  
  - FFmpeg success/failure messages;  
  - Notifications when fallback audio encoding is used.

### 7. Queue Completion & Notification Sound

- When the whole queue is finished:  
  - A message box pops up showing how many files succeeded/failed;  
  - If **“Play sound when queue is finished”** is enabled and a sound file is set,  
    that audio file will be played once as a notification.

### 8. Language Switching

- On the top-right, click the **“Language”** button:  
  - Choose among Simplified Chinese, Traditional Chinese, English, or Japanese;  
  - Most UI texts update immediately without restarting;  
  - The button label itself is always “Language” in all languages.


