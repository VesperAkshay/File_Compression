import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    # List all packages that need to be included
    "packages": [
        "os", 
        "sys", 
        "PyQt5", 
        "PyQt5.QtWidgets",
        "PyQt5.QtCore", 
        "PyQt5.QtGui",
        "zlib",  # For deflate compression
    ],
    # List all modules that need to be included
    "includes": [
        "ui.ui_components",
        "compression.compression_handler",
        "huffman.huffman",
        "lzw.lzw",
        "deflate.deflate",
    ],
    # Include all subpackages explicitly
    "include_files": [
        ("ui", "ui"),
        ("compression", "compression"),
        ("huffman", "huffman"),
        ("lzw", "lzw"),
        ("deflate", "deflate"),
        # Add additional resource files if needed
        # ("path/to/icon.ico", "icon.ico"),
    ],
    # Exclude packages not needed in the final build
    "excludes": [
        "tkinter", 
        "unittest",
        "email",
        "http",
        "xml",
        "pydoc_data",
        "PyQt5.QtQml",
        "PyQt5.QtQuick",
        "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtWebEngine",
        "PyQt5.QtNetwork",
    ],
    "include_msvcr": True,  # Include Microsoft Visual C++ runtime
}

# Base for Windows executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this for Windows GUI applications

executables = [
    Executable(
        script="main.py",  # Main entry point script
        base=base,
        target_name="FileCompression.exe",
        icon=None,  # Add path to your icon if available
        shortcut_name="File Compression",
        shortcut_dir="DesktopFolder",
        copyright="Copyright © 2023",
    )
]

setup(
    name="File Compression",
    version="1.0.0",
    description="Advanced file compression utility with multiple algorithms",
    author="Your Name",
    author_email="your.email@example.com",
    options={"build_exe": build_exe_options},
    executables=executables,
    # Additional setup options
    requires=[
        'PyQt5',
        'zlib',
    ],
)

# Notes for building:
# 1. Run "python setup.py build" to build the executable
# 2. Run "python setup.py bdist_msi" to create a Windows installer
# 3. The built files will be in the "build" directory
# 4. The installer will be in the "dist" directory

