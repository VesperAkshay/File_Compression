import os
import io
from PIL import Image


def compress_image(input_path, compressed_buffer, quality=70):
    """
    Compress an image using JPEG2000 format.

    :param input_path: Path to the original image file
    :param compressed_buffer: Path to save the compressed image
    :param quality: Quality level for compression (default is 70)
    """
    with Image.open(input_path) as img:
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG2000', quality_mode='dB', quality_layers=[quality])

        compressed_size = buffer.tell()
        buffer.seek(0)

        original_size = os.path.getsize(input_path)
        if compressed_size < original_size:
            print(f"Compression successful. Original size: {original_size}, Compressed size: {compressed_size}")
            with open(compressed_buffer, 'wb') as f:
                f.write(buffer.getvalue())
        else:
            compress_image(input_path, compressed_buffer, quality - 10)


def decompress_image(compressed_buffer, output_path):
    """
    Decompress a JPEG2000 image to a JPEG format.

    :param compressed_buffer: Path to the compressed image file
    :param output_path: Path to save the decompressed image
    """
    with Image.open(compressed_buffer) as img:
        img.save(output_path, format='JPEG', quality=95)
