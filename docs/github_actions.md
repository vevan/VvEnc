# GitHub Actions 自动打包说明

本项目提供了 GitHub Actions 工作流来自动构建可执行文件。

## 📋 工作流文件

### `build-multi-platform.yml` - 多平台构建

**功能**：同时构建 Windows、Linux、macOS 三个平台的可执行文件

**触发条件**：
- 推送以 `v` 开头的标签（如 `v1.0.0`）
- 手动触发（在 GitHub Actions 页面点击 "Run workflow"）

**输出**：
- Windows: `VvEnc.exe` + `VvEnc-Windows-x64-{version}.zip`
- Linux: `VvEnc` + `VvEnc-Ubuntu-x64-{version}.tar.gz`
- macOS: `VvEnc` + `VvEnc-Macos-x64-{version}.tar.gz`

## 🚀 使用方法

### 方法一：通过标签触发（推荐）

1. **创建并推送标签**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动触发构建**：
   - GitHub Actions 会自动开始构建
   - 构建完成后，如果标签以 `v` 开头，会自动创建 GitHub Release

3. **下载构建产物**：
   - 在 GitHub Actions 页面下载 Artifacts
   - 或在 Releases 页面下载发布包

### 方法二：手动触发

1. **进入 GitHub Actions 页面**：
   - 在仓库页面点击 "Actions" 标签
   - 选择 `Build Multi-Platform` 工作流

2. **手动运行**：
   - 点击 "Run workflow" 按钮
   - 可选择输入版本号（默认 `dev`）
   - 点击 "Run workflow" 开始构建

3. **下载构建产物**：
   - 构建完成后，在 Actions 页面下载 Artifacts

## 📦 构建产物

### Artifacts（构建产物）

构建完成后，可以在 Actions 页面下载：
- **名称**：`VvEnc-{platform}`（如 `VvEnc-windows-latest`、`VvEnc-ubuntu-latest`、`VvEnc-macos-latest`）
- **内容**：
  - 可执行文件（`VvEnc.exe` 或 `VvEnc`）
  - 压缩包（包含可执行文件和额外文件）

### Releases（发布包）

当推送以 `v` 开头的标签时，会自动创建 GitHub Release：
- **标题**：标签名称（如 `v1.0.0`）
- **内容**：自动生成的 Release Notes
- **附件**：各平台的压缩包

## ⚙️ 工作流配置说明

### 构建步骤

1. **环境设置**：使用 Python 3.11，Windows/Linux/macOS 最新版本
2. **依赖安装**：安装 `requirements.txt` 中的依赖 + PyInstaller + Pillow
3. **图标处理**：如果存在 `icon.png` 但无 `icon.ico`，自动转换
4. **清理旧文件**：删除之前的构建产物
5. **构建可执行文件**：使用 PyInstaller 打包
6. **复制额外文件**：复制 `ringtone.mp3` 和 `config.json`（如果存在）
7. **创建压缩包**：将构建产物打包
8. **上传 Artifacts**：上传到 GitHub Actions
9. **创建 Release**：如果是标签触发，自动创建 Release

### 自定义配置

如需修改构建参数，编辑 `.github/workflows/build-multi-platform.yml`：

- **Python 版本**：修改 `python-version: '3.11'`
- **PyInstaller 参数**：修改 `Build executable` 步骤中的命令
- **输出文件名**：修改 `Create release archive` 步骤

## 🔧 故障排除

### 构建失败

1. **检查日志**：在 Actions 页面查看详细错误信息
2. **常见问题**：
   - 依赖安装失败：检查 `requirements.txt`
   - PyInstaller 错误：检查 `main.py` 和导入路径
   - 图标转换失败：确保 `icon.png` 存在或直接提供 `icon.ico`

### 本地测试

在推送之前，可以在本地测试构建：

```bash
# Windows
.\build_exe.bat

# Linux/macOS（需要手动执行 PyInstaller 命令）
python -m PyInstaller --name="VvEnc" --onefile ...
```

## 📝 注意事项

1. **首次使用**：确保仓库已启用 GitHub Actions（默认已启用）
2. **权限**：创建 Release 需要仓库有写入权限（默认的 `GITHUB_TOKEN` 已足够）
3. **标签格式**：推荐使用语义化版本（如 `v1.0.0`、`v1.2.3-beta`）
4. **文件大小**：PyQt5 应用较大，构建可能需要 5-10 分钟
5. **Artifacts 保留**：默认保留 30 天，可在工作流中修改 `retention-days`

## 🔗 相关文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyInstaller 文档](https://pyinstaller.org/)
- [打包说明（中文）](package.md)
- [Building Executable (English)](package_en.md)

