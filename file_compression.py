import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox, QFileDialog, QMenu, QMenuBar)
from PyQt5.QtCore import Qt
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress_file, decompress_file as lzw_decompress_file
from deflate.deflate import compress_file as deflate_compress_file, decompress_file as deflate_decompress_file
from themes.themes import defaultStyle, darkStyle, lightStyle, retroStyle, draculaStyle, spaceStyle

class TextCompressionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Compression App')
        self.resize(600, 400)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.inputText = QTextEdit(self)
        self.inputText.setPlaceholderText("Enter or select text to compress...")
        self.layout.addWidget(self.inputText)

        self.algorithmSelector = QComboBox(self)
        self.algorithmSelector.addItem("Huffman")
        self.algorithmSelector.addItem("LZW")
        self.algorithmSelector.addItem("Deflate")
        self.layout.addWidget(self.algorithmSelector)

        self.buttonLayout = QHBoxLayout()
        self.layout.addLayout(self.buttonLayout)

        self.selectFileButton = QPushButton('Select File', self)
        self.selectFileButton.clicked.connect(self.selectFile)
        self.buttonLayout.addWidget(self.selectFileButton)

        self.compressButton = QPushButton('Compress', self)
        self.compressButton.clicked.connect(self.compressText)
        self.buttonLayout.addWidget(self.compressButton)

        self.decompressButton = QPushButton('Decompress', self)
        self.decompressButton.clicked.connect(self.decompressText)
        self.buttonLayout.addWidget(self.decompressButton)

        self.outputLabel = QLabel('Output:', self)
        self.layout.addWidget(self.outputLabel)

        self.outputText = QTextEdit(self)
        self.outputText.setReadOnly(True)
        self.outputText.setPlaceholderText("The result will be shown here...")
        self.layout.addWidget(self.outputText)

        self.createThemeButton()

        self.setStyleSheet(defaultStyle())
        print("UI initialized successfully.")

    def createThemeButton(self):
        self.themeButton = QPushButton('Themes', self)
        self.themeButton.setMenu(self.createThemeMenu())
        self.layout.addWidget(self.themeButton, alignment=Qt.AlignRight)

    def createThemeMenu(self):
        menu = QMenu(self)
        
        defaultThemeAction = menu.addAction("Default")
        defaultThemeAction.triggered.connect(self.setDefaultTheme)
        
        darkThemeAction = menu.addAction("Dark")
        darkThemeAction.triggered.connect(self.setDarkTheme)
        
        lightThemeAction = menu.addAction("Light")
        lightThemeAction.triggered.connect(self.setLightTheme)

        retroThemeAction = menu.addAction("Retro")
        retroThemeAction.triggered.connect(self.setRetroTheme)

        draculaThemeAction = menu.addAction("Dracula")
        draculaThemeAction.triggered.connect(self.setDraculaTheme)

        spaceThemeAction = menu.addAction("Space")
        spaceThemeAction.triggered.connect(self.setSpaceTheme)
        
        return menu

    def setDefaultTheme(self):
        self.setStyleSheet(defaultStyle())

    def setDarkTheme(self):
        self.setStyleSheet(darkStyle())

    def setLightTheme(self):
        self.setStyleSheet(lightStyle())

    def setRetroTheme(self):
        self.setStyleSheet(retroStyle())

    def setDraculaTheme(self):
        self.setStyleSheet(draculaStyle())

    def setSpaceTheme(self):
        self.setStyleSheet(spaceStyle())

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
            huffman.compress()
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
            huffman.decompress(input_path)
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

if __name__ == '__main__':
    def main():
        app = QApplication(sys.argv)
        ex = TextCompressionApp()
        ex.show()
        sys.exit(app.exec_())
    main()
