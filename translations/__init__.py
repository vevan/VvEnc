"""
翻译模块 - Python模块方案的多语言支持
"""
from typing import Optional


class LanguageManager:
    """语言管理器 - 不使用Qt翻译系统"""
    
    SUPPORTED_LANGUAGES = {
        'zh_CN': '简体中文',
        'zh_TW': '繁體中文',
        'en_US': 'English',
        'ja_JP': '日本語'
    }
    
    def __init__(self, default_language: str = 'zh_CN'):
        self.current_language = default_language
        self.translations = self._load_language(default_language)
    
    def _load_language(self, lang_code: str):
        """加载指定语言的翻译"""
        try:
            if lang_code == 'zh_CN':
                from translations import zh_CN
                return zh_CN.Translations()
            elif lang_code == 'zh_TW':
                from translations import zh_TW
                return zh_TW.Translations()
            elif lang_code == 'en_US':
                from translations import en_US
                return en_US.Translations()
            elif lang_code == 'ja_JP':
                from translations import ja_JP
                return ja_JP.Translations()
            else:
                # 默认返回简体中文
                from translations import zh_CN
                return zh_CN.Translations()
        except ImportError:
            # 如果翻译文件不存在，使用简体中文作为后备
            try:
                from translations import zh_CN
                return zh_CN.Translations()
            except ImportError:
                # 如果连简体中文都没有，返回一个空对象
                return EmptyTranslations()
    
    def set_language(self, lang_code: str) -> bool:
        """设置当前语言"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_code
            self.translations = self._load_language(lang_code)
            return True
        return False
    
    def tr(self, key: str, default: Optional[str] = None) -> str:
        """
        翻译函数
        
        Args:
            key: 翻译键名（如 'MAIN_WINDOW_TITLE'）
            default: 如果找不到翻译，返回的默认值
        
        Returns:
            翻译后的文本
        """
        if hasattr(self.translations, key):
            return getattr(self.translations, key)
        else:
            # 如果找不到翻译，返回默认值或键名
            return default if default is not None else key
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_available_languages(self) -> dict:
        """获取可用语言列表"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_language_name(self, lang_code: str) -> str:
        """获取语言显示名称"""
        return self.SUPPORTED_LANGUAGES.get(lang_code, lang_code)


class EmptyTranslations:
    """空翻译类 - 当翻译文件不存在时使用"""
    def __getattr__(self, name):
        return name

