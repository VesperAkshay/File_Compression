# File Compression Application - Technical Documentation

## 1. Introduction

The File Compression Application is a desktop utility that provides a user-friendly interface for compressing and decompressing files using various compression algorithms. This application is built using Python with PyQt5 for the graphical user interface.

### 1.1 Purpose

This document provides comprehensive technical details about the application's architecture, components, classes, and usage instructions for developers who want to understand, maintain, or extend the application.

### 1.2 Scope

The File Compression Application supports multiple compression algorithms including:
- Huffman coding
- LZW (Lempel-Ziv-Welch)
- Deflate
- Run-Length Encoding
- Arithmetic coding

Users can select files, choose a compression algorithm, and compress or decompress files through an intuitive interface.

## 2. System Architecture

### 2.1 High-Level Architecture

The application follows a modular architecture with separate components for:
- User Interface (UI)
- Compression Engine
- Algorithm Implementations
- File Handling

```
┌───────────────────────────────────────┐
│            User Interface             │
│  (CompressionApp, UI Components)      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│       Compression Handler              │
│   (Strategy pattern implementation)    │
└───┬───────────┬───────────┬───────────┘
    │           │           │
    ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Huffman │ │   LZW   │ │ Deflate │ ...
│Algorithm│ │Algorithm│ │Algorithm│
└─────────┘ └─────────┘ └─────────┘
```

### 2.2 Design Patterns

The application implements several design patterns:
- **Strategy Pattern**: For interchangeable compression algorithms
- **Factory Pattern**: For creating appropriate compression algorithm instances
- **Observer Pattern**: For UI updates during compression operations
- **Singleton Pattern**: For the compression handler instance

## 3. Component Descriptions

### 3.1 Main Application (main.py)

The entry point of the application that initializes the UI and sets up the application environment. It handles theme settings and launches the main window.

### 3.2 User Interface (ui/ui_components.py)

Contains all UI components including:
- Main application window
- File selection components
- Compression controls
- Results display
- Settings panel
- Animated buttons and interactive elements

### 3.3 Compression Handler (compression/compression_handler.py)

Central orchestrator for compression operations that:
- Selects appropriate compression algorithm based on user choice
- Manages file I/O operations
- Tracks compression statistics (ratio, time)
- Provides progress updates to the UI

### 3.4 Compression Algorithms

#### 3.4.1 Huffman Coding (huffman/huffman.py)
Implementation of Huffman coding algorithm for lossless data compression.

#### 3.4.2 LZW (lzw/lzw.py)
Implementation of the Lempel-Ziv-Welch algorithm for dictionary-based compression.

#### 3.4.3 Deflate (deflate/deflate.py)
Implementation of the Deflate algorithm combining LZ77 and Huffman coding.

#### 3.4.4 Other Algorithms
Additional compression algorithms (RLE, Arithmetic coding, etc.) with their implementations.

## 4. Class Reference

### 4.1 CompressionApp Class

```python
class CompressionApp(QMainWindow):
```

**Description**: Main application window that manages the user interface and interactions.

**Key Methods**:
- `__init__(self)`: Initializes the application window and components
- `set_dark_mode(self, enabled)`: Toggles dark mode
- `select_file(self)`: Opens file selection dialog
- `compress_file(self)`: Initiates file compression
- `decompress_file(self)`: Initiates file decompression
- `update_progress(self, value)`: Updates progress bar

### 4.2 AnimatedButton Class

```python
class AnimatedButton(QPushButton):
```

**Description**: Enhanced button with hover and click animations.

**Key Methods**:
- `__init__(self, text)`: Creates button with text
- `enterEvent(self, event)`: Handles mouse hover animation
- `leaveEvent(self, event)`: Handles mouse leave animation

### 4.3 CardFrame Class

```python
class CardFrame(QFrame):
```

**Description**: Custom frame with card-like appearance for UI grouping.

**Key Methods**:
- `__init__(self)`: Initializes the card frame with styling
- `setContent(self, layout)`: Sets the content layout for the card

