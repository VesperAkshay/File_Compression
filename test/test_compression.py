#!/usr/bin/env python3
"""
Compression Algorithm Test Script

This script tests all compression algorithms available in the application
with different file types and provides detailed results on:
- Compression ratio
- Compression speed
- Decompression speed
- File integrity after compression/decompression
"""

import os
import time
import shutil
import hashlib
import argparse
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

# Import the compression handler
from compression.compression_handler import CompressionHandler

def create_test_files(test_dir, sizes=None):
    """Create test files of different types and sizes"""
    if sizes is None:
        sizes = [10, 100, 1000]  # KB
    
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = []
    
    # Text files with different patterns
    for size in sizes:
        # Random text
        filename = os.path.join(test_dir, f"random_text_{size}KB.txt")
        with open(filename, 'w') as f:
            # Create random text with some patterns
            text = "This is a test file with some repeating patterns. " * (size * 1024 // 50)
            f.write(text)
        test_files.append(filename)
        
        # Repeating text (highly compressible)
        filename = os.path.join(test_dir, f"repeating_text_{size}KB.txt")
        with open(filename, 'w') as f:
            # Create highly repetitive text
            text = "ABCDEFG" * (size * 1024 // 7)
            f.write(text)
        test_files.append(filename)
    
    return test_files

def get_file_hash(filename):
    """Calculate MD5 hash of a file to verify integrity"""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

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
    start_time = time.time()
    handler.process(algorithm, 'compress', input_file, compressed_file, use_threading=False)
    compression_time = time.time() - start_time
    
    # Get compressed file size
    compressed_size = os.path.getsize(compressed_file)
    compression_ratio = (1 - (compressed_size / file_size)) * 100
    
    # Test decompression
    start_time = time.time()
    handler.process(algorithm, 'decompress', compressed_file, decompressed_file, use_threading=False)
    decompression_time = time.time() - start_time
    
    # Verify integrity
    decompressed_hash = get_file_hash(decompressed_file)
    integrity_check = "PASS" if original_hash == decompressed_hash else "FAIL"
    
    # Return results
    return {
        "algorithm": algorithm,
        "file": file_basename,
        "original_size": file_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "compression_time": compression_time,
        "decompression_time": decompression_time,
        "integrity": integrity_check
    }

def run_tests(test_files, output_dir, algorithms=None):
    """Run tests on all algorithms and files"""
    handler = CompressionHandler()
    
    if algorithms is None:
        algorithms = handler.get_available_algorithms()
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for input_file in test_files:
        for algorithm in algorithms:
            try:
                result = test_algorithm(handler, algorithm, input_file, output_dir)
                results.append(result)
                print(f"Tested {algorithm} on {os.path.basename(input_file)}: {result['compression_ratio']:.2f}% compression")
            except Exception as e:
                print(f"Error testing {algorithm} on {os.path.basename(input_file)}: {str(e)}")
                results.append({
                    "algorithm": algorithm,
                    "file": os.path.basename(input_file),
                    "original_size": os.path.getsize(input_file),
                    "compressed_size": 0,
                    "compression_ratio": 0,
                    "compression_time": 0,
                    "decompression_time": 0,
                    "integrity": "ERROR"
                })
    
    return results

def display_results(results):
    """Display test results in a table"""
    headers = ["Algorithm", "File", "Original Size (B)", "Compressed Size (B)", 
               "Compression Ratio (%)", "Compression Time (s)", "Decompression Time (s)", "Integrity"]
    
    table_data = []
    for result in results:
        table_data.append([
            result["algorithm"],
            result["file"],
            result["original_size"],
            result["compressed_size"],
            f"{result['compression_ratio']:.2f}",
            f"{result['compression_time']:.4f}",
            f"{result['decompression_time']:.4f}",
            result["integrity"]
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def plot_results(results, output_dir):
    """Generate plots for the test results"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Group results by algorithm
    algorithms = {}
    for result in results:
        algo = result["algorithm"]
        if algo not in algorithms:
            algorithms[algo] = []
        algorithms[algo].append(result)
    
    # Plot compression ratios
    plt.figure(figsize=(12, 8))
    
    # Get unique file names
    file_names = sorted(list(set(result["file"] for result in results)))
    
    # Set up the plot
    x = np.arange(len(file_names))
    width = 0.8 / len(algorithms)
    
    # Plot each algorithm
    for i, (algo, algo_results) in enumerate(algorithms.items()):
        # Create a mapping from file name to result
        file_to_result = {r["file"]: r for r in algo_results}
        
        # Get compression ratios for each file
        ratios = [file_to_result.get(file, {"compression_ratio": 0})["compression_ratio"] for file in file_names]
        
        # Plot the bars
        plt.bar(x + i * width, ratios, width, label=algo)
    
    plt.xlabel('Files')
    plt.ylabel('Compression Ratio (%)')
    plt.title('Compression Ratio by Algorithm and File')
    plt.xticks(x + width * (len(algorithms) - 1) / 2, [name[:20] + '...' if len(name) > 20 else name for name in file_names], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'compression_ratios.png'))
    
    # Plot compression times
    plt.figure(figsize=(12, 8))
    
    # Plot each algorithm
    for i, (algo, algo_results) in enumerate(algorithms.items()):
        # Create a mapping from file name to result
        file_to_result = {r["file"]: r for r in algo_results}
        
        # Get compression times for each file
        times = [file_to_result.get(file, {"compression_time": 0})["compression_time"] for file in file_names]
        
        # Plot the bars
        plt.bar(x + i * width, times, width, label=algo)
    
    plt.xlabel('Files')
    plt.ylabel('Compression Time (s)')
    plt.title('Compression Time by Algorithm and File')
    plt.xticks(x + width * (len(algorithms) - 1) / 2, [name[:20] + '...' if len(name) > 20 else name for name in file_names], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'compression_times.png'))
    
    # Plot decompression times
    plt.figure(figsize=(12, 8))
    
    # Plot each algorithm
    for i, (algo, algo_results) in enumerate(algorithms.items()):
        # Create a mapping from file name to result
        file_to_result = {r["file"]: r for r in algo_results}
        
        # Get decompression times for each file
        times = [file_to_result.get(file, {"decompression_time": 0})["decompression_time"] for file in file_names]
        
        # Plot the bars
        plt.bar(x + i * width, times, width, label=algo)
    
    plt.xlabel('Files')
    plt.ylabel('Decompression Time (s)')
    plt.title('Decompression Time by Algorithm and File')
    plt.xticks(x + width * (len(algorithms) - 1) / 2, [name[:20] + '...' if len(name) > 20 else name for name in file_names], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'decompression_times.png'))
    
    print(f"Plots saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Test compression algorithms')
    parser.add_argument('--test-dir', default='test_files', help='Directory to store test files')
    parser.add_argument('--output-dir', default='test_results', help='Directory to store test results')
    parser.add_argument('--algorithms', nargs='+', help='Specific algorithms to test')
    parser.add_argument('--sizes', nargs='+', type=int, default=[10, 100, 1000], help='Sizes of test files in KB')
    parser.add_argument('--no-plots', action='store_true', help='Do not generate plots')
    
    args = parser.parse_args()
    
    # Create test files
    print(f"Creating test files in {args.test_dir}...")
    test_files = create_test_files(args.test_dir, args.sizes)
    
    # Run tests
    print(f"Running tests with {len(test_files)} files and storing results in {args.output_dir}...")
    results = run_tests(test_files, args.output_dir, args.algorithms)
    
    # Display results
    print("\nTest Results:")
    display_results(results)
    
    # Generate plots
    if not args.no_plots:
        try:
            print("\nGenerating plots...")
            plot_results(results, args.output_dir)
        except Exception as e:
            print(f"Error generating plots: {str(e)}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 