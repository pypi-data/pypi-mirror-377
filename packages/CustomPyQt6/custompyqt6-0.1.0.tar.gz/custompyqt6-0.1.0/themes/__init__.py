from ..core.styles import StyleManager

def set_theme(theme_name):
    manager = StyleManager()
    manager.set_theme(theme_name)
    return manager.get_stylesheet()

def get_available_themes():
    manager = StyleManager()
    return list(manager.themes.keys())