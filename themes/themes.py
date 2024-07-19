# themes.py
def apply_theme(app, theme):
    if theme == "Light":
        app.setStyleSheet(lightStyle())
    elif theme == "Dark":
        app.setStyleSheet(darkStyle())
    elif theme == "Retro":
        app.setStyleSheet(retroStyle())
    elif theme == "Space":
        app.setStyleSheet(spaceStyle())
    elif theme == "Dracula":
        app.setStyleSheet(draculaStyle())
    elif theme == "Horror":
        app.setStyleSheet(horrorStyle())
    elif theme == "Innovative":
        app.setStyleSheet(innovativeTheme())
    else:
        app.setStyleSheet(defaultStyle())


def defaultStyle():
    return """
        QWidget {
            background-color: #f0f0f0;
        }
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QComboBox {
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
        }
    """

def darkStyle():
    return """
        QWidget {
            background-color: #2d2d2d;
        }
        QTextEdit {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #4d4d4d;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #4d4d4d;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #5a5a5a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #787878;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        }
    """

def lightStyle():
    return """
        QWidget {
            background-color: #ffffff;
        }
        QTextEdit {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #e7e7e7;
            color: black;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #dcdcdc;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #000000;
        }
    """

def retroStyle():
    return """
        QWidget {
            background-color: #ffd700;
        }
        QTextEdit {
            background-color: #f5deb3;
            color: #000000;
            border: 2px solid #8b4513;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QComboBox {
            background-color: #f5deb3;
            color: #000000;
            border: 2px solid #8b4513;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QPushButton {
            background-color: #8b4513;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QPushButton:hover {
            background-color: #a0522d;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #000000;
            font-family: 'Courier New', Courier, monospace;
        }
    """

def spaceStyle():
    return """
        QWidget {
            background-color: #000000;
        }
        QTextEdit {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #2a2a2a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        }
    """

def draculaStyle():
    return """
        QWidget {
            background-color: #282a36;
        }
        QTextEdit {
            background-color: #44475a;
            color: #f8f8f2;
            border: 1px solid #6272a4;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #44475a;
            color: #f8f8f2;
            border: 1px solid #6272a4;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #50fa7b;
            color: #282a36;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #69ff94;
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #f8f8f2;
        }
    """

def horrorStyle():
    return """
        QWidget {
            background-color: #000000; /* Dark background */
        }
        QTextEdit {
            background-color: #2f2f2f; /* Dark gray */
            color: #ff0000; /* Red text */
            border: 2px solid #800000; /* Dark red */
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QComboBox {
            background-color: #2f2f2f; /* Dark gray */
            color: #ff0000; /* Red text */
            border: 2px solid #800000; /* Dark red */
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QPushButton {
            background-color: #800000; /* Dark red */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }
        QPushButton:hover {
            background-color: #a00000; /* Lighter red on hover */
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #ff0000; /* Red text */
            font-family: 'Courier New', Courier, monospace;
        }
    """

def innovativeTheme():
    return """
        QWidget {
            background-color: #1e1e2f; /* Deep navy blue */
        }
        QTextEdit {
            background-color: #2a2a3c; /* Dark slate gray */
            color: #f8f8f2; /* Light gray text */
            border: 2px solid #50fa7b; /* Neon green */
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-family: 'Fira Code', monospace; /* Modern monospaced font */
        }
        QComboBox {
            background-color: #2a2a3c; /* Dark slate gray */
            color: #f8f8f2; /* Light gray text */
            border: 2px solid #50fa7b; /* Neon green */
            border-radius: 8px;
            padding: 6px;
            font-size: 16px;
            font-family: 'Fira Code', monospace; /* Modern monospaced font */
        }
        QPushButton {
            background-color: #ff79c6; /* Bright pink */
            color: #ffffff; /* White text */
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            font-family: 'Fira Code', monospace; /* Modern monospaced font */
        }
        QPushButton:hover {
            background-color: #ff92d0; /* Lighter pink on hover */
        }
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #50fa7b; /* Neon green */
            font-family: 'Fira Code', monospace; /* Modern monospaced font */
        }
    """
