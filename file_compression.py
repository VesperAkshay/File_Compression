import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox, QFileDialog, QMenu, QMenuBar, QAction)
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress_file, decompress_file as lzw_decompress_file
from deflate.deflate import compress_file as deflate_compress_file, decompress_file as deflate_decompress_file
from themes.themes import apply_theme

class TextCompressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        print("Initializing UI...")
        self.setStyleSheet("""
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
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.menuBar = QMenuBar(self)
        self.themeMenu = QMenu("Themes", self)
        self.menuBar.addMenu(self.themeMenu)

        self.themes = ["Light", "Dark", "Retro", "Space", "Dracula", "Horror", "Innovative"]
        for theme in self.themes:
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(lambda checked, t=theme: self.applyTheme(t))
            self.themeMenu.addAction(theme_action)
        self.layout.addWidget(self.menuBar)

        self.inputText = QTextEdit(self)
        self.inputText.setPlaceholderText("Enter or select text to compress...")
        self.layout.addWidget(self.inputText)

        self.algorithmSelector = QComboBox(self)
        self.algorithmSelector.addItem("Huffman")
        self.algorithmSelector.addItem("LZW")
        self.algorithmSelector.addItem("Deflate")
        self.layout.addWidget(self.algorithmSelector)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)

        self.selectFileButton = QPushButton('Select File', self)
        self.selectFileButton.clicked.connect(self.selectFile)
        self.buttonLayout.addWidget(self.selectFileButton)

        self.compressButton = QPushButton('Compress', self)
        self.compressButton.clicked.connect(self.compressText)
        self.buttonLayout.addWidget(self.compressButton)

        self.decompressButton = QPushButton('Decompress', self)
        self.decompressButton.clicked.connect(self.decompressText)
        self.buttonLayout.addWidget(self.decompressButton)

        self.layout.addLayout(self.buttonLayout)

        self.outputLabel = QLabel('Output:', self)
        self.layout.addWidget(self.outputLabel)

        self.outputText = QTextEdit(self)
        self.outputText.setReadOnly(True)
        self.outputText.setPlaceholderText("The result will be shown here...")
        self.layout.addWidget(self.outputText)

        self.setLayout(self.layout)
        self.setWindowTitle('Text Compression App')
        self.resize(600, 400)

        print("UI initialized successfully.")

    def selectFile(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Select a Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filePath:
            print(f"File selected: {filePath}")
            with open(filePath, 'r') as file:
                self.inputText.setText(file.read())
            self.inputPath = filePath
        else:
            print("No file selected.")

    def getSaveFileName(self, defaultName):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", defaultName, "All Files (*)", options=options)
        if filePath:
            print(f"Save file path: {filePath}")
            return filePath
        print(f"Using default save file name: {defaultName}")
        return defaultName

    def compressText(self):
        algorithm = self.algorithmSelector.currentText()
        input_text = self.inputText.toPlainText()
        input_path = getattr(self, 'inputPath', 'input.txt')
        output_path = self.getSaveFileName('compressed_file.bin')

        if not hasattr(self, 'inputPath'):
            with open(input_path, 'w') as f:
                f.write(input_text)

        if algorithm == 'Huffman':
            print("Using Huffman algorithm.")
            huffman = HuffmanCoding(input_path)
            huffman.compress(output_path)
        elif algorithm == 'LZW':
            print("Using LZW algorithm.")
            lzw_compress_file(input_path, output_path)
        elif algorithm == 'Deflate':
            print("Using Deflate algorithm.")
            deflate_compress_file(input_path, output_path)

        with open(output_path, 'rb') as f:
            compressed_data = f.read()
        self.outputText.setText(compressed_data.hex())
        print("Text compressed successfully.")

    def decompressText(self):
        print("Decompressing text...")
        algorithm = self.algorithmSelector.currentText()
        input_text = self.inputText.toPlainText()
        input_path = self.getSaveFileName('compressed_file.bin')
        output_path = self.getSaveFileName('decompressed_file.txt')

        with open(input_path, 'wb') as f:
            f.write(bytes.fromhex(input_text))

        if algorithm == 'Huffman':
            print("Using Huffman algorithm.")
            huffman = HuffmanCoding(input_path)
            huffman.decompress(input_path, output_path)
        elif algorithm == 'LZW':
            print("Using LZW algorithm.")
            lzw_decompress_file(input_path, output_path)
        elif algorithm == 'Deflate':
            print("Using Deflate algorithm.")
            deflate_decompress_file(input_path, output_path)

        with open(output_path, 'r') as f:
            decompressed_data = f.read()
        self.outputText.setText(decompressed_data)
        print("Text decompressed successfully.")

    def applyTheme(self, theme):
        apply_theme(self, theme)

if __name__ == '__main__':
    def main():
        app = QApplication(sys.argv)
        ex = TextCompressionApp()
        ex.show()
        sys.exit(app.exec_())
    main()
