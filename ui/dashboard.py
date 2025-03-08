from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout, QSpacerItem, QSizePolicy, QStyle, QMessageBox, QFileDialog,
    QApplication
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QFont
import os
import datetime

# Import the CompressionApp class
try:
    from ui.ui_components import CompressionApp
except ImportError:
    print("Dashboard: Could not import CompressionApp")
    CompressionApp = None

class StatCard(QFrame):
    def __init__(self, title, value, icon_name=None, parent=None):
        super().__init__(parent)
        self.setObjectName("stat-card")
        self.setFixedHeight(120)
        self.setMinimumWidth(200)
        
        # Apply card styling
        self.setStyleSheet("""
            #stat-card {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                font-family: 'Fira Code', sans-serif;
            }
        """)
        
        # Card layout
        layout = QVBoxLayout(self)
        
        # Card header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon (if provided)
        if icon_name:
            icon_label = QLabel()
            style = self.style()
            icon = style.standardIcon(getattr(style, icon_name))
            icon_label.setPixmap(icon.pixmap(24, 24))
            header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; padding-top: 10px;")
        self.value_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
    def update_value(self, new_value):
        """Update the card's value"""
        self.value_label.setText(str(new_value))

class RecentFileItem(QFrame):
    def __init__(self, file_name, file_path, operation, date, parent=None, on_click=None):
        super().__init__(parent)
        self.setObjectName("recent-file-item")
        self.setFixedHeight(70)
        self.file_path = file_path + file_name if file_path else file_name
        self.on_click = on_click
        
        # Apply styling
        self.setStyleSheet("""
            #recent-file-item {
                background-color: #ffffff;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                margin-bottom: 8px;
            }
            #recent-file-item:hover {
                background-color: #f5f5f5;
                cursor: pointer;
            }
            QLabel {
                font-family: 'Fira Code', sans-serif;
            }
        """)
        
        # Item layout
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # File icon
        file_icon = QLabel()
        style = self.style()
        icon = style.standardIcon(QStyle.SP_FileIcon)
        file_icon.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(file_icon, 0, 0, 2, 1)
        
        # File name
        name_label = QLabel(file_name)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(name_label, 0, 1)
        
        # File path
        path_label = QLabel(file_path)
        path_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(path_label, 1, 1)
        
        # Operation badge
        op_label = QLabel(operation)
        op_label.setStyleSheet(f"""
            font-size: 12px; 
            color: {'#28a745' if operation == 'Compressed' else '#007bff'}; 
            background-color: {'#e8f5e9' if operation == 'Compressed' else '#e3f2fd'}; 
            padding: 3px 8px;
            border-radius: 4px;
        """)
        layout.addWidget(op_label, 0, 2, Qt.AlignRight)
        
        # Date
        date_label = QLabel(date)
        date_label.setStyleSheet("font-size: 12px; color: #999;")
        layout.addWidget(date_label, 1, 2, Qt.AlignRight)
    
    def mousePressEvent(self, event):
        """Handle mouse press events to make the item clickable"""
        if self.on_click:
            self.on_click(self.file_path)
        super().mousePressEvent(event)

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = None
        self.initUI()
        
        # Try to find the CompressionApp instance
        self.app = self.get_app()
        if self.app:
            print("Dashboard: Successfully connected to CompressionApp")
        else:
            print("Dashboard: Could not find CompressionApp")
        
    def get_app(self):
        """Get the CompressionApp instance"""
        # Check if CompressionApp is available
        if CompressionApp is None:
            print("Dashboard: CompressionApp class is not available")
            return None
            
        # First check if the direct parent is the CompressionApp
        if isinstance(self.parent(), CompressionApp):
            return self.parent()
            
        # Then try to find it in the widget hierarchy
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, CompressionApp):
                return parent
            parent = parent.parent()
            
        # If not found in hierarchy, try to find the main window
        for widget in QApplication.instance().topLevelWidgets():
            if isinstance(widget, CompressionApp):
                return widget
                
        return None
        
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Dashboard header
        header_layout = QHBoxLayout()
        
        # Dashboard title
        self.dashboard_label = QLabel('Dashboard Overview')
        self.dashboard_label.setStyleSheet("font-family: 'Fira Code'; font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(self.dashboard_label)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Fira Code';
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignRight)
        
        main_layout.addLayout(header_layout)
        
        # Quick actions section
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setStyleSheet("font-family: 'Fira Code'; font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        main_layout.addWidget(quick_actions_label)
        
        # Quick action buttons
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(15)
        
        # Create action buttons with direct connections
        browse_btn = self.create_action_button(quick_actions_layout, "Browse Files", "SP_DirOpenIcon")
        browse_btn.clicked.connect(self.browse_files)
        
        compress_btn = self.create_action_button(quick_actions_layout, "Compress File", "SP_ArrowDown")
        compress_btn.clicked.connect(self.compress_action)
        
        decompress_btn = self.create_action_button(quick_actions_layout, "Decompress File", "SP_ArrowUp")
        decompress_btn.clicked.connect(self.decompress_action)
        
        history_btn = self.create_action_button(quick_actions_layout, "View History", "SP_BrowserReload")
        history_btn.clicked.connect(self.history_action)
        
        main_layout.addLayout(quick_actions_layout)
        
        # Stats section
        stats_label = QLabel("Statistics")
        stats_label.setStyleSheet("font-family: 'Fira Code'; font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        main_layout.addWidget(stats_label)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Create stat cards
        self.total_files_card = StatCard("Total Files", "0", "SP_FileIcon")
        self.space_saved_card = StatCard("Space Saved", "0 MB", "SP_DriveHDIcon")
        self.compression_ratio_card = StatCard("Avg. Compression", "0%", "SP_ArrowDown")
        
        stats_layout.addWidget(self.total_files_card)
        stats_layout.addWidget(self.space_saved_card)
        stats_layout.addWidget(self.compression_ratio_card)
        
        main_layout.addLayout(stats_layout)
        
        # Recent files section
        recent_label = QLabel("Recent Files")
        recent_label.setStyleSheet("font-family: 'Fira Code'; font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        main_layout.addWidget(recent_label)
        
        # Scroll area for recent files
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for recent files
        self.recent_files_container = QWidget()
        self.recent_files_layout = QVBoxLayout(self.recent_files_container)
        self.recent_files_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_files_layout.setSpacing(10)
        
        scroll_area.setWidget(self.recent_files_container)
        main_layout.addWidget(scroll_area)
        
        # Add a spacer at the bottom
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Load initial data
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load dashboard data from the app's history"""
        # Initialize default values
        total_files = 0
        space_saved = 0
        compression_ratio = 0
        
        # Try to get real data from the parent (CompressionApp)
        if hasattr(self.parent(), 'file_history') and self.parent().file_history:
            # We have history data
            history = self.parent().file_history
            
            # Calculate statistics
            total_files = len(history)
            
            # Calculate space saved (if available)
            compressed_files = 0
            original_sizes = 0
            compressed_sizes = 0
            
            for entry in history:
                if 'original_size' in entry and 'compressed_size' in entry:
                    original_sizes += entry['original_size']
                    compressed_sizes += entry['compressed_size']
                    compressed_files += 1
            
            if original_sizes > 0 and compressed_files > 0:
                space_saved = original_sizes - compressed_sizes
                compression_ratio = int((1 - (compressed_sizes / original_sizes)) * 100)
            
            # Format space saved
            space_saved_mb = space_saved / (1024 * 1024)  # Convert to MB
            space_saved_str = f"{space_saved_mb:.1f} MB" if space_saved_mb < 1000 else f"{space_saved_mb/1024:.1f} GB"
            
            # Update stat cards
            self.total_files_card.update_value(total_files)
            self.space_saved_card.update_value(space_saved_str)
            self.compression_ratio_card.update_value(f"{compression_ratio}%")
            
            # Clear existing recent files
            for i in reversed(range(self.recent_files_layout.count())):
                widget = self.recent_files_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Add history items (most recent first)
            recent_entries = sorted(history, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
            
            for entry in recent_entries:
                file_name = os.path.basename(entry.get('file_path', 'Unknown'))
                file_path = os.path.dirname(entry.get('file_path', ''))
                operation = entry.get('operation', 'Unknown')
                date = entry.get('date', 'Unknown date')
                
                file_item = RecentFileItem(
                    file_name, 
                    file_path, 
                    operation, 
                    date,
                    on_click=self.handle_file_click
                )
                self.recent_files_layout.addWidget(file_item)
        else:
            # No history data available
            self.total_files_card.update_value(0)
            self.space_saved_card.update_value("0 MB")
            self.compression_ratio_card.update_value("0%")
        
        # Add a "no files" message if there are no files to display
        if self.recent_files_layout.count() == 0:
            no_files_label = QLabel("No recent files found. Start by compressing or decompressing a file.")
            no_files_label.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #999; padding: 20px;")
            no_files_label.setAlignment(Qt.AlignCenter)
            self.recent_files_layout.addWidget(no_files_label)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Animation effect for refresh
        for widget in [self.total_files_card, self.space_saved_card, self.compression_ratio_card]:
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(300)
            animation.setStartValue(widget.geometry())
            animation.setEndValue(widget.geometry())
            animation.setEasingCurve(QEasingCurve.OutBack)
            animation.start()
        
        # Reload data
        self.load_dashboard_data()
    
    def create_action_button(self, layout, text, icon_name):
        """Create a styled action button and add it to the layout"""
        print(f"Dashboard: Creating button '{text}'")
        btn = QPushButton(text)
        btn.setMinimumHeight(50)
        
        # Set icon if provided
        if icon_name:
            style = self.style()
            icon = style.standardIcon(getattr(style, icon_name))
            btn.setIcon(icon)
        
        # Style the button
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px 15px;
                font-family: 'Fira Code';
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        layout.addWidget(btn)
        return btn
    
    def browse_files(self):
        """Handle browse files button click"""
        print("Dashboard: Browse files button clicked")
        
        # Use the stored app reference if available
        app = self.app or self.get_app()
        
        if app and hasattr(app, 'select_file'):
            app.select_file()
            print("Dashboard: select_file method called")
        else:
            print("Dashboard: Could not find CompressionApp or select_file method")
            # Fallback to QFileDialog
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", "All Files (*)", options=options
            )
            
            if file_path:
                print(f"Selected file: {file_path}")
                if app and hasattr(app, 'process_dropped_file'):
                    app.process_dropped_file(file_path)
                    
                    # Navigate to the appropriate view
                    if file_path.lower().endswith(('.zip', '.gz', '.bz2', '.tar', '.rar', '.7z')):
                        if hasattr(app, 'handle_nav_action'):
                            app.handle_nav_action('decompress')
                        else:
                            self.decompress_action()
                    else:
                        if hasattr(app, 'handle_nav_action'):
                            app.handle_nav_action('compress')
                        else:
                            self.compress_action()
                else:
                    # Handle the file operation directly
                    operation = "decompress" if file_path.lower().endswith(('.zip', '.gz', '.bz2', '.tar', '.rar', '.7z')) else "compress"
                    self.handle_file_operation(file_path, operation)
    
    def compress_action(self):
        """Handle compress button click"""
        print("Dashboard: Compress button clicked")
        app = self.app or self.get_app()
        
        if app and hasattr(app, 'handle_nav_action'):
            app.handle_nav_action("compress")
        else:
            print("Dashboard: Could not find CompressionApp or handle_nav_action method")
            # Show file dialog to select a file to compress
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File to Compress", "", "All Files (*)", options=options
            )
            if file_path:
                self.handle_file_operation(file_path, "compress")
    
    def decompress_action(self):
        """Handle decompress button click"""
        print("Dashboard: Decompress button clicked")
        app = self.app or self.get_app()
        
        if app and hasattr(app, 'handle_nav_action'):
            app.handle_nav_action("decompress")
        else:
            print("Dashboard: Could not find CompressionApp or handle_nav_action method")
            # Show file dialog to select a file to decompress
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File to Decompress", "", 
                "Compressed Files (*.zip *.gz *.bz2 *.tar *.rar *.7z);;All Files (*)", 
                options=options
            )
            if file_path:
                self.handle_file_operation(file_path, "decompress")
    
    def history_action(self):
        """Handle history button click"""
        print("Dashboard: History button clicked")
        app = self.app or self.get_app()
        
        if app and hasattr(app, 'handle_nav_action'):
            app.handle_nav_action("history")
        else:
            print("Dashboard: Could not find CompressionApp or handle_nav_action method")
            QMessageBox.information(self, "History", "History view is not available without CompressionApp access.")
    
    def handle_file_operation(self, file_path, operation_type):
        """Handle file operations directly if CompressionApp is not available"""
        if operation_type == "compress":
            QMessageBox.information(self, 'Compress File', 
                f'Would compress file: {file_path}\n'
                f'(Direct CompressionApp access not available)')
        elif operation_type == "decompress":
            QMessageBox.information(self, 'Decompress File', 
                f'Would decompress file: {file_path}\n'
                f'(Direct CompressionApp access not available)')
        else:
            QMessageBox.information(self, 'File Operation', 
                f'Would perform {operation_type} on file: {file_path}\n'
                f'(Direct CompressionApp access not available)')
    
    def handle_file_click(self, file_path):
        """Handle clicking on a recent file item"""
        # Check if the file exists
        if not os.path.exists(file_path):
            # Show error message if the file doesn't exist
            QMessageBox.warning(self, 'File Not Found', f'The file {file_path} no longer exists.')
            return
            
        # Use the stored app reference if available
        app = self.app or self.get_app()
        
        if app and hasattr(app, 'process_dropped_file'):
            # Process the file
            app.process_dropped_file(file_path)
            
            # Navigate to the appropriate view
            if file_path.lower().endswith(('.zip', '.gz', '.bz2', '.tar', '.rar', '.7z')):
                if hasattr(app, 'handle_nav_action'):
                    app.handle_nav_action('decompress')
                else:
                    self.decompress_action()
            else:
                if hasattr(app, 'handle_nav_action'):
                    app.handle_nav_action('compress')
                else:
                    self.compress_action()
        else:
            print(f"Dashboard: Could not find CompressionApp or process_dropped_file method")
            # Handle the file operation directly
            operation = "decompress" if file_path.lower().endswith(('.zip', '.gz', '.bz2', '.tar', '.rar', '.7z')) else "compress"
            self.handle_file_operation(file_path, operation) 