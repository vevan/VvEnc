# 打包说明

## 使用方法

1. 双击运行 `build_exe.bat` 批处理文件
2. 等待打包完成（通常需要1-3分钟）
3. 打包完成后，exe文件位于 `dist\VvEnc.exe`

## 打包结果

- **输出位置**: `dist\VvEnc.exe`
- **文件大小**: 约 60-65 MB（包含所有依赖）
- **运行要求**: 
  - Windows 7 或更高版本
  - 无需安装Python
  - 需要系统已安装FFmpeg（或在设置中指定FFmpeg路径）

## 注意事项

1. **首次运行**: exe文件首次运行会在同目录下创建 `config.json` 配置文件
2. **FFmpeg依赖**: 程序需要FFmpeg才能工作，请确保：
   - FFmpeg已添加到系统PATH环境变量，或
   - 在程序设置中指定FFmpeg的完整路径
3. **文件分发**: 可以将exe文件复制到任何位置使用，无需其他文件
4. **杀毒软件**: 某些杀毒软件可能会误报，这是PyInstaller打包程序的常见情况，可以添加信任

## 图标设置

- 如果存在 `icon.ico` 文件，将自动使用
- 如果只有 `icon.png` 文件，会自动转换为 `icon.ico`
- 如果没有图标文件，将使用默认图标

## 打包参数说明

- `--onefile`: 打包成单个exe文件
- `--windowed`: 无控制台窗口（GUI程序）
- `--add-data`: 包含core和gui模块
- `--collect-all PyQt5`: 收集所有PyQt5依赖
- `--clean`: 清理临时文件

## 故障排除

如果打包失败：
1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 确保PyInstaller已安装：`pip install pyinstaller`
3. 检查Python版本（推荐3.8-3.12）

如果exe运行失败：
1. 检查是否有错误提示
2. 尝试在命令行运行查看详细错误
3. 确保系统已安装Visual C++ Redistributable

