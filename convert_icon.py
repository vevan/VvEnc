"""
将icon.png转换为icon.ico的辅助脚本
"""
try:
    from PIL import Image
    
    # 打开PNG图片
    img = Image.open('icon.png')
    
    # 转换为ICO格式，包含多个尺寸
    img.save('icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
    
    print("图标转换成功！已生成 icon.ico")
except ImportError:
    print("错误: 需要安装Pillow库")
    print("请运行: pip install Pillow")
except FileNotFoundError:
    print("错误: 未找到 icon.png 文件")
except Exception as e:
    print(f"转换失败: {e}")




