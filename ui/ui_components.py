import sys
import os
import mimetypes
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Import PyQt5 modules
from PyQt5.QtCore import QPropertyAnimation, Qt, QSize
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QComboBox, QMessageBox, QGraphicsOpacityEffect, 
    QProgressBar, QCheckBox, QLineEdit, QInputDialog, QGridLayout, QStyle
)

# Import compression modules - these will be used by the compression handler
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress
from burrowswheeler.burrowswheeler import compress as bw_compress, decompress as bw_decompress

# Import the compression handler
from compression.compression_handler import CompressionHandler

# Import the Dashboard class from dashboard.py
from ui.dashboard import Dashboard

class EncryptionHandler:
    """Class to handle file encryption and decryption using AES"""
    
    @staticmethod
    def derive_key(password, salt=None):
        """Derive a 256-bit key from the password"""
        if salt is None:
            salt = os.urandom(16)
        # Use PBKDF2 to derive a key from the password
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        return key, salt
    
    @staticmethod
    def encrypt_file(input_file, output_file, password):
        """Encrypt a file using AES-256"""
        # Read the input file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Derive a key from the password
        key, salt = EncryptionHandler.derive_key(password)
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Create an encryptor
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt the data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Write the salt, IV, and encrypted data to the output file
        with open(output_file, 'wb') as f:
            f.write(salt)
            f.write(iv)
            f.write(encrypted_data)
    
    @staticmethod
    def decrypt_file(input_file, output_file, password):
        """Decrypt a file using AES-256"""
        # Read the input file
        with open(input_file, 'rb') as f:
            salt = f.read(16)
            iv = f.read(16)
            encrypted_data = f.read()
        
        # Derive the key from the password and salt
        key, _ = EncryptionHandler.derive_key(password, salt)
        
        # Create a decryptor
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        # Write the decrypted data to the output file
        with open(output_file, 'wb') as f:
            f.write(data)

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
        self.file_history = []  # Initialize file history
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Compression Tool')
        self.setGeometry(100, 100, 1000, 600)
        self.setAcceptDrops(True)  # Enable drag and drop
        
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar
        self.setup_sidebar()
        
        # Create main content area
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        
        # Add the content container to the main layout
        self.main_layout.addWidget(self.content_container)
        
        # Setup the main content widgets
        self.setup_header()
        self.setup_drop_area()
        self.setup_file_info()
        self.setup_compression_options()
        self.setup_action_buttons()
        self.setup_progress_area()
        
        # Apply initial style
        self.apply_style()
        
    def setup_sidebar(self):
        # Create sidebar container
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        
        # Sidebar layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # App logo/title area
        logo_container = QWidget()
        logo_container.setObjectName("logo-container")
        logo_container.setFixedHeight(60)
        logo_layout = QHBoxLayout(logo_container)
        
        logo_icon = QLabel()
        # Try to load the app icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_icon.setPixmap(pixmap)
        else:
            # Use a standard icon as fallback
            style = self.style()
            icon = style.standardIcon(QStyle.SP_FileIcon)
            logo_icon.setPixmap(icon.pixmap(32, 32))
        
        app_title = QLabel("Compressor")
        app_title.setObjectName("app-title")
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(app_title)
        logo_layout.setAlignment(Qt.AlignLeft)
        
        sidebar_layout.addWidget(logo_container)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            {"name": "dashboard", "text": "Dashboard", "icon": QStyle.SP_FileDialogDetailedView},
            {"name": "compress", "text": "Compress", "icon": QStyle.SP_ArrowDown},
            {"name": "decompress", "text": "Decompress", "icon": QStyle.SP_ArrowUp},
            {"name": "history", "text": "History", "icon": QStyle.SP_BrowserReload},
            {"name": "settings", "text": "Settings", "icon": QStyle.SP_FileDialogInfoView}
        ]
        
        for item in nav_items:
            btn = QPushButton(item["text"])
            btn.setObjectName(f"nav-{item['name']}")
            
            # Use standard icon
            style = self.style()
            icon = style.standardIcon(item["icon"])
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, name=item["name"]: self.handle_nav_action(name))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[item["name"]] = btn
        
        # Add spacer to push theme toggle to bottom
        sidebar_layout.addStretch()
        
        # Theme toggle
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)
        
        theme_icon = QLabel()
        # Use standard icon
        style = self.style()
        icon = style.standardIcon(QStyle.SP_DesktopIcon)
        theme_icon.setPixmap(icon.pixmap(20, 20))
        
        self.theme_switch = QCheckBox("Dark Mode")
        self.theme_switch.stateChanged.connect(self.toggle_dark_mode)
        
        theme_layout.addWidget(theme_icon)
        theme_layout.addWidget(self.theme_switch)
        
        sidebar_layout.addWidget(theme_container)
        
        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar)
    
    def setup_header(self):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        self.page_title = QLabel("File Compression")
        self.page_title.setObjectName("page-title")
        
        # Add mode indicator
        self.mode_indicator = QLabel("")
        self.mode_indicator.setObjectName("mode-indicator")
        self.mode_indicator.setVisible(False)
        
        header_layout.addWidget(self.page_title)
        header_layout.addWidget(self.mode_indicator)
        header_layout.addStretch()
        
        self.content_layout.addWidget(header)
    
    def setup_drop_area(self):
        self.drop_area = QWidget()
        self.drop_area.setObjectName("drop-area")
        self.drop_area.setMinimumHeight(200)
        
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignCenter)
        
        # Icon for drop area
        drop_icon = QLabel()
        # Use standard icon
        style = self.style()
        icon = style.standardIcon(QStyle.SP_ArrowUp)
        drop_icon.setPixmap(icon.pixmap(64, 64))
        drop_icon.setAlignment(Qt.AlignCenter)
        
        drop_text = QLabel("Drag & Drop Files Here")
        drop_text.setObjectName("drop-text")
        drop_text.setAlignment(Qt.AlignCenter)
        
        drop_subtext = QLabel("or")
        drop_subtext.setAlignment(Qt.AlignCenter)
        
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setObjectName("browse-btn")
        self.browse_btn.clicked.connect(self.select_file)
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        
        drop_layout.addWidget(drop_icon)
        drop_layout.addWidget(drop_text)
        drop_layout.addWidget(drop_subtext)
        drop_layout.addWidget(self.browse_btn, 0, Qt.AlignCenter)
        
        self.content_layout.addWidget(self.drop_area)
    
    def setup_file_info(self):
        self.file_info = QWidget()
        self.file_info.setObjectName("file-info")
        self.file_info.setVisible(False)  # Hidden initially until file is selected
        
        file_info_layout = QVBoxLayout(self.file_info)
        
        # File details header
        file_header = QLabel("File Details")
        file_header.setObjectName("section-header")
        
        # File details grid
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        
        # File name
        details_grid.addWidget(QLabel("Name:"), 0, 0)
        self.file_name_label = QLabel("No file selected")
        details_grid.addWidget(self.file_name_label, 0, 1)
        
        # File type
        details_grid.addWidget(QLabel("Type:"), 1, 0)
        self.file_type_label = QLabel("N/A")
        details_grid.addWidget(self.file_type_label, 1, 1)
        
        # File size
        details_grid.addWidget(QLabel("Size:"), 2, 0)
        self.file_size_label = QLabel("N/A")
        details_grid.addWidget(self.file_size_label, 2, 1)
        
        file_info_layout.addWidget(file_header)
        file_info_layout.addLayout(details_grid)
        
        self.content_layout.addWidget(self.file_info)
    
    def setup_compression_options(self):
        self.options_widget = QWidget()
        self.options_widget.setObjectName("compression-options")
        self.options_widget.setVisible(False)  # Hidden initially until file is selected
        
        options_layout = QVBoxLayout(self.options_widget)
        
        # Options header
        options_header = QLabel("Compression Options")
        options_header.setObjectName("section-header")
        options_layout.addWidget(options_header)
        
        # Options grid
        options_grid = QGridLayout()
        options_grid.setColumnStretch(1, 1)
        
        # Algorithm selection
        options_grid.addWidget(QLabel("Algorithm:"), 0, 0)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setObjectName("algorithm-combo")
        self.algorithm_combo.addItems(['deflate', 'huffman', 'lzw', 'burrowswheeler'])
        options_grid.addWidget(self.algorithm_combo, 0, 1)
        
        # Category selection
        options_grid.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.setObjectName("category-combo")
        self.category_combo.addItems(['All', 'Text', 'Image', 'Audio', 'Video'])
        self.category_combo.currentTextChanged.connect(self.category_changed)
        options_grid.addWidget(self.category_combo, 1, 1)
        
        # Encryption option
        options_grid.addWidget(QLabel("Security:"), 2, 0)
        encryption_widget = QWidget()
        encryption_layout = QHBoxLayout(encryption_widget)
        encryption_layout.setContentsMargins(0, 0, 0, 0)
        
        self.encryption_checkbox = QCheckBox("Enable Encryption")
        self.encryption_checkbox.setObjectName("encryption-checkbox")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (if encryption enabled)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setEnabled(False)
        
        self.encryption_checkbox.stateChanged.connect(
            lambda state: self.password_input.setEnabled(state == Qt.Checked)
        )
        
        encryption_layout.addWidget(self.encryption_checkbox)
        encryption_layout.addWidget(self.password_input)
        
        options_grid.addWidget(encryption_widget, 2, 1)
        
        options_layout.addLayout(options_grid)
        
        self.content_layout.addWidget(self.options_widget)
    
    def setup_action_buttons(self):
        self.action_buttons = QWidget()
        self.action_buttons.setObjectName("action-buttons")
        self.action_buttons.setVisible(False)  # Hidden initially until file is selected
        
        action_layout = QVBoxLayout(self.action_buttons)
        
        # Add a label to clearly indicate what to do
        self.action_instruction = QLabel("Select an operation to perform:")
        self.action_instruction.setObjectName("action-instruction")
        action_layout.addWidget(self.action_instruction)
        
        # Button container for better styling
        button_container = QWidget()
        button_container.setObjectName("button-container")
        button_layout = QVBoxLayout(button_container)
        
        self.compress_btn = QPushButton("Compress")
        self.compress_btn.setObjectName("primary-btn")
        self.compress_btn.clicked.connect(lambda: self.process_file('compress'))
        self.compress_btn.setCursor(Qt.PointingHandCursor)
        self.compress_btn.setMinimumHeight(50)  # Make buttons larger
        
        self.decompress_btn = QPushButton("Decompress")
        self.decompress_btn.setObjectName("secondary-btn")
        self.decompress_btn.clicked.connect(lambda: self.process_file('decompress'))
        self.decompress_btn.setCursor(Qt.PointingHandCursor)
        self.decompress_btn.setMinimumHeight(50)  # Make buttons larger
        
        button_layout.addWidget(self.compress_btn)
        button_layout.addWidget(self.decompress_btn)
        
        action_layout.addWidget(button_container)
        
        self.content_layout.addWidget(self.action_buttons)
    
    def setup_progress_area(self):
        self.progress_widget = QWidget()
        self.progress_widget.setObjectName("progress-widget")
        self.progress_widget.setVisible(False)  # Hidden initially
        
        progress_layout = QVBoxLayout(self.progress_widget)
        
        self.operation_label = QLabel("Operation in progress...")
        self.operation_label.setObjectName("operation-label")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress-bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.result_label = QLabel()
        self.result_label.setObjectName("result-label")
        self.result_label.setVisible(False)
        
        progress_layout.addWidget(self.operation_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.result_label)
        
        self.content_layout.addWidget(self.progress_widget)
        self.content_layout.addStretch()
    
    def apply_style(self):
        # Light mode styles
        light_style = """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #333333;
                background-color: #ffffff;
            }
            
            #sidebar {
                background-color: #f5f5f5;
                border-right: 1px solid #e0e0e0;
            }
            
            #logo-container {
                background-color: #007bff;
                padding: 10px;
            }
            
            #app-title {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            
            QPushButton[objectName^="nav-"] {
                background-color: transparent;
                border: none;
                border-radius: 0;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
            }
            
            QPushButton[objectName^="nav-"]:hover {
                background-color: #e0e0e0;
            }
            
            QPushButton[objectName^="nav-"].active {
                background-color: #007bff;
                color: white;
            }
            
            #page-title {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
            
            #mode-indicator {
                font-size: 16px;
                font-weight: bold;
                color: #007bff;
                background-color: #e6f2ff;
                padding: 5px 10px;
                border-radius: 5px;
                margin-left: 10px;
            }
            
            #drop-area {
                background-color: #f9f9f9;
                border: 2px dashed #cccccc;
                border-radius: 10px;
            }
            
            #drop-area:hover {
                border-color: #007bff;
            }
            
            #drop-text {
                font-size: 18px;
                font-weight: bold;
                color: #555555;
            }
            
            #browse-btn {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            #browse-btn:hover {
                background-color: #0069d9;
            }
            
            #section-header {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-top: 10px;
            }
            
            #action-instruction {
                font-size: 16px;
                color: #555555;
                margin-bottom: 10px;
            }
            
            #button-container {
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
            }
            
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            
            QComboBox:hover {
                border-color: #007bff;
            }
            
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
            }
            
            #primary-btn {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            
            #primary-btn:hover {
                background-color: #0069d9;
            }
            
            #secondary-btn {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            
            #secondary-btn:hover {
                background-color: #5a6268;
            }
            
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 5px;
            }
        """
        
        # Dark mode styles
        dark_style = """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #f0f0f0;
                background-color: #1e1e1e;
            }
            
            #sidebar {
                background-color: #252526;
                border-right: 1px solid #333333;
            }
            
            #logo-container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #1565c0);
                padding: 10px;
                border-bottom: 1px solid #333333;
            }
            
            #app-title {
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            }
            
            QPushButton[objectName^="nav-"] {
                background-color: transparent;
                border: none;
                border-radius: 0;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                color: #cccccc;
                border-left: 3px solid transparent;
            }
            
            QPushButton[objectName^="nav-"]:hover {
                background-color: #2d2d30;
                border-left: 3px solid #2979ff;
                color: #ffffff;
            }
            
            QPushButton[objectName^="nav-"].active {
                background-color: #2979ff;
                color: white;
                border-left: 3px solid #ffffff;
            }
            
            #page-title {
                font-size: 24px;
                font-weight: bold;
                color: #f0f0f0;
                border-bottom: 1px solid #333333;
                padding-bottom: 5px;
            }
            
            #mode-indicator {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #1565c0);
                padding: 5px 10px;
                border-radius: 5px;
                margin-left: 10px;
            }
            
            #drop-area {
                background-color: #2d2d30;
                border: 2px dashed #555555;
                border-radius: 10px;
                box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
            }
            
            #drop-area:hover {
                border-color: #2979ff;
                background-color: #333337;
            }
            
            #drop-text {
                font-size: 18px;
                font-weight: bold;
                color: #f0f0f0;
            }
            
            #browse-btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2979ff, stop:1 #1565c0);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            #browse-btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e88e5, stop:1 #0d47a1);
            }
            
            #section-header {
                font-size: 18px;
                font-weight: bold;
                color: #f0f0f0;
                margin-top: 10px;
                border-bottom: 1px solid #333333;
                padding-bottom: 5px;
            }
            
            #action-instruction {
                font-size: 16px;
                color: #cccccc;
                margin-bottom: 10px;
            }
            
            #button-container {
                background-color: #2d2d30;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }
            
            QComboBox {
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
                background-color: #333337;
                color: #f0f0f0;
                selection-background-color: #2979ff;
            }
            
            QComboBox:hover {
                border-color: #2979ff;
                background-color: #3c3c41;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #444444;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #333337;
                border: 1px solid #444444;
                selection-background-color: #2979ff;
                selection-color: #ffffff;
            }
            
            QLineEdit {
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                background-color: #333337;
                color: #f0f0f0;
            }
            
            QLineEdit:focus {
                border-color: #2979ff;
                background-color: #3c3c41;
            }
            
            #primary-btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2979ff, stop:1 #1565c0);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            
            #primary-btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e88e5, stop:1 #0d47a1);
            }
            
            #secondary-btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop:1 #424242);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            
            #secondary-btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #757575, stop:1 #616161);
            }
            
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 5px;
                text-align: center;  
                height: 20px;
                background-color: #333337;
                color: #f0f0f0;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #1565c0);
                border-radius: 5px;
            }
            
            QCheckBox {
                color: #f0f0f0;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #444444;
                border-radius: 3px;
                background-color: #333337;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2979ff;
                image: url(check.png);
            }
            
            QCheckBox::indicator:hover {
                border-color: #2979ff;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #2d2d30;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #666666;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: #2d2d30;
                height: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: #555555;
                min-width: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #666666;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QToolTip {
                background-color: #2d2d30;
                color: #f0f0f0;
                border: 1px solid #444444;
                border-radius: 3px;
            }
        """
        
        self.light_style = light_style
        self.dark_style = dark_style
        
        # Apply initial style (light mode by default)
        self.setStyleSheet(light_style)
    
    def toggle_dark_mode(self, state):
        self.dark_mode = (state == Qt.Checked)
        if self.dark_mode:
            self.setStyleSheet(self.dark_style)
        else:
            self.setStyleSheet(self.light_style)
            
        # Update settings panel if it exists
        if hasattr(self, 'settings_widget') and self.settings_widget:
            self.settings_widget.updateStyle()
            
        # Add a smooth transition effect
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.animation = QPropertyAnimation(self.graphicsEffect(), b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.7)
        self.animation.setEndValue(1.0)
        self.animation.start()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("border-color: #007bff;")
    
    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("")
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("")
            
            # Get the first dropped file
            file_url = event.mimeData().urls()[0]
            file_path = file_url.toLocalFile()
            
            # Process the dropped file
            self.process_dropped_file(file_path)
    
    def process_dropped_file(self, file_path):
        if os.path.isfile(file_path):
            self.selected_file = file_path
            self.file_name_label.setText(os.path.basename(file_path))
            
            # Update file type
            file_type = self.compression_handler.detect_file_type(file_path) if self.compression_handler else "Unknown"
            self.file_type_label.setText(file_type)
            
            # Update file size
            file_size = os.path.getsize(file_path)
            size_display = self.format_file_size(file_size)
            self.file_size_label.setText(size_display)
            
            # Update algorithms based on file type
            self.update_algorithms_for_file_type(file_type)
            
            # Show file info and options
            self.file_info.setVisible(True)
            self.options_widget.setVisible(True)
            self.action_buttons.setVisible(True)
            
            # Check which mode is active (compress or decompress)
            # and show only the relevant button
            for btn_name, btn in self.nav_buttons.items():
                if btn.property("class") == "active":
                    active_mode = btn_name
                    break
            else:
                active_mode = "dashboard"  # Default to dashboard if no button is active
            
            # Set the appropriate button styling and visibility based on active mode
            if active_mode == "compress":
                self.compress_btn.setVisible(True)
                self.decompress_btn.setVisible(False)
                self.compress_btn.setObjectName("primary-btn")
                self.mode_indicator.setText("COMPRESS MODE")
                self.action_instruction.setText("Click to compress the selected file:")
            elif active_mode == "decompress":
                self.compress_btn.setVisible(False)
                self.decompress_btn.setVisible(True)
                self.decompress_btn.setObjectName("primary-btn")
                self.mode_indicator.setText("DECOMPRESS MODE")
                self.action_instruction.setText("Click to decompress the selected file:")
            else:
                # In dashboard mode, show both buttons
                self.compress_btn.setVisible(True)
                self.decompress_btn.setVisible(True)
                self.compress_btn.setObjectName("primary-btn")
                self.decompress_btn.setObjectName("secondary-btn")
                self.action_instruction.setText("Select an operation to perform:")
            
            # Apply the styling
            self.compress_btn.style().unpolish(self.compress_btn)
            self.compress_btn.style().polish(self.compress_btn)
            self.decompress_btn.style().unpolish(self.decompress_btn)
            self.decompress_btn.style().polish(self.decompress_btn)
            
            # Show the mode indicator
            self.mode_indicator.setVisible(True)
            
            # Add to history
            self.add_to_history(file_path, "Selected")
    
    def select_file(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.Detail)
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            self.process_dropped_file(file_path)
    
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

    def add_to_history(self, file_path, operation):
        """Add a file operation to the history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file_history.append({
            'file': file_path, 
            'operation': operation,
            'timestamp': timestamp
        })

    def show_file_history(self):
        """Display the file history in a dedicated widget"""
        # Create a history widget if it doesn't exist
        if not hasattr(self, 'history_widget'):
            self.history_widget = QWidget()
            self.history_widget.setObjectName("history-widget")
            history_layout = QVBoxLayout(self.history_widget)
            
            # History header
            history_header = QLabel("File History")
            history_header.setObjectName("page-title")
            
            # History list container
            self.history_list_container = QWidget()
            self.history_list_layout = QVBoxLayout(self.history_list_container)
            
            # Add to layout
            history_layout.addWidget(history_header)
            history_layout.addWidget(self.history_list_container)
            
            # Add to main content
            self.content_layout.addWidget(self.history_widget)
            self.history_widget.setVisible(False)
        
        # Clear previous history items
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Hide all other content widgets
        self.drop_area.setVisible(False)
        self.file_info.setVisible(False)
        self.options_widget.setVisible(False)
        self.action_buttons.setVisible(False)
        self.progress_widget.setVisible(False)
        
        # Show history widget
        self.history_widget.setVisible(True)
        
        # Display history or a message if empty
        if not self.file_history:
            empty_label = QLabel("No file history available.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.history_list_layout.addWidget(empty_label)
        else:
            # Add history items
            for entry in self.file_history:
                history_item = QWidget()
                history_item.setObjectName("history-item")
                history_item.setStyleSheet("""
                    #history-item {
                        background-color: #f9f9f9;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 10px;
                    }
                    #history-item:hover {
                        background-color: #f0f0f0;
                    }
                """)
                
                item_layout = QHBoxLayout(history_item)
                
                # Operation icon
                icon_label = QLabel()
                style = self.style()
                
                # Choose appropriate icon based on operation
                if entry['operation'].lower() == "compressed":
                    icon = style.standardIcon(QStyle.SP_ArrowDown)
                elif entry['operation'].lower() == "decompressed":
                    icon = style.standardIcon(QStyle.SP_ArrowUp)
                elif entry['operation'].lower() == "selected":
                    icon = style.standardIcon(QStyle.SP_FileIcon)
                else:
                    icon = style.standardIcon(QStyle.SP_FileIcon)
                
                icon_label.setPixmap(icon.pixmap(24, 24))
                
                # File info
                info_widget = QWidget()
                info_layout = QVBoxLayout(info_widget)
                info_layout.setContentsMargins(0, 0, 0, 0)
                
                operation_label = QLabel(f"{entry['operation'].capitalize()}")
                operation_label.setStyleSheet("font-weight: bold;")
                
                file_label = QLabel(os.path.basename(entry['file']))
                
                timestamp_label = QLabel(entry['timestamp'])
                timestamp_label.setStyleSheet("color: #888; font-size: 12px;")
                
                info_layout.addWidget(operation_label)
                info_layout.addWidget(file_label)
                info_layout.addWidget(timestamp_label)
                
                # Add to item layout
                item_layout.addWidget(icon_label)
                item_layout.addWidget(info_widget, 1)
                
                self.history_list_layout.addWidget(history_item)

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

        # Check if encryption is enabled
        use_encryption = self.encryption_checkbox.isChecked()
        password = None
        
        if use_encryption:
            # Get password from the password input field
            password = self.password_input.text()
            if not password:
                QMessageBox.warning(self, 'Error', 'Password is required for encryption.')
                return

        algorithm = self.algorithm_combo.currentText()
        
        # Show progress widget
        self.drop_area.setVisible(False)
        self.file_info.setVisible(False)
        self.options_widget.setVisible(False)
        self.action_buttons.setVisible(False)
        self.progress_widget.setVisible(True)
        
        # Set operation label
        operation_text = "Compressing" if mode == "compress" else "Decompressing"
        self.operation_label.setText(f"{operation_text} file: {os.path.basename(input_file)}")
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.result_label.setVisible(False)

        # Disable buttons during processing
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)

        try:
            if self.compression_handler:
                try:
                    # Disconnect any existing connections to avoid multiple connections
                    self.compression_handler.progress_updated.disconnect()
                    self.compression_handler.operation_completed.disconnect()
                    self.compression_handler.operation_failed.disconnect()
                except:
                    # It's okay if they weren't connected
                    pass
                
                # Connect to the signals with correct names
                self.compression_handler.progress_updated.connect(self.update_progress)
                self.compression_handler.operation_completed.connect(self.handle_operation_completed)
                self.compression_handler.operation_failed.connect(self.handle_operation_failed)
                
                # Use the compression handler with threading and encryption if enabled
                self.compression_handler.process(algorithm, mode, input_file, output_file, 
                                               use_threading=True, 
                                               use_encryption=use_encryption, 
                                               password=password)
            else:
                # Fall back to direct module calls if no handler is provided
                # Note: This path doesn't support encryption
                if use_encryption:
                    QMessageBox.warning(self, 'Warning', 'Encryption is only supported when using the compression handler.')
                
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
                self.add_to_history(input_file, mode)  # Add to history
        
        except Exception as e:
            self.handle_operation_failed(str(e))

    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)

    def handle_operation_completed(self, result):
        """Handle successful completion of compression/decompression"""
        self.progress_bar.setValue(100)  # Set progress to 100% after processing
        
        # Re-enable buttons
        self.compress_btn.setEnabled(True)
        self.decompress_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        
        # Build result message
        message = 'Operation completed successfully!'
        
        if 'original_size' in result and 'compressed_size' in result:
            # This is a compression result
            message += f'\nOriginal size: {self.format_file_size(result["original_size"])}'
            message += f'\nCompressed size: {self.format_file_size(result["compressed_size"])}'
            if 'ratio' in result:
                message += f'\nCompression ratio: {result["ratio"]:.2f}%'
                
            # Add to history
            if 'output_file' in result:
                self.add_to_history(result['output_file'], 'Compressed')
                
        elif 'compressed_size' in result and 'decompressed_size' in result:
            # This is a decompression result
            message += f'\nCompressed size: {self.format_file_size(result["compressed_size"])}'
            message += f'\nDecompressed size: {self.format_file_size(result["decompressed_size"])}'
            
            # Add to history
            if 'output_file' in result:
                self.add_to_history(result['output_file'], 'Decompressed')
        
        if 'time' in result:
            message += f'\nTime taken: {result["time"]:.2f} seconds'
        
        # Update result label
        self.result_label.setText(message)
        self.result_label.setStyleSheet("color: #28a745; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        self.result_label.setVisible(True)

    def handle_operation_failed(self, error_message):
        """Handle operation failure"""
        self.progress_bar.setValue(0)  # Reset progress bar
        
        # Re-enable buttons
        self.compress_btn.setEnabled(True)
        self.decompress_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        
        # Update result label
        self.result_label.setText(f"Error: {error_message}")
        self.result_label.setStyleSheet("color: #dc3545; padding: 10px; background-color: #f8d7da; border-radius: 5px;")
        self.result_label.setVisible(True)

    def handle_nav_action(self, action_name):
        # Reset all navigation button styles
        for btn_name, btn in self.nav_buttons.items():
            btn.setProperty("class", "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Set active button style
        if action_name in self.nav_buttons:
            self.nav_buttons[action_name].setProperty("class", "active")
            self.nav_buttons[action_name].style().unpolish(self.nav_buttons[action_name])
            self.nav_buttons[action_name].style().polish(self.nav_buttons[action_name])
        
        # Hide all content widgets first
        self.drop_area.setVisible(False)
        self.file_info.setVisible(False)
        self.options_widget.setVisible(False)
        self.action_buttons.setVisible(False)
        self.progress_widget.setVisible(False)
        
        # Hide dashboard if it exists
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.setVisible(False)
            
        if hasattr(self, 'history_widget'):
            self.history_widget.setVisible(False)
        
        # Reset mode indicator
        self.mode_indicator.setVisible(False)
        
        # Show appropriate content based on action
        if action_name == "dashboard":
            # Show dashboard view
            self.page_title.setText("Dashboard")
            
            # Create dashboard widget if it doesn't exist
            if not hasattr(self, 'dashboard_widget'):
                from ui.dashboard import Dashboard
                self.dashboard_widget = Dashboard(self)
                self.content_layout.addWidget(self.dashboard_widget)
            
            # Show dashboard
            self.dashboard_widget.setVisible(True)
            
            # Refresh dashboard data
            if hasattr(self.dashboard_widget, 'load_dashboard_data'):
                self.dashboard_widget.load_dashboard_data()
            
        elif action_name == "compress":
            # Show compression view
            self.page_title.setText("File Compression")
            self.mode_indicator.setText("COMPRESS MODE")
            self.mode_indicator.setVisible(True)
            self.drop_area.setVisible(True)
            
            # Show only compress button in compress mode
            self.compress_btn.setVisible(True)
            self.decompress_btn.setVisible(False)
            
            # Update instruction
            self.action_instruction.setText("Click to compress the selected file:")
            
            # If a file is already selected, show the file info and options
            if hasattr(self, 'selected_file'):
                self.file_info.setVisible(True)
                self.options_widget.setVisible(True)
                self.action_buttons.setVisible(True)
                
                # Highlight the compress button
                self.compress_btn.setObjectName("primary-btn")
                self.compress_btn.style().unpolish(self.compress_btn)
                self.compress_btn.style().polish(self.compress_btn)
                
        elif action_name == "decompress":
            # Show decompression view
            self.page_title.setText("File Decompression")
            self.mode_indicator.setText("DECOMPRESS MODE")
            self.mode_indicator.setVisible(True)
            self.drop_area.setVisible(True)
            
            # Show only decompress button in decompress mode
            self.compress_btn.setVisible(False)
            self.decompress_btn.setVisible(True)
            
            # Update instruction
            self.action_instruction.setText("Click to decompress the selected file:")
            
            # If a file is already selected, show the file info and options
            if hasattr(self, 'selected_file'):
                self.file_info.setVisible(True)
                self.options_widget.setVisible(True)
                self.action_buttons.setVisible(True)
                
                # Highlight the decompress button
                self.decompress_btn.setObjectName("primary-btn")
                self.decompress_btn.style().unpolish(self.decompress_btn)
                self.decompress_btn.style().polish(self.decompress_btn)
                
        elif action_name == "history":
            # Show history view
            self.page_title.setText("File History")
            self.show_file_history()
            
        elif action_name == "settings":
            # Show settings view
            self.page_title.setText("Settings")
            
            # Create settings widget if it doesn't exist
            if not hasattr(self, 'settings_widget'):
                from ui.settings import Settings
                self.settings_widget = Settings(self)
                self.content_layout.addWidget(self.settings_widget)
            
            # Show settings
            self.settings_widget.setVisible(True)
            
            # Hide other widgets
            if hasattr(self, 'dashboard_widget'):
                self.dashboard_widget.setVisible(False)
            if hasattr(self, 'history_widget'):
                self.history_widget.setVisible(False)

