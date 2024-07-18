# deflate/deflate.py
import zlib

def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    compressed_data = zlib.compress(data, level=9)
    
    with open(output_file, 'wb') as f:
        f.write(compressed_data)

def decompress_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        compressed_data = f.read()
    decompressed_data = zlib.decompress(compressed_data)
    
    with open(output_file, 'wb') as f:
        f.write(decompressed_data)
