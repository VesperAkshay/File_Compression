# Compression Algorithm Testing

This directory contains scripts for testing the compression algorithms implemented in the application.

## Requirements

Before running the tests, make sure you have the required dependencies:

```bash
pip install tabulate matplotlib numpy
```

## Quick Test

The `quick_test.py` script allows you to quickly test all compression algorithms on a single file.

### Usage

```bash
python quick_test.py <file_to_compress> [--output-dir OUTPUT_DIR] [--algorithms ALGORITHM1 ALGORITHM2 ...]
```

### Examples

Test all algorithms on a text file:
```bash
python quick_test.py sample.txt
```

Test specific algorithms:
```bash
python quick_test.py sample.txt --algorithms deflate huffman
```

Specify an output directory:
```bash
python quick_test.py sample.txt --output-dir my_test_results
```

## Comprehensive Test

The `test_compression.py` script performs a comprehensive test of all compression algorithms with different file types and sizes. It generates test files, compresses and decompresses them, and provides detailed results including plots.

### Usage

```bash
python test_compression.py [--test-dir TEST_DIR] [--output-dir OUTPUT_DIR] [--algorithms ALGORITHM1 ALGORITHM2 ...] [--sizes SIZE1 SIZE2 ...] [--no-plots]
```

### Examples

Run a comprehensive test with default settings:
```bash
python test_compression.py
```

Test specific algorithms with specific file sizes:
```bash
python test_compression.py --algorithms deflate huffman --sizes 10 50 100
```

Run tests without generating plots:
```bash
python test_compression.py --no-plots
```

## Test Results

The test results include:

1. **Compression Ratio**: The percentage reduction in file size.
2. **Compression Time**: The time taken to compress the file.
3. **Decompression Time**: The time taken to decompress the file.
4. **Integrity Check**: Verification that the decompressed file matches the original.

For the comprehensive test, plots are generated to visualize:
- Compression ratios across different file types and algorithms
- Compression times across different file types and algorithms
- Decompression times across different file types and algorithms

## Interpreting Results

- **Higher compression ratio** is better (more space saved).
- **Lower compression/decompression time** is better (faster processing).
- **Integrity check** should always be "PASS" for lossless compression.

Different algorithms may perform better for different file types:
- Text files with repetitive patterns typically compress well with dictionary-based algorithms like LZW.
- Files with varied content may benefit from entropy-based algorithms like Huffman coding.
- The best algorithm depends on your specific use case and priorities (speed vs. compression ratio). 