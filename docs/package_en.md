# Building Executable

## Usage

1. Double-click to run the `build_exe.bat` batch file
2. Wait for the build to complete (usually takes 1-3 minutes)
3. After building, the exe file will be located at `dist\VvEnc.exe`

## Build Output

- **Output location**: `dist\VvEnc.exe`
- **File size**: Approximately 60-65 MB (includes all dependencies)
- **System requirements**: 
  - Windows 7 or higher
  - No Python installation required
  - FFmpeg must be installed on the system (or specify FFmpeg path in settings)

## Notes

1. **First run**: The exe file will create a `config.json` configuration file in the same directory on first run
2. **FFmpeg dependency**: The program requires FFmpeg to work. Please ensure:
   - FFmpeg is added to the system PATH environment variable, or
   - Specify the full path to FFmpeg in the program settings
3. **File distribution**: You can copy the exe file to any location and use it without other files
4. **Antivirus software**: Some antivirus software may give false positives. This is common with PyInstaller-packaged programs. You can add it to the whitelist.

## Icon Settings

- If `icon.ico` exists, it will be used automatically
- If only `icon.png` exists, it will be automatically converted to `icon.ico`
- If no icon file exists, the default icon will be used

## Build Parameters

- `--onefile`: Package into a single exe file
- `--windowed`: No console window (GUI program)
- `--add-data`: Include core and gui modules
- `--collect-all PyQt5`: Collect all PyQt5 dependencies
- `--clean`: Clean temporary files

## Troubleshooting

If the build fails:
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Make sure PyInstaller is installed: `pip install pyinstaller`
3. Check Python version (recommended 3.8-3.12)

If the exe fails to run:
1. Check for error messages
2. Try running from command line to see detailed errors
3. Make sure Visual C++ Redistributable is installed on the system

