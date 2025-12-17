# GitHub Actions Auto Build Guide

This project provides GitHub Actions workflows to automatically build executables.

## 📋 Workflow Files

### 1. `build.yml` - Windows Single Platform Build

**Use Case**: When only Windows version is needed

**Triggers**:
- Push tags starting with `v` (e.g., `v1.0.0`)
- Manual trigger (click "Run workflow" in GitHub Actions page)

**Outputs**:
- `VvEnc.exe` executable
- `VvEnc-Windows-x64-{version}.zip` archive

### 2. `build-multi-platform.yml` - Multi-Platform Build

**Use Case**: When Windows, Linux, and macOS versions are all needed

**Triggers**: Same as above

**Outputs**:
- Windows: `VvEnc.exe` + `VvEnc-Windows-x64-{version}.zip`
- Linux: `VvEnc` + `VvEnc-Ubuntu-x64-{version}.tar.gz`
- macOS: `VvEnc` + `VvEnc-Macos-x64-{version}.tar.gz`

## 🚀 Usage

### Method 1: Trigger via Tag (Recommended)

1. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Automatic build**:
   - GitHub Actions will automatically start building
   - After build completes, if the tag starts with `v`, it will automatically create a GitHub Release

3. **Download artifacts**:
   - Download Artifacts from GitHub Actions page
   - Or download release packages from Releases page

### Method 2: Manual Trigger

1. **Go to GitHub Actions page**:
   - Click "Actions" tab in the repository
   - Select the workflow (`Build Executable` or `Build Multi-Platform`)

2. **Run manually**:
   - Click "Run workflow" button
   - Optionally enter a version number (default: `dev`)
   - Click "Run workflow" to start

3. **Download artifacts**:
   - After build completes, download Artifacts from Actions page

## 📦 Build Artifacts

### Artifacts

After build completes, you can download from Actions page:
- **Name**: `VvEnc-Windows-x64` (single platform) or `VvEnc-{platform}` (multi-platform)
- **Contents**:
  - Executable file (`VvEnc.exe` or `VvEnc`)
  - Archive (contains executable and additional files)

### Releases

When pushing a tag starting with `v`, it will automatically create a GitHub Release:
- **Title**: Tag name (e.g., `v1.0.0`)
- **Content**: Auto-generated Release Notes
- **Attachments**: Platform-specific archives

## ⚙️ Workflow Configuration

### Build Steps

1. **Environment Setup**: Python 3.11, latest Windows/Linux/macOS
2. **Install Dependencies**: Install from `requirements.txt` + PyInstaller + Pillow
3. **Icon Processing**: Convert `icon.png` to `icon.ico` if needed
4. **Clean Old Files**: Remove previous build artifacts
5. **Build Executable**: Package using PyInstaller
6. **Copy Additional Files**: Copy `ringtone.mp3` and `config.json` (if exists)
7. **Create Archive**: Package build artifacts
8. **Upload Artifacts**: Upload to GitHub Actions
9. **Create Release**: Automatically create Release if triggered by tag

### Custom Configuration

To modify build parameters, edit `.github/workflows/build.yml` or `build-multi-platform.yml`:

- **Python Version**: Modify `python-version: '3.11'`
- **PyInstaller Parameters**: Modify commands in `Build executable` step
- **Output Filename**: Modify `Create release archive` step

## 🔧 Troubleshooting

### Build Failures

1. **Check Logs**: View detailed error messages in Actions page
2. **Common Issues**:
   - Dependency installation failed: Check `requirements.txt`
   - PyInstaller errors: Check `main.py` and import paths
   - Icon conversion failed: Ensure `icon.png` exists or provide `icon.ico` directly

### Local Testing

Before pushing, you can test the build locally:

```bash
# Windows
.\build_exe.bat

# Linux/macOS (need to run PyInstaller command manually)
python -m PyInstaller --name="VvEnc" --onefile ...
```

## 📝 Notes

1. **First Use**: Ensure GitHub Actions is enabled for the repository (enabled by default)
2. **Permissions**: Creating Releases requires write access (default `GITHUB_TOKEN` is sufficient)
3. **Tag Format**: Recommended to use semantic versioning (e.g., `v1.0.0`, `v1.2.3-beta`)
4. **File Size**: PyQt5 applications are large, builds may take 5-10 minutes
5. **Artifact Retention**: Default 30 days, can be modified in workflow `retention-days`

## 🔗 Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Building Executable (Chinese)](package.md)
- [Building Executable (English)](package_en.md)

