# Software Requirements Specification

## File Compression Application

**Version:** 1.0

**Date:** 2023

---

## Table of Contents
1. [Introduction](#1-introduction)
1. [Purpose](#11-purpose)
2. [Scope](#12-scope)
3. [Definitions, Acronyms, and Abbreviations](#13-definitions-acronyms-and-abbreviations)
4. [References](#14-references)
5. [Overview](#15-overview)
2. [System Overview](#2-system-overview)
1. [System Perspective](#21-system-perspective)
2. [System Functions](#22-system-functions)
3. [User Characteristics](#23-user-characteristics)
4. [Constraints](#24-constraints)
5. [Assumptions and Dependencies](#25-assumptions-and-dependencies)
3. [Functional Requirements](#3-functional-requirements)
1. [File Compression](#31-file-compression)
2. [File Decompression](#32-file-decompression)
3. [Algorithm Selection](#33-algorithm-selection)
4. [File Operations](#34-file-operations)
5. [User Interface](#35-user-interface)
4. [Non-Functional Requirements](#4-non-functional-requirements)
1. [Performance](#41-performance)
2. [Usability](#42-usability)
3. [Reliability](#43-reliability)
4. [Security](#44-security)
5. [Maintainability](#45-maintainability)
5. [System Architecture](#5-system-architecture)
1. [Component Diagram](#51-component-diagram)
2. [Module Descriptions](#52-module-descriptions)
3. [Data Flow](#53-data-flow)
6. [Use Cases](#6-use-cases)
1. [Compress a File](#61-compress-a-file)
2. [Decompress a File](#62-decompress-a-file)
3. [Change Compression Algorithm](#63-change-compression-algorithm)
4. [Toggle Dark Mode](#64-toggle-dark-mode)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document describes the requirements and specifications for the File Compression application. It provides a detailed outline of the functional and non-functional requirements, system architecture, and use cases for the application.

### 1.2 Scope

The File Compression application is designed to compress and decompress files using various algorithms such as Huffman, LZW, and Deflate. The application provides a graphical user interface for users to select files, choose compression algorithms, and perform compression and decompression operations.

The application aims to:

- Reduce file size through efficient compression algorithms
- Provide an intuitive user interface for file operations
- Support multiple compression algorithms with different efficiency characteristics
- Allow users to customize the appearance with light and dark modes

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| Compression | Process of encoding data to use fewer bits than the original representation |
| Decompression | Process of decoding compressed data back to its original form |
| Huffman Coding | An algorithm that uses variable-length codes for encoding characters based on their frequency |
| LZW | Lempel-Ziv-Welch, a universal lossless data compression algorithm |
| Deflate | A lossless data compression algorithm that uses a combination of LZ77 and Huffman coding |
| GUI | Graphical User Interface |
| PyQt | Python binding for the Qt cross-platform application framework |

### 1.4 References

1. Python Programming Language: https://www.python.org/
2. PyQt5 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
3. Huffman Coding: https://en.wikipedia.org/wiki/Huffman_coding
4. LZW Algorithm: https://en.wikipedia.org/wiki/Lempel-Ziv-Welch
5. Deflate Algorithm: https://en.wikipedia.org/wiki/Deflate

### 1.5 Overview

The remainder of this document describes the functionality, requirements, and design of the File Compression application. It includes detailed specifications for user interface components, compression algorithms, and system architecture.

## 2. System Overview

### 2.1 System Perspective

The File Compression application is a standalone desktop application developed using Python and PyQt5. It interacts with the file system to read, compress, and write files. The application does not require external systems or services beyond the operating system's file handling capabilities.

### 2.2 System Functions

The primary functions of the File Compression application include:

- Compressing files using various algorithms (Huffman, LZW, Deflate)
- Decompressing previously compressed files
- Providing file selection capabilities
- Displaying compression statistics (original size, compressed size, compression ratio)
- Supporting UI customization (light/dark mode)

### 2.3 User Characteristics

The application is designed for:

- General computer users who need to compress files for storage or transmission
- Users with basic knowledge of file systems and compression concepts
- Users who prefer a graphical interface over command-line tools

No special technical expertise is required to use the application, though users should understand basic concepts of file compression.

### 2.4 Constraints

- The application is developed in Python, requiring the Python interpreter to be installed
- PyQt5 library must be available for the UI components
- The application's performance is limited by the user's hardware capabilities, particularly for large file operations
- The compression efficiency is dependent on the selected algorithm and the nature of the input data

### 2.5 Assumptions and Dependencies

- The application assumes the user has read and write permissions for the files they wish to compress/decompress
- The application depends on Python 3.6+ and PyQt5
- The application assumes the operating system provides standard file dialog capabilities

## 3. Functional Requirements

### 3.1 File Compression

#### FR-1.1: Compression Algorithm Support

- The system shall support multiple compression algorithms including Huffman, LZW, and Deflate.
- The system shall allow users to select the desired compression algorithm.
- The system shall apply the selected algorithm to compress the chosen file.

#### FR-1.2: Compression Metrics

- The system shall display the original file size before compression.
- The system shall display the compressed file size after compression.
- The system shall calculate and display the compression ratio (percentage of size reduction).
- The system shall display the time taken to complete the compression operation.

#### FR-1.3: File Output

- The system shall save compressed files with an appropriate extension based on the algorithm used.
- The system shall provide feedback on the success or failure of the compression operation.

### 3.2 File Decompression

#### FR-2.1: Decompression Support

- The system shall support decompression of files compressed using any of the supported algorithms.
- The system shall automatically detect the compression algorithm used based on the file extension or header.
- The system shall restore the decompressed file to its original state.

#### FR-2.2: Decompression Metrics

- The system shall display the compressed file size.
- The system shall display the decompressed file size.
- The system shall display the time taken to complete the decompression operation.

#### FR-2.3: File Output

- The system shall save decompressed files with their original filename when possible.
- The system shall provide feedback on the success or failure of the decompression operation.

### 3.3 Algorithm Selection

#### FR-3.1: Algorithm Choice

- The system shall provide a dropdown menu for selecting compression algorithms.
- The system shall display a brief description of each algorithm's characteristics.
- The system shall remember the last used algorithm for subsequent operations.

### 3.4 File Operations

#### FR-4.1: File Selection

- The system shall provide a browse button to open a file selection dialog.
- The system shall display the selected file's path in a text field.
- The system shall allow users to drag and drop files onto the application.

#### FR-4.2: File Validation

- The system shall verify that selected files exist and are accessible.
- The system shall check if the file is already compressed before compression.
- The system shall verify that the file is of a supported format for the operation.

### 3.5 User Interface

#### FR-5.1: Layout

- The system shall provide a clean, intuitive interface with clear sections for different operations.
- The system shall display compression statistics in a dedicated area.
- The system shall provide visual feedback during processing (progress bars, status messages).

#### FR-5.2: Appearance Customization

- The system shall provide a light/dark mode toggle.
- The system shall save the user's preference for light/dark mode between sessions.
- The system shall apply consistent styling across all UI elements when changing modes.

## 4. Non-Functional Requirements

### 4.1 Performance

#### NFR-1.1: Compression Speed

- The system shall compress files in a reasonable time frame, with performance dependent on file size and algorithm.
- The system shall provide progress indication for operations that take more than 2 seconds.

#### NFR-1.2: Memory Usage

- The system shall optimize memory usage during compression/decompression operations.
- The system shall not crash due to out-of-memory errors for files within the supported size range.

### 4.2 Usability

#### NFR-2.1: Ease of Use

- The system shall have a learning curve of less than 10 minutes for basic operations.
- The system shall provide tooltips for buttons and controls.
- The system shall display error messages in plain language.

#### NFR-2.2: Accessibility

- The system shall use color combinations that maintain readability for color-blind users.
- The system shall support keyboard navigation for all major functions.
- The system shall maintain readable text sizes and contrast ratios.

### 4.3 Reliability

#### NFR-3.1: Error Handling

- The system shall handle exceptions gracefully without crashing.
- The system shall provide clear error messages when operations fail.
- The system shall not corrupt files during failed operations.

#### NFR-3.2: Data Integrity

- The system shall ensure that decompressed files are identical to their original versions.
- The system shall implement verification mechanisms to detect corrupted compressed files.

### 4.4 Security

#### NFR-4.1: File Access

- The system shall only access files explicitly selected by the user.
- The system shall not modify files without user permission.

### 4.5 Maintainability

#### NFR-5.1: Code Structure

- The system shall follow object-oriented design principles.
- The system shall separate UI, business logic, and algorithm implementations.
- The system shall be modular to allow easy addition of new compression algorithms.

#### NFR-5.2: Documentation

- The system shall have comprehensive code documentation.
- The system shall maintain up-to-date user documentation.

## 5. System Architecture

### 5.1 Component Diagram

```
+---------------------+
|    CompressionApp   |
| (Main Application)  |
+----------+----------+
        |
        v
+----------+----------+
|                     |
|  UI Components      |
|                     |
+-----+--------+-----+
    |        |
    v        v
+-----+----+  +--------+
|          |  |        |
| File I/O |  | Themes |
|          |  |        |
+-----+----+  +--------+
    |
    v
+-----+----------------+
|                      |
| Compression Handler  |
|                      |
+---+------+------+----+
    |      |      |
    v      v      v
+-----+ +-----+ +-------+
|     | |     | |       |
| LZW | | Huf | | Def.  |
|     | | fman| |       |
+-----+ +-----+ +-------+
```

### 5.2 Module Descriptions

#### Main Application (main.py)

The entry point of the application that initializes the UI components and sets up the application environment.

#### UI Components (ui_components.py)

Contains all the UI elements including buttons, text fields, dropdowns, and layout managers. This module handles user interactions and forwards requests to the appropriate handlers.

#### Compression Handler (compression_handler.py)

Manages the compression and decompression processes. It serves as a facade to the various compression algorithm implementations.

#### Compression Algorithms

- **Huffman**: Implements the Huffman coding algorithm for compression and decompression.
- **LZW**: Implements the Lempel-Ziv-Welch algorithm for compression and decompression.
- **Deflate**: Implements the Deflate algorithm for compression and decompression.

### 5.3 Data Flow

1. User selects a file and compression algorithm through the UI
2. UI passes file path and algorithm choice to the Compression Handler
3. Compression Handler calls the appropriate algorithm module
4. Algorithm performs compression/decompression and returns the result
5. Compression Handler updates the file system with the compressed/decompressed file
6. UI displays the results and statistics to the user

## 6. Use Cases

### 6.1 Compress a File

**Actor:** User

**Precondition:** The application is running, and the user has access to the file to be compressed.

**Main Flow:**
1. User selects "Compress" operation mode
2. User clicks the browse button to select a file
3. User selects a compression algorithm from the dropdown
4. User clicks the "Compress" button
5. System displays progress during compression
6. System saves the compressed file and displays compression statistics

**Alternative Flow:**
- If the file is already compressed, system warns the user
- If the file cannot be accessed, system displays an error message

**Postcondition:** The file is compressed and saved with an appropriate extension.

### 6.2 Decompress a File

**Actor:** User

**Precondition:** The application is running, and the user has access to a previously compressed file.

**Main Flow:**
1. User selects "Decompress" operation mode
2. User clicks the browse button to select a compressed file
3. User clicks the "Decompress" button
4. System displays progress during decompression
5. System saves the decompressed file and displays statistics

**Alternative Flow:**
-

