"""
批量视频编码工具 - 主入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("批量视频编码工具")
    app.setOrganizationName("VideoEncoder")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()




