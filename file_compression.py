# ui.py
import sys
import os
from PyQt5.QtCore import QPropertyAnimation, Qt, QDir
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QTreeView, QFileSystemModel, QGraphicsOpacityEffect

from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.animation = QPropertyAnimation(self.graphicsEffect(), b"opacity")
        self.animation.setDuration(200)
        self.setStyleSheet("QPushButton { font-family: 'Fira Code'; font-size: 14px; color: #333; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 10px; }")

    def enterEvent(self, event):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.7)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(0.7)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().leaveEvent(event)

class CompressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Compression and Decompression Tool')
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.layout = QVBoxLayout()
        self.setFont(QFont('Fira Code'))

        # File selection layout
        self.file_select_layout = QHBoxLayout()
        self.file_label = QLabel('Selected File: None')
        self.file_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.select_file_btn = AnimatedButton('Select File')
        self.select_file_btn.clicked.connect(self.select_file)
        self.file_select_layout.addWidget(self.file_label)
        self.file_select_layout.addWidget(self.select_file_btn)

        # Algorithm selection layout
        self.algorithm_layout = QHBoxLayout()
        self.algorithm_label = QLabel('Algorithm:')
        self.algorithm_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 5px;")
        self.algorithm_combo.addItems(['deflate', 'huffman', 'lzw'])
        self.algorithm_layout.addWidget(self.algorithm_label)
        self.algorithm_layout.addWidget(self.algorithm_combo)

        # Mode selection layout
        self.mode_layout = QHBoxLayout()
        self.compress_btn = AnimatedButton('Compress')
        self.decompress_btn = AnimatedButton('Decompress')
        self.compress_btn.clicked.connect(lambda: self.process_file('compress'))
        self.decompress_btn.clicked.connect(lambda: self.process_file('decompress'))
        self.mode_layout.addWidget(self.compress_btn)
        self.mode_layout.addWidget(self.decompress_btn)

        # Adding layouts to the main layout
        self.layout.addLayout(self.file_select_layout)
        self.layout.addLayout(self.algorithm_layout)
        self.layout.addLayout(self.mode_layout)

        self.setLayout(self.layout)

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setDirectory(QDir.rootPath())
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            file = file_dialog.selectedFiles()[0]
            self.file_label.setText(f'Selected File: {os.path.basename(file)}')
            self.selected_file = file

    def process_file(self, mode):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, 'Error', 'Please select a file first.')
            return

        input_file = self.selected_file
        file_ext = '.bin' if mode == 'compress' else '.txt'
        output_file = QFileDialog.getSaveFileName(self, "Save File As", "", f"All Files (*{file_ext})")[0]

        if not output_file:
            return

        if not output_file.endswith(file_ext):
            output_file += file_ext

        algorithm = self.algorithm_combo.currentText()

        try:
            if algorithm == 'deflate':
                if mode == 'compress':
                    deflate_compress(input_file, output_file)
                else:
                    deflate_decompress(input_file, output_file)
            elif algorithm == 'huffman':
                huffman = HuffmanCoding(input_file)
                if mode == 'compress':
                    output_path = huffman.compress()
                    os.rename(output_path, output_file)
                    os.rename(output_path + '.tree', output_file + '.tree')
                else:
                    huffman.decompress(input_file)
                    os.rename('decompressed_file.txt', output_file)
            elif algorithm == 'lzw':
                if mode == 'compress':
                    lzw_compress(input_file, output_file)
                else:
                    lzw_decompress(input_file, output_file)

            QMessageBox.information(self, 'Success', f'File {mode}ed successfully and saved to {output_file}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icon/icon2.jpeg'))
    ex = CompressionApp()
    ex.show()
    sys.exit(app.exec_())
