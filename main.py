"""
批量视频编码工具 - 主入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.config_manager import ConfigManager
from translations import LanguageManager


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("批量视频编码工具")
    app.setOrganizationName("VideoEncoder")
    
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




