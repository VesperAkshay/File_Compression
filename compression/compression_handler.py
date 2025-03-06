import os
import time
import mimetypes

# Import compression algorithm modules
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress
from burrowswheeler.burrowswheeler import compress as bwt_compress, decompress as bwt_decompress
from jpeg_2000.jpeg2000 import compress_image, decompress_image
from pyflacaudio.Pyflac import compress_audio, decompress_audio

class CompressionHandler:
    """
    Class to handle all compression-related operations.
    Provides a unified interface for different compression algorithms.
    """

    ALGORITHMS = {
        "text": {
            "deflate": "Deflate Algorithm",
            "huffman": "Huffman Coding", 
            "lzw": "LZW Compression",
            "bwt": "Burrows-Wheeler Transform"
        },
        "image": {
            "jpeg2000": "JPEG2000 Image Compression"
        },
        "audio": {
            "flac": "FLAC Audio Compression"
        }
    }

    # File extensions mapping
    FILE_TYPES = {
        "text": [".txt", ".csv", ".log", ".md", ".py", ".js", ".html", ".css", ".json", ".xml"],
        "image": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"],
        "audio": [".wav", ".mp3", ".aac", ".flac", ".ogg"]
    }

    def __init__(self):
        self.source_file = None
        self.destination_file = None
        self.algorithm = None
        self.file_type = None
        self.compression_time = 0
        self.compression_ratio = 0

    def set_source_file(self, file_path):
        """Set the source file to compress/decompress"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        self.source_file = file_path
        self.file_type = self.detect_file_type(file_path)

    def set_destination_file(self, file_path):
        """Set the destination file for the compression/decompression result"""
        self.destination_file = file_path

    def set_algorithm(self, algorithm):
        """Set the compression algorithm to use"""
        # Check if the algorithm is valid for any file type
        valid_algorithm = False
        for file_type, algorithms in self.ALGORITHMS.items():
            if algorithm in algorithms:
                valid_algorithm = True
                break
        
        if not valid_algorithm:
            available_algorithms = []
            for algorithms in self.ALGORITHMS.values():
                available_algorithms.extend(algorithms.keys())
            raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {available_algorithms}")
        
        self.algorithm = algorithm

    def compress(self):
        """Compress the source file using the selected algorithm"""
        if not self.source_file or not self.destination_file or not self.algorithm:
            raise ValueError("Source file, destination file, and algorithm must be set before compression")

        start_time = time.time()

        # Text compression algorithms
        if self.algorithm == "deflate":
            deflate_compress(self.source_file, self.destination_file)
        elif self.algorithm == "huffman":
            huffman_coder = HuffmanCoding(self.source_file)
            output_path = huffman_coder.compress()
            # Copy the compressed file to the destination
            with open(output_path, 'rb') as f_in, open(self.destination_file, 'wb') as f_out:
                f_out.write(f_in.read())
            # Delete the temporary file created by HuffmanCoding
            if os.path.exists(output_path):
                os.remove(output_path)
        elif self.algorithm == "lzw":
            lzw_compress(self.source_file, self.destination_file)
        elif self.algorithm == "bwt":
            bwt_compress(self.source_file, self.destination_file)
        # Image compression algorithms
        elif self.algorithm == "jpeg2000":
            compress_image(self.source_file, self.destination_file)
        # Audio compression algorithms
        elif self.algorithm == "flac":
            compress_audio(self.source_file, self.destination_file)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        self.compression_time = time.time() - start_time
        self._calculate_compression_ratio()

        return {
            "original_size": os.path.getsize(self.source_file),
            "compressed_size": os.path.getsize(self.destination_file),
            "ratio": self.compression_ratio,
            "time": self.compression_time
        }

    def decompress(self):
        """Decompress the source file using the selected algorithm"""
        if not self.source_file or not self.destination_file or not self.algorithm:
            raise ValueError("Source file, destination file, and algorithm must be set before decompression")

        start_time = time.time()

        # Text decompression algorithms
        if self.algorithm == "deflate":
            deflate_decompress(self.source_file, self.destination_file)
        elif self.algorithm == "huffman":
            huffman_coder = HuffmanCoding(self.source_file)
            output_path = huffman_coder.decompress(self.source_file)
            # Copy the decompressed file to the destination
            with open(output_path, 'rb') as f_in, open(self.destination_file, 'wb') as f_out:
                f_out.write(f_in.read())
            # Delete the temporary file created by HuffmanCoding
            if os.path.exists(output_path):
                os.remove(output_path)
        elif self.algorithm == "lzw":
            lzw_decompress(self.source_file, self.destination_file)
        elif self.algorithm == "bwt":
            bwt_decompress(self.source_file, self.destination_file)
        # Image decompression algorithms
        elif self.algorithm == "jpeg2000":
            decompress_image(self.source_file, self.destination_file)
        # Audio decompression algorithms
        elif self.algorithm == "flac":
            decompress_audio(self.source_file, self.destination_file)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        decompression_time = time.time() - start_time

        return {
            "compressed_size": os.path.getsize(self.source_file),
            "decompressed_size": os.path.getsize(self.destination_file),
            "time": decompression_time
        }

    def get_available_algorithms(self, file_type=None):
        """
        Return a list of available compression algorithms.
        
        Args:
            file_type (str, optional): If provided, filter algorithms for this file type.
            
        Returns:
            list: List of algorithm names if file_type is provided,
                Dictionary of all algorithms by file type otherwise.
        """
        if file_type:
            if file_type in self.ALGORITHMS:
                return list(self.ALGORITHMS[file_type].keys())
            else:
                return []
        
        # If no file_type is specified, return all algorithms
        all_algorithms = []
        for algorithms in self.ALGORITHMS.values():
            all_algorithms.extend(algorithms.keys())
        return all_algorithms

    def get_algorithm_description(self, algorithm):
        """Return the description of a specific algorithm"""
        for file_type, algorithms in self.ALGORITHMS.items():
            if algorithm in algorithms:
                return algorithms[algorithm]
        return "Unknown algorithm"

    def detect_file_type(self, file_path):
        """
        Detect the type of file based on its extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Detected file type ('text', 'image', 'audio') or 'text' as default
        """
        _, ext = os.path.splitext(file_path.lower())
        
        for file_type, extensions in self.FILE_TYPES.items():
            if ext in extensions:
                return file_type
        
        # Default to text if we can't determine the type
        return "text"

    def get_file_types(self):
        """Return all supported file types"""
        return list(self.FILE_TYPES.keys())

    def _calculate_compression_ratio(self):
        """Calculate the compression ratio after compression"""
        if not os.path.exists(self.destination_file):
            return

        original_size = os.path.getsize(self.source_file)
        compressed_size = os.path.getsize(self.destination_file)

        if original_size == 0:
            self.compression_ratio = 0
        else:
            self.compression_ratio = (1 - (compressed_size / original_size)) * 100

    def process(self, algorithm, mode, input_file, output_file):
        """
        Process a file using the specified algorithm and mode.

        Args:
            algorithm (str): The compression algorithm to use
            mode (str): Either 'compress' or 'decompress'
            input_file (str): Path to the input file
            output_file (str): Path to the output file

        Returns:
            dict: Information about the compression/decompression process
        """
        self.set_source_file(input_file)
        self.set_destination_file(output_file)
        self.set_algorithm(algorithm)

        if mode.lower() == 'compress':
            return self.compress()
        elif mode.lower() == 'decompress':
            return self.decompress()
        else:
            raise ValueError(f"Unsupported mode: {mode}. Use 'compress' or 'decompress'")

    def suggest_algorithm(self, file_path):
        """
        Suggest an appropriate compression algorithm based on the file type.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Suggested algorithm name
        """
        file_type = self.detect_file_type(file_path)
        
        if file_type in self.ALGORITHMS and self.ALGORITHMS[file_type]:
            # Return the first algorithm for this file type
            return next(iter(self.ALGORITHMS[file_type]))
        
        # Default to deflate if no appropriate algorithm is foun


