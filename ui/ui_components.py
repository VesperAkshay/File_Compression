import sys
import os
import mimetypes
from PyQt5.QtCore import QPropertyAnimation, Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QGraphicsOpacityEffect, QProgressBar, QCheckBox

# Import compression modules - these will be used by the compression handler
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress
from burrowswheeler.burrowswheeler import compress as bw_compress, decompress as bw_decompress

# Import the compression handler
from compression.compression_handler import CompressionHandler

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.animation = QPropertyAnimation(self.graphicsEffect(), b"opacity")
        self.animation.setDuration(200)
        self.setStyleSheet("""
            QPushButton {
                font-family: 'Fira Code';
                font-size: 14px;
                color: #ffffff;
                background-color: #007ACC;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005FA3;
            }
        """)

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
    def __init__(self, compression_handler=None):
        super().__init__()
        self.compression_handler = compression_handler
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Compression and Decompression Tool')
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.layout = QVBoxLayout()
        self.setFont(QFont('Fira Code'))

        # Dark mode toggle with checkbox
        self.dark_mode_toggle = QCheckBox('Enable Dark Mode')
        self.dark_mode_toggle.setStyleSheet("color: #333;")
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        self.layout.addWidget(self.dark_mode_toggle)
        
        # Category selection layout
        self.category_layout = QHBoxLayout()
        self.category_label = QLabel('File Category:')
        self.category_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                font-family: 'Fira Code';
                font-size: 14px;
                color: #333;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                border: 1px solid #007ACC;
            }
        """)
        self.category_combo.addItems(['All', 'Text', 'Image', 'Audio', 'Video'])
        self.category_combo.currentTextChanged.connect(self.category_changed)
        
        self.category_layout.addWidget(self.category_label)
        self.category_layout.addWidget(self.category_combo)

        # File selection layout
        # File selection layout
        self.file_select_layout = QHBoxLayout()
        self.file_icon_label = QLabel()
        self.file_label = QLabel('Selected File: None')
        self.file_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.file_type_label = QLabel('File Type: None')
        self.file_type_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.select_file_btn = AnimatedButton('Select File')
        self.select_file_btn.clicked.connect(self.select_file)
        self.file_select_layout.addWidget(self.file_icon_label)
        self.file_select_layout.addWidget(self.file_label)
        self.file_select_layout.addWidget(self.file_type_label)
        self.file_select_layout.addWidget(self.select_file_btn)
        
        # File info layout
        self.file_info_layout = QHBoxLayout()
        self.file_size_label = QLabel('Size: N/A')
        self.file_size_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.file_info_layout.addWidget(self.file_size_label)
        # Algorithm selection layout
        self.algorithm_layout = QHBoxLayout()
        self.algorithm_label = QLabel('Algorithm:')
        self.algorithm_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setStyleSheet("""
            QComboBox {
                font-family: 'Fira Code';
                font-size: 14px;
                color: #333;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                border: 1px solid #007ACC;
            }
        """)
        self.algorithm_combo.addItems(['deflate', 'huffman', 'lzw', 'burrowswheeler'])
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

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #e0e0e0;
                border-radius: 5px;
                height: 20px;
                text-align: center;  
                color: #000;  
            }
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 5px;
            }
            QProgressBar::text {
                color: #000; 
            }
        """)

        # Adding layouts to the main layout
        # Adding layouts to the main layout
        self.layout.addLayout(self.category_layout)
        self.layout.addLayout(self.file_select_layout)
        self.layout.addLayout(self.file_info_layout)
        self.layout.addLayout(self.algorithm_layout)
        self.layout.addLayout(self.mode_layout)
        self.layout.addWidget(self.progress_bar)  # Add progress bar to the main layout
        self.setLayout(self.layout)
    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setDirectory(os.getcwd())  # Set the default directory to the current working directory
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            file = file_dialog.selectedFiles()[0]
            self.file_label.setText(f'Selected File: {os.path.basename(file)}')
            self.selected_file = file
            
            # Update file size information
            file_size = os.path.getsize(file)
            size_display = self.format_file_size(file_size)
            self.file_size_label.setText(f'Size: {size_display}')
            
            # Update the available algorithms based on file type
            if self.compression_handler:
                file_type = self.compression_handler.detect_file_type(file)
                self.update_algorithms_for_file_type(file_type)
                
                # Show file type label
                file_type_display = file_type.capitalize()
                self.file_type_label.setText(f'File Type: {file_type_display}')
                
                # Update file icon (placeholder for now)
                # You could add actual icons in a future update
                # icon_path = f"./icons/{file_type}.png"
                # if os.path.exists(icon_path):
                #     self.file_icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
                
            # Reset category to "All" when a new file is selected
            self.category_combo.setCurrentText("All")
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        
    def update_algorithms_for_file_type(self, file_type):
        """Update the algorithm dropdown based on file type"""
        if self.compression_handler:
            # Clear the current items
            self.algorithm_combo.clear()
            
            # Get algorithms for this file type
            algorithms = self.compression_handler.get_available_algorithms(file_type)
            
            # Add the algorithms to the combo box
            self.algorithm_combo.addItems(algorithms)
    
    def category_changed(self, category):
        """Handle category selection change"""
        if not self.compression_handler:
            return
            
        if category == 'All':
            # Show all algorithms
            self.algorithm_combo.clear()
            all_algorithms = self.compression_handler.get_available_algorithms()
            self.algorithm_combo.addItems(all_algorithms)
        else:
            # Show algorithms for this category
            file_type = category.lower()
            self.update_algorithms_for_file_type(file_type)

    def toggle_dark_mode(self, state):
        if state == Qt.Checked:
            self.setStyleSheet("""
                QWidget { background-color: #1E1E1E; color: #D4D4D4; }
                QLabel { color: #D4D4D4; }
                QProgressBar { background-color: #3C3C3C; border-radius: 5px; text-align: center; }
                QProgressBar::chunk { background-color: #007ACC; border-radius: 5px; }
                QPushButton { background-color: #007ACC; color: #fff; border: none; padding: 10px; }
                QPushButton:hover { background-color: #005FA3; }
                QComboBox { background-color: #3C3C3C; color: #D4D4D4; border: 1px solid #007ACC; padding: 5px; }
            """)
            self.file_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #D4D4D4;")
            self.file_type_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #D4D4D4;")
            self.algorithm_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #D4D4D4;")
            self.dark_mode_toggle.setStyleSheet("QCheckBox { color: #FFFFFF; } QCheckBox::indicator { background-color: #3C3C3C; border: 1px solid #007ACC; }")
            self.category_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #D4D4D4;")
            self.file_size_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #D4D4D4;")
            self.progress_bar.setStyleSheet("""
                QProgressBar { background-color: #3C3C3C; border-radius: 5px; text-align: center; }
                QProgressBar::chunk { background-color: #007ACC; border-radius: 5px; }
                QProgressBar::text { color: #FFFFFF; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background-color: #F5F5F5; color: #333; }
                QLabel { color: #333; }
                QProgressBar { background-color: #e0e0e0; border-radius: 5px; text-align: center; }
                QProgressBar::chunk { background-color: #007ACC; border-radius: 5px; }
                QPushButton { background-color: #007ACC; color: #fff; border: none; padding: 10px; }
                QPushButton:hover { background-color: #005FA3; }
                QComboBox { background-color: #fff; color: #333; border: 1px solid #ddd; padding: 5px; }
            """)
            self.file_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
            self.file_type_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
            self.algorithm_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
            self.dark_mode_toggle.setStyleSheet("QCheckBox { color: #333333; } QCheckBox::indicator { background-color: #FFFFFF; border: 1px solid #333333; }")
            self.category_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
            self.file_size_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
            self.progress_bar.setStyleSheet("""
                QProgressBar { background-color: #e0e0e0; border-radius: 5px; text-align: center; }
                QProgressBar::chunk { background-color: #007ACC; border-radius: 5px; }
                QProgressBar::text { color: #000000; }
            """)

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
        self.progress_bar.setValue(0)  # Reset progress bar

        try:
            if self.compression_handler:
                # Use the compression handler if it's available
                self.compression_handler.process(algorithm, mode, input_file, output_file)
            else:
                # Fall back to direct module calls if no handler is provided
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
                    else:
                        huffman.decompress(input_file)
                        os.rename('decompressed_file.txt', output_file)
                
                elif algorithm == 'lzw':
                    if mode == 'compress':
                        lzw_compress(input_file, output_file)
                    else:
                        lzw_decompress(input_file, output_file)
                
                elif algorithm == 'burrowswheeler':
                    if mode == 'compress':
                        bw_compress(input_file, output_file)
                    else:
                        bw_decompress(input_file, output_file)

            self.progress_bar.setValue(100)  # Set progress to 100% after processing
            QMessageBox.information(self, 'Success', f'File {mode}ed successfully and saved to {output_file}')
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            self.progress_bar.setValue(0)  # Reset progress bar on error

