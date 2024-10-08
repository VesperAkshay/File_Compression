import bz2

def compress(input_file, output_file):
    """
    Compresses a text file using bzip2.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output compressed file.
    """
    try:
        # Read the input text file
        with open(input_file, 'rb') as f:
            data = f.read()

        # Compress the data using bzip2
        compressed_data = bz2.compress(data)

        # Save the compressed data to the output file
        with open(output_file, 'wb') as f:
            f.write(compressed_data)

    except Exception as e:
        print(f"Compression error: {e}")

def decompress(input_file, output_file):
    """
    Decompresses a text file compressed with bzip2.

    Args:
        input_file (str): Path to the compressed file.
        output_file (str): Path to save the decompressed file.
    """
    try:
        # Read the compressed data
        with open(input_file, 'rb') as f:
            compressed_data = f.read()

        # Decompress the data
        decompressed_data = bz2.decompress(compressed_data)

        # Save the original data to the output file
        with open(output_file, 'wb') as f:
            f.write(decompressed_data)

    except Exception as e:
        print(f"Decompression error: {e}")