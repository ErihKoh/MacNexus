"""Стилі інтерфейсу MacNexus."""

DARK_THEME = """
QMainWindow {
    background-color: #17191e;
}

QWidget {
    color: #e4e7ed;
    font-family: "Helvetica Neue";
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #20232a;
    border-right: 1px solid #30343d;
}

QLabel#logoLabel {
    color: #ffffff;
    font-size: 23px;
    font-weight: bold;
}

QLabel#subtitleLabel {
    color: #858c9a;
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 1px;
}

QLabel#pageTitle {
    color: #ffffff;
    font-size: 26px;
    font-weight: bold;
}

QLabel#pageDescription {
    color: #9299a7;
    font-size: 13px;
}

QPushButton#navButton {
    background-color: transparent;
    color: #aab1be;
    border: none;
    border-radius: 7px;
    padding: 9px;
    text-align: left;
}

QPushButton#navButton:hover {
    background-color: #2a2e37;
    color: #ffffff;
}

QPushButton#navButton:checked {
    background-color: #303c55;
    color: #8ab4f8;
    font-weight: bold;
}


QFrame#statusCard {
    background-color: #22262e;
    border: 1px solid #343945;
    border-radius: 10px;
}

QLabel#cardTitle {
    color: #aab1be;
    font-size: 13px;
}

QLabel#cardStatus {
    color: #e4e7ed;
    font-size: 17px;
    font-weight: bold;
}

QLabel#versionLabel {
    color: #737b89;
    font-size: 11px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f4f6f9;
}

QWidget {
    color: #252a34;
    font-family: "Helvetica Neue";
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e1e5eb;
}

QLabel#logoLabel {
    color: #202630;
    font-size: 23px;
    font-weight: bold;
}

QLabel#subtitleLabel {
    color: #89919f;
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 1px;
}

QLabel#pageTitle {
    color: #202630;
    font-size: 26px;
    font-weight: bold;
}

QLabel#pageDescription {
    color: #737d8d;
    font-size: 13px;
}

QPushButton#navButton {
    background-color: transparent;
    color: #737d8d;
    border: none;
    border-radius: 7px;
    padding: 9px;
    text-align: left;
}

QPushButton#navButton:hover {
    background-color: #f0f2f6;
    color: #252a34;
}

QPushButton#navButton:checked {
    background-color: #e9f0fc;
    color: #245db5;
    font-weight: bold;
}

QFrame#statusCard {
    background-color: #ffffff;
    border: 1px solid #e1e5eb;
    border-radius: 10px;
}

QLabel#cardTitle {
    color: #737d8d;
    font-size: 13px;
}

QLabel#cardStatus {
    color: #252a34;
    font-size: 17px;
    font-weight: bold;
}

QLabel#versionLabel {
    color: #929aa7;
    font-size: 11px;
}

"""

THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}
