import sys
import os
import sys
import logging
import tempfile
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from ui.ui_components import CompressionApp
from compression.compression_handler import CompressionHandler

# Set up logging
def setup_directories():
    """Create all necessary directories for the application"""
    # Determine if we're running in a frozen environment (like cx_Freeze)
    if getattr(sys, 'frozen', False):
        # If frozen, use user's AppData directory (Windows) or home directory (others)
        if os.name == 'nt':  # Windows
            base_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FileCompression')
        else:  # macOS, Linux, etc.
            base_dir = os.path.join(os.path.expanduser('~'), '.filecompression')
    else:
        # If not frozen, use the directory of the script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    dirs = ['logs', 'temp', 'icons']
    created_dirs = {}
    
    for dir_name in dirs:
        dir_path = os.path.join(base_dir, dir_name)
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logging.info(f"Created directory: {dir_path}")
            created_dirs[dir_name] = dir_path
        except Exception as e:
            logging.error(f"Failed to create directory {dir_path}: {str(e)}")
    
    return created_dirs

def setup_logging():
    """Set up basic logging for the application"""
    # Determine if we're running in a frozen environment (like cx_Freeze)
    if getattr(sys, 'frozen', False):
        # If frozen, use user's AppData directory (Windows) or home directory (others)
        if os.name == 'nt':  # Windows
            log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FileCompression', 'logs')
        else:  # macOS, Linux, etc.
            log_dir = os.path.join(os.path.expanduser('~'), '.filecompression', 'logs')
    else:
        # If not frozen, use the directory of the script
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        # Fall back to user directory if logs dir can't be created
        print(f"Warning: Could not create logs directory: {str(e)}")
        log_dir = os.path.expanduser('~')
    
    log_file = os.path.join(log_dir, 'compression_app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('compression_app')

def setup_temp_directories():
    """Create necessary temporary directories"""
    # Determine if we're running in a frozen environment (like cx_Freeze)
    if getattr(sys, 'frozen', False):
        # If frozen, use user's AppData directory (Windows) or home directory (others)
        if os.name == 'nt':  # Windows
            temp_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FileCompression', 'temp')
        else:  # macOS, Linux, etc.
            temp_dir = os.path.join(os.path.expanduser('~'), '.filecompression', 'temp')
    else:
        # If not frozen, use the directory of the script
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    
    try:
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    except Exception as e:
        logging.error(f"Failed to create temp directory: {str(e)}")
        # Fall back to system temp directory
        temp_dir = os.path.join(tempfile.gettempdir(), 'filecompression')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    
    return temp_dir

def setup_app_style(app):
    """Set up application style and theme"""
    # Use Fusion style for a modern look
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set the application palette for better colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    
    # app.setPalette(palette)  # Commented out for now, enable if dark mode is default

def setup_app_icons(app):
    """Set up application icons"""
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning(f"App icon not found at {icon_path}")
    except Exception as e:
        logging.error(f"Error setting application icon: {str(e)}")

def main():
    # Set up logging
    logger = setup_logging()
    logger.info("Starting File Compression Application")

    # Create all necessary directories
    try:
        app_dirs = setup_directories()
        logger.info(f"Application directories set up: {', '.join(app_dirs.keys())}")
    except Exception as e:
        logger.error(f"Error setting up application directories: {str(e)}")
    
    try:
        # Initialize QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("File Compression Tool")
        app.setApplicationDisplayName("File Compression Tool")
        app.setOrganizationName("CompressOrg")
        
        # Set up application style and icons
        setup_app_style(app)
        setup_app_icons(app)
        
        # Initialize the compression handler
        compression_handler = CompressionHandler()
        logger.info("Compression handler initialized")
        
        # Initialize the UI and connect it to the compression handler
        window = CompressionApp(compression_handler)
        window.setWindowTitle("File Compression Tool")
        window.resize(800, 600)  # Set a reasonable starting size
        window.show()
        logger.info("UI initialized and shown")
        
        # Run the application
        return_code = app.exec_()
        logger.info(f"Application exiting with code: {return_code}")
        sys.exit(return_code)
        
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
