from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QComboBox, QFileDialog, QColorDialog, 
    QSpacerItem, QSizePolicy, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.updateStyle()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Settings header
        header_layout = QHBoxLayout()

        # Settings title
        self.settings_label = QLabel('Settings')
        self.settings_label.setObjectName("page-title")
        header_layout.addWidget(self.settings_label)

        main_layout.addLayout(header_layout)

        # Theme selection section
        theme_card = self.create_card_widget("Appearance")
        theme_layout = QVBoxLayout(theme_card)
        
        theme_label = QLabel("Select Theme:")
        theme_label.setObjectName("section-header")
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentIndexChanged.connect(self.themeChanged)
        theme_layout.addWidget(self.theme_combo)
        
        main_layout.addWidget(theme_card)

        # Directory section
        dir_card = self.create_card_widget("File Management")
        dir_card_layout = QVBoxLayout(dir_card)
        
        dir_label = QLabel("Default Directory:")
        dir_label.setObjectName("section-header")
        dir_card_layout.addWidget(dir_label)

        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        dir_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browse-btn")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)

        dir_card_layout.addLayout(dir_layout)
        main_layout.addWidget(dir_card)

        # Advanced settings section
        advanced_card = self.create_card_widget("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_card)
        
        # Compression level
        comp_level_layout = QHBoxLayout()
        comp_level_label = QLabel("Default Compression Level:")
        comp_level_layout.addWidget(comp_level_label)
        
        self.comp_level_combo = QComboBox()
        self.comp_level_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.comp_level_combo.setCurrentIndex(1)  # Medium by default
        comp_level_layout.addWidget(self.comp_level_combo)
        
        advanced_layout.addLayout(comp_level_layout)

        # Auto-save option
        self.auto_save_check = QCheckBox("Auto-save compression history")
        self.auto_save_check.setChecked(True)
        advanced_layout.addWidget(self.auto_save_check)
        
        main_layout.addWidget(advanced_card)

        # Buttons section
        button_layout = QHBoxLayout()
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary-btn")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("secondary-btn")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        main_layout.addLayout(button_layout)

        # Add a spacer at the bottom
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def create_card_widget(self, title=None):
        """Create a card-like container for settings sections"""
        card = QFrame()
        card.setObjectName("settings-card")
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)
        card.setStyleSheet("""
            #settings-card {
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        if title:
            layout = QVBoxLayout(card)
            layout.setContentsMargins(15, 15, 15, 15)
            
            title_label = QLabel(title)
            title_label.setObjectName("card-title")
            title_label.setStyleSheet("""
                font-weight: bold;
                font-size: 16px;
                padding-bottom: 5px;
                border-bottom: 1px solid;
                margin-bottom: 10px;
            """)
            
            layout.addWidget(title_label)
        
        return card

    def updateStyle(self):
        """Update the style based on the parent's dark mode setting"""
        if hasattr(self.parent, 'dark_mode') and self.parent.dark_mode:
            self.theme_combo.setCurrentIndex(1)  # Dark
            # Update card styling for dark mode
            for card in self.findChildren(QFrame, "settings-card"):
                card.setStyleSheet("""
                    #settings-card {
                        background-color: #2d2d30;
                        border-radius: 8px;
                        padding: 15px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                    }
                """)
        else:
            self.theme_combo.setCurrentIndex(0)  # Light
            # Update card styling for light mode
            for card in self.findChildren(QFrame, "settings-card"):
                card.setStyleSheet("""
                    #settings-card {
                        background-color: #f9f9f9;
                        border-radius: 8px;
                        padding: 15px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }
                """)

    def themeChanged(self, index):
        """Handle theme change in the combo box"""
        if hasattr(self.parent, 'theme_switch'):
            # Update the parent's theme switch to match
            self.parent.theme_switch.setChecked(index == 1)

    def browse_directory(self):
        """Open a dialog to select a directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def reset_settings(self):
        """Reset settings to default values"""
        self.theme_combo.setCurrentIndex(0)  # Light theme
        self.dir_input.setText("")
        self.comp_level_combo.setCurrentIndex(1)  # Medium
        self.auto_save_check.setChecked(True)
        QMessageBox.information(self, "Settings Reset", "All settings have been reset to default values.")

    def save_settings(self):
        """Save the settings"""
        theme = self.theme_combo.currentText()
        default_dir = self.dir_input.text()
        comp_level = self.comp_level_combo.currentText()
        auto_save = "Enabled" if self.auto_save_check.isChecked() else "Disabled"
        
        message = f"Theme: {theme}\nDefault Directory: {default_dir}\nCompression Level: {comp_level}\nAuto-save: {auto_save}"
        QMessageBox.information(self, "Settings Saved", message) 