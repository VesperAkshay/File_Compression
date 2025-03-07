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
        "numpy",
        "PIL",
        "soundfile",
        "io",
        "bz2",
    ],
    # List all modules that need to be included
    "includes": [
        "ui.ui_components",
        "compression.compression_handler",
        "huffman.huffman",
        "lzw.lzw",
        "deflate.deflate",
        "burrowswheeler.burrowswheeler",
        "jpeg_2000",
        "pyflacaudio",
        "file_compression",
    ],
    # Include all subpackages explicitly
    "include_files": [
        ("ui", "ui"),
        ("compression", "compression"),
        ("huffman", "huffman"),
        ("lzw", "lzw"),
        ("deflate", "deflate"),
        ("burrowswheeler", "burrowswheeler"),
        ("jpeg_2000", "jpeg_2000"),
        ("pyflacaudio", "pyflacaudio"),
        ("icons", "icons"),
        # Add additional resource files if needed
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
        icon="icons/app_icon.ico" if os.path.exists("icons/app_icon.ico") else None,  # Use app icon if available
        shortcut_name="File Compression",
        shortcut_dir="DesktopFolder",
        copyright="Copyright © 2023",
    )
]

setup(
    name="File Compression",
    version="1.0.0",
    description="Advanced file compression utility with multiple algorithms",
    long_description="A comprehensive file compression application supporting multiple algorithms including Huffman, LZW, Deflate, Burrows-Wheeler, JPEG 2000, and FLAC audio compression.",
    author="Akshay Patel",
    author_email="apexl563@gmail.com",
    options={"build_exe": build_exe_options},
    executables=executables,
    packages=[
        "ui",
        "compression",
        "huffman",
        "lzw",
        "deflate",
        "burrowswheeler",
        "jpeg_2000",
        "pyflacaudio",
    ],
    package_data={
        "": ["*.ico", "*.png", "*.jpg", "*.gif", "*.ui"],
        "icons": ["*"],
    },
    include_package_data=True,
    # Additional setup options
    # Additional setup options
    requires=[
        'PyQt5',
        'zlib',
        'numpy',
        'Pillow',  # PIL's installable name
        'soundfile',
    ],
    install_requires=[
        'PyQt5',
        'numpy',
        'Pillow',
        'soundfile',
    ],
    python_requires='>=3.6',
)

# Notes for building:
# 1. Run "python setup.py build" to build the executable
# 2. Run "python setup.py bdist_msi" to create a Windows installer
# 3. The built files will be in the "build" directory
# 4. The installer will be in the "dist" directory