### 4.4 CompressionHandler Class

```python
class CompressionHandler:
```

**Description**: Manages compression and decompression operations.

**Key Methods**:
- `__init__(self)`: Initializes the handler
- `compress(self, file_path, algorithm, callback=None)`: Compresses file using specified algorithm
- `decompress(self, file_path, callback=None)`: Decompresses file
- `get_statistics(self)`: Returns compression statistics

### 4.5 HuffmanCompression Class

```python
class HuffmanCompression:
```

**Description**: Implements Huffman coding compression algorithm.

**Key Methods**:
- `compress(self, data)`: Compresses input data
- `decompress(self, data, tree)`: Decompresses data using Huffman tree
- `build_frequency_table(self, data)`: Builds frequency table for input data
- `build_huffman_tree(self, freq_table)`: Builds Huffman tree from frequency table

### 4.6 LZWCompression Class

```python
class LZWCompression:
```

**Description**: Implements LZW compression algorithm.

**Key Methods**:
- `compress(self, data)`: Compresses input data
- `decompress(self, data)`: Decompresses data
- `build_dictionary(self)`: Builds initial dictionary for compression

## 5. Data Flow

### 5.1 Compression Flow

1. User selects a file for compression
2. User chooses compression algorithm
3. UI calls CompressionHandler.compress()
4. CompressionHandler creates appropriate algorithm instance
5. Algorithm compresses the file
6. Progress updates are sent to UI
7. Compression statistics are displayed to user

### 5.2 Decompression Flow

1. User selects a compressed file
2. CompressionHandler detects file type
3. Appropriate decompression algorithm is selected
4. File is decompressed
5. Original file is restored

## 6. Usage Instructions

### 6.1 Compressing Files

1. Launch the application
2. Click "Select File" button
3. Choose a file to compress
4. Select compression algorithm from dropdown
5. Click "Compress" button
6. Monitor progress and wait for completion
7. Access the compressed file in the same directory as the original

### 6.2 Decompressing Files

1. Launch the application
2. Click "Select File" button
3. Choose a compressed file (with extension matching the compression algorithm)
4. Click "Decompress" button
5. Monitor progress and wait for completion
6. Access the decompressed file in the same directory

### 6.3 Configuration Options

The application provides several configuration options:
- Dark/Light mode toggle
- Compression level (when supported by algorithm)
- Output directory selection
- File naming options

## 7. Performance Considerations

### 7.1 Memory Usage

- Huffman: Moderate memory usage for frequency tables and tree
- LZW: Higher memory usage for dictionary
- Deflate: Balanced memory usage

### 7.2 Processing Time

- Huffman: Fast for text files
- LZW: Efficient for repetitive data
- Deflate: Best overall performance for general files

## 8. Error Handling

The application implements comprehensive error handling for scenarios including:
- File not found
- Invalid file format
- Insufficient disk space
- Memory limitations
- Corrupted compressed files

Error messages are displayed to the user with appropriate guidance for resolution.

## 9. Troubleshooting

### 9.1 Common Issues

#### UI Indentation Error
If encountering an indentation error in ui_components.py, check line 82 for proper indentation of the setStyleSheet method call.

#### Dark Mode Toggle Issues
If dark mode isn't applying correctly, verify that all components are properly inheriting theme properties.

#### Compression Fails
If compression fails:
- Check file permissions
- Ensure sufficient disk space
- Verify file isn't already compressed with the same algorithm

### 9.2 Logging

The application logs operations to a log file located in the application directory. Log levels can be adjusted in the settings.

## 10. Extension Points

The application is designed for extensibility:
- New compression algorithms can be added by implementing the base Compressor interface
- UI themes can be customized by modifying the theme.json file
- Additional file formats can be supported by extending the file handler

## 11. Dependencies

The application relies on the following external libraries:
- PyQt5: For the graphical user interface
- zlib: For deflate algorithm implementation
- numpy: For numerical operations in some algorithms
- bitarray: For bit-level operations in Huffman coding

