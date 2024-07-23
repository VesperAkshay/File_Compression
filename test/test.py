# main.py
import argparse
import os
import sys
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress

def main():
    parser = argparse.ArgumentParser(description="File Compression and Decompression Tool")
    parser.add_argument('mode', choices=['compress', 'decompress'], help="Mode of operation: compress or decompress")
    parser.add_argument('algorithm', choices=['deflate', 'huffman', 'lzw'], help="Compression algorithm: deflate, huffman, or lzw")
    parser.add_argument('input_file', help="Input file path")
    parser.add_argument('output_file', help="Output file path")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: The file {args.input_file} does not exist.")
        sys.exit(1)
    
    if args.algorithm == 'deflate':
        if args.mode == 'compress':
            deflate_compress(args.input_file, args.output_file)
            print(f"File compressed successfully using Deflate and saved to {args.output_file}")
        else:
            deflate_decompress(args.input_file, args.output_file)
            print(f"File decompressed successfully using Deflate and saved to {args.output_file}")
    
    elif args.algorithm == 'huffman':
        huffman = HuffmanCoding(args.input_file)
        if args.mode == 'compress':
            output_path = huffman.compress()
            os.rename(output_path, args.output_file)
            os.rename(output_path + '.tree', args.output_file + '.tree')
            print(f"File compressed successfully using Huffman and saved to {args.output_file}")
        else:
            huffman.decompress(args.input_file)
            os.rename('decompressed_file.txt', args.output_file)
            print(f"File decompressed successfully using Huffman and saved to {args.output_file}")
    
    elif args.algorithm == 'lzw':
        if args.mode == 'compress':
            lzw_compress(args.input_file, args.output_file)
            print(f"File compressed successfully using LZW and saved to {args.output_file}")
        else:
            lzw_decompress(args.input_file, args.output_file)
            print(f"File decompressed successfully using LZW and saved to {args.output_file}")

if __name__ == "__main__":
    main()
