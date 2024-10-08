import sys
import os
from PyQt5.QtCore import QPropertyAnimation, Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QComboBox, QMessageBox, QGraphicsOpacityEffect, QTabWidget, QLineEdit, QSpacerItem, QSizePolicy
)
import time
import pyflacaudio.Pyflac as pyflac
# Import your compression modules
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress
from burrowswheeler.burrowswheeler import compress as burrowswheeler_compress, decompress as burrowswheeler_decompress
from jpeg_2000.jpeg2000 import compress_image as jpeg2000_compress, decompress_image as jpeg2000_decompress


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.animation = QPropertyAnimation(self.graphicsEffect(), b"opacity")
        self.animation.setDuration(200)
        self.setStyleSheet(""" 
                QPushButton {
                    font-family: 'Poppins'; 
                    font-size: 14px; 
                    color: #fff; 
                    background-color: #6200ea; 
                    border: none; 
                    border-radius: 10px; 
                    padding: 10px; 
                }
                QPushButton:hover {
                    background-color: #3700b3;
                }
            """)


class CompressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Compression Tool')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f1f1f1;")

        self.layout = QVBoxLayout()
        self.setFont(QFont('Poppins'))

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_file_type_tab("Compression"), "Compression")
        self.tabs.addTab(self.create_file_type_tab("Decompression"), "Decompression")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def create_file_type_tab(self, mode):
        tab = QTabWidget()
        file_types = ["Image", "Text", "Audio", "Video"]

        # Define valid file extensions for each type
        valid_extensions = {
            "Text": ['.txt', '.doc', '.docx'],
            "Image": ['.png', '.jpg', '.jpeg', '.bmp', '.gif'],
            "Audio": ['.mp3', '.wav', '.aac'],
            "Video": ['.mp4', '.avi', '.mkv', '.mov']
        }

        for file_type in file_types:
            sub_tab = QWidget()
            sub_layout = QVBoxLayout()
            sub_layout.setSpacing(20)
            sub_layout.setContentsMargins(20, 20, 20, 20)

            # File selection
            input_file_edit = QLineEdit()
            input_file_edit.setPlaceholderText(f"Select {file_type} File")
            input_file_btn = AnimatedButton('...', self)
            input_file_btn.setFixedWidth(40)
            input_file_btn.clicked.connect(
                lambda _, edit=input_file_edit, f_type=file_type: self.select_file(edit, f_type, valid_extensions))

            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel(f"Select {file_type} File:"))
            input_layout.addWidget(input_file_edit)
            input_layout.addWidget(input_file_btn)
            sub_layout.addLayout(input_layout)

            # Output directory selection
            output_file_edit = QLineEdit()
            output_file_edit.setPlaceholderText(f"Select Output Directory")
            output_file_btn = AnimatedButton('...', self)
            output_file_btn.setFixedWidth(40)
            output_file_btn.clicked.connect(lambda _, edit=output_file_edit: self.select_directory(edit))

            output_layout = QHBoxLayout()
            output_layout.addWidget(QLabel('Select Output Directory:'))
            output_layout.addWidget(output_file_edit)
            output_layout.addWidget(output_file_btn)
            sub_layout.addLayout(output_layout)

            # Algorithm selection
            algorithm_layout = QHBoxLayout()
            algorithm_label = QLabel('Algorithm:')
            algorithm_combo = QComboBox()

            # Conditionally populate the algorithm combo box for all file types
            if file_type == "Text":
                algorithm_combo.addItems(['Deflate', 'Huffman', 'LZW', 'Burrows-Wheeler'])
            elif file_type == "Image":
                algorithm_combo.addItems(['JPEG2000', 'Deflate', 'Huffman', 'LZW'])  # Only JPEG2000 for images
            elif file_type == "Audio":
                algorithm_combo.addItems(['FLAC', 'Deflate', 'Huffman', 'LZW'])
            else:
                algorithm_combo.addItems(['Deflate', 'Huffman', 'LZW'])

            algorithm_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            algorithm_layout.addWidget(algorithm_label)
            algorithm_layout.addWidget(algorithm_combo)
            sub_layout.addLayout(algorithm_layout)

            # Processing button
            process_btn = AnimatedButton(mode, self)
            process_btn.clicked.connect(
                lambda _, m=mode, edit=input_file_edit, out_edit=output_file_edit,
                       alg_combo=algorithm_combo: self.process_file(m, edit.text(), out_edit.text(),
                                                                    alg_combo.currentText(), file_type)
            )
            sub_layout.addWidget(process_btn, alignment=Qt.AlignCenter)

            # Add a spacer to push content to the top
            sub_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            sub_tab.setLayout(sub_layout)
            tab.addTab(sub_tab, file_type)

        return tab

    def select_file(self, line_edit, file_type, valid_extensions):
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            if not any(file_path.lower().endswith(ext) for ext in valid_extensions[file_type]):
                QMessageBox.warning(self, 'Error',
                                    f'Invalid file type selected. Please select a valid {file_type} file.')
            else:
                line_edit.setText(file_path)

    def select_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self)
        if directory:
            line_edit.setText(directory)

    def process_file(self, mode, input_file, output_file, algorithm, file_type):
        if not input_file or not output_file:
            QMessageBox.warning(self, 'Error', 'Please select both input and output locations.')
            return

        try:
            original_size = os.path.getsize(input_file)

            if algorithm.lower() == 'deflate':
                if mode == 'Compression':
                    deflate_compress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'Deflate compression successful.')
                else:
                    deflate_decompress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'Deflate decompression successful.')
            elif algorithm.lower() == 'huffman':
                huffman = HuffmanCoding(input_file)
                if mode == 'Compression':
                    output_path = huffman.compress()
                    os.rename(output_path, output_file)
                    os.rename(output_path + '.tree', output_file + '.tree')
                    QMessageBox.information(self, 'Success', 'Huffman compression successful.')
                else:
                    huffman.decompress(input_file)
                    os.rename('decompressed_file.txt', output_file)
                    QMessageBox.information(self, 'Success', 'Huffman decompression successful.')
            elif algorithm.lower() == 'lzw':
                if mode == 'Compression':
                    lzw_compress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'LZW compression successful.')
                else:
                    lzw_decompress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'LZW decompression successful.')
            elif algorithm.lower() == 'burrows-wheeler' and file_type == "Text":
                if mode == 'Compression':
                    burrowswheeler_compress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'Burrows-Wheeler compression successful.')
                else:
                    burrowswheeler_decompress(input_file, output_file)
                    QMessageBox.information(self, 'Success', 'Burrows-Wheeler compression successful.')
            elif algorithm.lower() == 'jpeg2000' and mode == 'Compression':
                jpeg2000_compress(input_file, output_file)
                QMessageBox.information(self, 'Success', 'Image compression successful.')
            elif algorithm.lower() == 'jpeg2000' and mode == 'Decompression':
                jpeg2000_decompress(input_file, output_file)
                QMessageBox.information(self, 'Success', 'Image decompression successful.')
            elif algorithm.lower() == 'flac' and mode == 'Compression':
                pyflac.compress_audio(input_file, output_file)
                QMessageBox.information(self, 'Success', 'Audio compression (FLAC) successful.')
            elif algorithm.lower() == 'flac' and mode == 'Decompression':
                pyflac.decompress_audio(input_file, output_file)
                QMessageBox.information(self, 'Success', 'Audio decompression (FLAC) successful.')

            # Get the compressed size and display file sizes
            input_qlabel = QLabel(f"Input size is: {self.format_size(os.path.getsize(input_file))}")
            output_qlabel = QLabel(f"Output size is: {self.format_size(os.path.getsize(output_file))}")

            self.layout.addWidget(input_qlabel, alignment=Qt.AlignCenter)
            self.layout.addWidget(output_qlabel, alignment=Qt.AlignCenter)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def format_size(self, size_in_bytes):
        """Helper function to format file sizes in a readable format (KB, MB, GB)."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompressionApp()
    window.show()
    sys.exit(app.exec_())
