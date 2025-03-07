# deflate/deflate.py
import zlib
import os

def compress_file(input_file, output_file, progress_callback=None):
    # Get file size for progress calculation
    file_size = os.path.getsize(input_file)
    
    with open(input_file, 'rb') as f:
        data = f.read()
        
        # Call progress callback with bytes read
        if progress_callback:
            progress_callback(file_size)
            
    compressed_data = zlib.compress(data, level=9)
    
    with open(output_file, 'wb') as f:
        f.write(compressed_data)

def decompress_file(input_file, output_file, progress_callback=None):
    # Get file size for progress calculation
    file_size = os.path.getsize(input_file)
    
    with open(input_file, 'rb') as f:
        compressed_data = f.read()
        
        # Call progress callback with bytes read
        if progress_callback:
            progress_callback(file_size)
            
    decompressed_data = zlib.decompress(compressed_data)
    
    with open(output_file, 'wb') as f:
        f.write(decompressed_data)
