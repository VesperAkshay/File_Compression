#!/usr/bin/env python3
"""
Quick Compression Algorithm Test

This script tests all compression algorithms on a single file and displays the results.
"""

import os
import time
import hashlib
import argparse
from tabulate import tabulate

from compression.compression_handler import CompressionHandler

def get_file_hash(filename):
    """Calculate MD5 hash of a file to verify integrity"""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def format_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def test_algorithm(handler, algorithm, input_file, output_dir):
    """Test a specific compression algorithm on a file"""
    file_basename = os.path.basename(input_file)
    file_size = os.path.getsize(input_file)
    
    # Prepare output files
    compressed_file = os.path.join(output_dir, f"{file_basename}.{algorithm}.bin")
    decompressed_file = os.path.join(output_dir, f"{file_basename}.{algorithm}.decompressed")
    
    # Calculate original file hash
    original_hash = get_file_hash(input_file)
    
    # Test compression
    print(f"Testing {algorithm} compression...")
    start_time = time.time()
    handler.process(algorithm, 'compress', input_file, compressed_file, use_threading=False)
    compression_time = time.time() - start_time
    
    # Get compressed file size
    compressed_size = os.path.getsize(compressed_file)
    compression_ratio = (1 - (compressed_size / file_size)) * 100
    
    # Test decompression
    print(f"Testing {algorithm} decompression...")
    start_time = time.time()
    handler.process(algorithm, 'decompress', compressed_file, decompressed_file, use_threading=False)
    decompression_time = time.time() - start_time
    
    # Verify integrity
    decompressed_hash = get_file_hash(decompressed_file)
    integrity_check = "PASS" if original_hash == decompressed_hash else "FAIL"
    
    # Return results
    return {
        "algorithm": algorithm,
        "original_size": file_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "integrity": integrity_check
    }

def main():
    parser = argparse.ArgumentParser(description='Quick test of compression algorithms')
    parser.add_argument('file', help='File to compress')
    parser.add_argument('--output-dir', default='quick_test_results', help='Directory to store test results')
    parser.add_argument('--algorithms', nargs='+', help='Specific algorithms to test')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist")
        return
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize compression handler
    handler = CompressionHandler()
    
    # Get algorithms to test
    if args.algorithms:
        algorithms = args.algorithms
    else:
        algorithms = handler.get_available_algorithms()
    
    # Run tests
    results = []
    for algorithm in algorithms:
        try:
            result = test_algorithm(handler, algorithm, args.file, args.output_dir)
            results.append(result)
        except Exception as e:
            print(f"Error testing {algorithm}: {str(e)}")
            results.append({
                "algorithm": algorithm,
                "original_size": os.path.getsize(args.file),
                "compressed_size": 0,
                "compression_ratio": 0,
                "compression_time": 0,
                "decompression_time": 0,
                "integrity": "ERROR"
            })
    
    # Display results
    print("\nTest Results:")
    headers = ["Algorithm", "Original Size", "Compressed Size", 
               "Compression Ratio (%)", "Compression Time (s)", "Decompression Time (s)", "Integrity"]
    
    table_data = []
    for result in results:
        table_data.append([
            result["algorithm"],
            format_size(result["original_size"]),
            format_size(result["compressed_size"]),
            f"{result['compression_ratio']:.2f}",
            f"{result['compression_time']:.4f}",
            f"{result['decompression_time']:.4f}",
            result["integrity"]
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Find the best algorithm based on compression ratio
    best_algorithm = max(results, key=lambda x: x["compression_ratio"])
    print(f"\nBest compression ratio: {best_algorithm['algorithm']} ({best_algorithm['compression_ratio']:.2f}%)")
    
    # Find the fastest algorithm for compression
    fastest_compression = min(results, key=lambda x: x["compression_time"])
    print(f"Fastest compression: {fastest_compression['algorithm']} ({fastest_compression['compression_time']:.4f}s)")
    
    # Find the fastest algorithm for decompression
    fastest_decompression = min(results, key=lambda x: x["decompression_time"])
    print(f"Fastest decompression: {fastest_decompression['algorithm']} ({fastest_decompression['decompression_time']:.4f}s)")
    
    print(f"\nAll test files are saved in {args.output_dir}")

if __name__ == "__main__":
    main() 