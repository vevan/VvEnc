"""
批量视频编码工具 - 主入口
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from core.config_manager import ConfigManager
from translations import LanguageManager


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("VvEnc")
    app.setOrganizationName("vevanSoft")
    
    # 设置应用程序图标（任务栏图标）
    # 处理 PyInstaller 打包后的路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件：从临时目录读取
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(__file__)
    
    icon_path = os.path.join(base_path, "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 加载配置
    config_manager = ConfigManager()
    
    # 初始化语言管理器
    language = config_manager.get("language", "zh_CN")
    i18n_manager = LanguageManager(language)
    
    # 创建主窗口（传入语言管理器）
    window = MainWindow(i18n_manager=i18n_manager)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()




