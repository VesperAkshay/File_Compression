import os
import sys

from PyQt5.QtCore import QPropertyAnimation, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Import your compression modules
from deflate.deflate import (
    compress_file as deflate_compress,
    decompress_file as deflate_decompress,
)
from huffman.huffman import HuffmanCoding
from lzw.lzw import (
    compress_file as lzw_compress,
    decompress_file as lzw_decompress,
)


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.animation = QPropertyAnimation(self.graphicsEffect(), b"opacity")
        self.animation.setDuration(200)
        self.setStyleSheet(
            """
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
        """
        )

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
        self.setWindowTitle("File Compression Tool")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f1f1f1;")

        self.layout = QVBoxLayout()
        self.setFont(QFont("Poppins"))

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(
            self.create_file_type_tab("Compression"), "Compression"
        )
        self.tabs.addTab(
            self.create_file_type_tab("Decompression"), "Decompression"
        )

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def create_file_type_tab(self, mode):
        tab = QTabWidget()
        file_types = ["Image", "Text", "Audio", "Video"]

        for file_type in file_types:
            sub_tab = QWidget()
            sub_layout = QVBoxLayout()
            sub_layout.setSpacing(20)  # Add spacing between widgets
            sub_layout.setContentsMargins(
                20, 20, 20, 20
            )  # Add margin around the tab

            # Button with icon and text

            # File selection
            input_file_edit = QLineEdit()
            input_file_edit.setPlaceholderText(f"Select {file_type} File")
            input_file_btn = AnimatedButton("...", self)
            input_file_btn.setFixedWidth(40)
            input_file_btn.clicked.connect(
                lambda _, edit=input_file_edit: self.select_file(edit)
            )

            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel(f"Select {file_type} File:"))
            input_layout.addWidget(input_file_edit)
            input_layout.addWidget(input_file_btn)
            sub_layout.addLayout(input_layout)

            # Output directory selection
            output_file_edit = QLineEdit()
            output_file_edit.setPlaceholderText(f"Select Output Directory")
            output_file_btn = AnimatedButton("...", self)
            output_file_btn.setFixedWidth(40)
            output_file_btn.clicked.connect(
                lambda _, edit=output_file_edit: self.select_directory(edit)
            )

            output_layout = QHBoxLayout()
            output_layout.addWidget(QLabel("Select Output Directory:"))
            output_layout.addWidget(output_file_edit)
            output_layout.addWidget(output_file_btn)
            sub_layout.addLayout(output_layout)

            # Algorithm selection
            # Algorithm selection
            algorithm_layout = QHBoxLayout()
            algorithm_label = QLabel("Algorithm:")
            algorithm_combo = QComboBox()
            algorithm_combo.addItems(["Deflate", "Huffman", "LZW"])

            # Set the size policy of the combo box to match the text box
            algorithm_combo.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Fixed
            )

            algorithm_layout.addWidget(algorithm_label)
            algorithm_layout.addWidget(algorithm_combo)
            sub_layout.addLayout(algorithm_layout)

            # Processing button
            process_btn = AnimatedButton(mode, self)
            process_btn.clicked.connect(
                lambda _, m=mode, edit=input_file_edit, out_edit=output_file_edit, alg_combo=algorithm_combo: self.process_file(
                    m, edit.text(), out_edit.text(), alg_combo.currentText()
                )
            )
            sub_layout.addWidget(process_btn, alignment=Qt.AlignCenter)

            # Add a spacer to push content to the top
            sub_layout.addSpacerItem(
                QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            )

            sub_tab.setLayout(sub_layout)
            tab.addTab(sub_tab, file_type)

        return tab

    def select_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            line_edit.setText(file_path)

    def select_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self)
        if directory:
            line_edit.setText(directory)

    def process_file(self, mode, input_file, output_file, algorithm):
        if not input_file or not output_file:
            QMessageBox.warning(
                self, "Error", "Please select both input and output locations."
            )
            return

        algorithm = algorithm.lower()

        try:
            if algorithm == "deflate":
                if mode == "Compression":
                    deflate_compress(input_file, output_file)
                else:
                    deflate_decompress(input_file, output_file)
            elif algorithm == "huffman":
                huffman = HuffmanCoding(input_file)
                if mode == "Compression":
                    output_path = huffman.compress()
                    os.rename(output_path, output_file)
                    os.rename(output_path + ".tree", output_file + ".tree")
                else:
                    huffman.decompress(input_file)
                    os.rename("decompressed_file.txt", output_file)
            elif algorithm == "lzw":
                if mode == "Compression":
                    lzw_compress(input_file, output_file)
                else:
                    lzw_decompress(input_file, output_file)

            QMessageBox.information(
                self,
                "Success",
                f"File {mode.lower()}ed successfully and saved to {output_file}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./icon/icon2.jpeg"))
    ex = CompressionApp()
    ex.show()
    sys.exit(app.exec_())
