class StyleManager:
    def __init__(self):
        self.themes = {
            "dark": {
                "background": "#2b2b2b",
                "foreground": "#ffffff",
                "primary": "#bb86fc",
                "secondary": "#03dac6",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#cf6679",
                "text": "#ffffff",
                "border": "#444444"
            },
            "light": {
                "background": "#f5f5f5",
                "foreground": "#000000",
                "primary": "#6200ee",
                "secondary": "#03dac6",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#b00020",
                "text": "#000000",
                "border": "#cccccc"
            },
            "blue": {
                "background": "#1e3a5f",
                "foreground": "#ffffff",
                "primary": "#4fc3f7",
                "secondary": "#0288d1",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#f44336",
                "text": "#ffffff",
                "border": "#2c4f7c"
            }
        }
        self.current_theme = "dark"

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name

    def get_theme(self):
        return self.themes[self.current_theme]

    def get_stylesheet(self):
        theme = self.get_theme()

        return f"""
        QMainWindow, QDialog {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}

        .custom-button {{
            background-color: {theme['primary']};
            color: {theme['foreground']};
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }}

        .custom-button:hover {{
            background-color: {theme['secondary']};
        }}

        .custom-button:pressed {{
            background-color: {theme['primary']};
        }}

        .custom-label {{
            color: {theme['text']};
            padding: 5px;
        }}

        .custom-entry {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 2px solid {theme['border']};
            border-radius: 5px;
            padding: 5px;
            selection-background-color: {theme['primary']};
        }}

        .custom-entry:focus {{
            border: 2px solid {theme['primary']};
        }}

        .custom-combobox {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 2px solid {theme['border']};
            border-radius: 5px;
            padding: 5px;
        }}

        .custom-combobox:focus {{
            border: 2px solid {theme['primary']};
        }}

        .custom-combobox QAbstractItemView {{
            background-color: {theme['background']};
            color: {theme['text']};
            selection-background-color: {theme['primary']};
        }}

        .custom-checkbox {{
            color: {theme['text']};
            spacing: 5px;
        }}

        .custom-checkbox::indicator {{
            width: 15px;
            height: 15px;
            border: 2px solid {theme['border']};
            border-radius: 3px;
            background: {theme['background']};
        }}

        .custom-checkbox::indicator:checked {{
            background: {theme['primary']};
            border: 2px solid {theme['primary']};
        }}

        .custom-slider {{
            height: 10px;
        }}

        .custom-slider::groove:horizontal {{
            border: 1px solid {theme['border']};
            height: 10px;
            background: {theme['background']};
            border-radius: 5px;
        }}

        .custom-slider::handle:horizontal {{
            background: {theme['primary']};
            border: 1px solid {theme['primary']};
            width: 20px;
            margin: -5px 0;
            border-radius: 10px;
        }}

        .custom-slider::add-page:horizontal {{
            background: {theme['border']};
            border-radius: 5px;
        }}

        .custom-slider::sub-page:horizontal {{
            background: {theme['primary']};
            border-radius: 5px;
        }}
        """
