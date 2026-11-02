"""Стилі інтерфейсу MacNexus."""

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    color: #e6e6e6;
    font-family: -apple-system;
    font-size: 13px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    color: #222222;
    font-family: -apple-system;
    font-size: 13px;
}
"""

THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}
