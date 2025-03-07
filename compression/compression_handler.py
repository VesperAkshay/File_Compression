import os
import time
import mimetypes
import threading
import hashlib
from PyQt5.QtCore import QObject, pyqtSignal
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Import compression algorithm modules
from deflate.deflate import compress_file as deflate_compress, decompress_file as deflate_decompress
from huffman.huffman import HuffmanCoding
from lzw.lzw import compress_file as lzw_compress, decompress_file as lzw_decompress
from burrowswheeler.burrowswheeler import compress as bwt_compress, decompress as bwt_decompress
from jpeg_2000.jpeg2000 import compress_image, decompress_image
from pyflacaudio.Pyflac import compress_audio, decompress_audio

class CompressionHandler(QObject):
    """
    Class to handle all compression-related operations.
    Provides a unified interface for different compression algorithms.
    """
    progress_updated = pyqtSignal(int)
    operation_completed = pyqtSignal(dict)
    operation_failed = pyqtSignal(str)

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
        super(CompressionHandler, self).__init__()
        self.source_file = None
        self.destination_file = None
        self.algorithm = None
        self.file_type = None
        self.compression_time = None
        self.compression_ratio = None
        self.use_encryption = False
        self.encryption_password = None

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

    def set_encryption(self, use_encryption, password=None):
        """Enable or disable encryption and set the password"""
        self.use_encryption = use_encryption
        self.encryption_password = password

    def derive_key(self, password, salt=None):
        """Derive a 256-bit key from the password"""
        if salt is None:
            salt = os.urandom(16)
        # Use PBKDF2 to derive a key from the password
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        return key, salt

    def encrypt_file(self, input_file, output_file, password):
        """Encrypt a file using AES-256"""
        # Read the input file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Derive a key from the password
        key, salt = self.derive_key(password)
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Create an encryptor
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt the data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Write the salt, IV, and encrypted data to the output file
        with open(output_file, 'wb') as f:
            f.write(salt)
            f.write(iv)
            f.write(encrypted_data)

    def decrypt_file(self, input_file, output_file, password):
        """Decrypt a file using AES-256"""
        # Read the input file
        with open(input_file, 'rb') as f:
            salt = f.read(16)
            iv = f.read(16)
            encrypted_data = f.read()
        
        # Derive the key from the password and salt
        key, _ = self.derive_key(password, salt)
        
        # Create a decryptor
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        # Write the decrypted data to the output file
        with open(output_file, 'wb') as f:
            f.write(data)

    def compress(self, update_progress=None):
        """Compress the source file using the selected algorithm"""
        if not self.source_file or not self.destination_file or not self.algorithm:
            raise ValueError("Source file, destination file, and algorithm must be set before compression")

        start_time = time.time()
        
        # Emit initial progress
        if hasattr(self, 'progress_updated'):
            self.progress_updated.emit(0)

        try:
            # Get file size for progress calculation
            total_size = os.path.getsize(self.source_file)
            
            # Create a temporary file for the compressed output
            temp_output = self.destination_file + '.temp'
            
            # Text compression algorithms
            if self.algorithm == "deflate":
                # Emit progress updates during compression
                def progress_callback(bytes_processed):
                    progress = min(int((bytes_processed / total_size) * 100), 99)
                    if hasattr(self, 'progress_updated'):
                        self.progress_updated.emit(progress)
                
                deflate_compress(self.source_file, temp_output if self.use_encryption else self.destination_file, progress_callback)
            elif self.algorithm == "huffman":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(25)  # Starting
                
                huffman_coder = HuffmanCoding(self.source_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                output_path = huffman_coder.compress()
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(75)  # Almost done
                
                # Copy the compressed file to the destination
                with open(output_path, 'rb') as f_in, open(temp_output if self.use_encryption else self.destination_file, 'wb') as f_out:
                    f_out.write(f_in.read())
                # Delete the temporary file created by HuffmanCoding
                if os.path.exists(output_path):
                    os.remove(output_path)
            elif self.algorithm == "lzw":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(30)  # Starting
                
                lzw_compress(self.source_file, temp_output if self.use_encryption else self.destination_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(90)  # Almost done
            elif self.algorithm == "bwt":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(30)  # Starting
                
                bwt_compress(self.source_file, temp_output if self.use_encryption else self.destination_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(90)  # Almost done
            # Image compression algorithms
            elif self.algorithm == "jpeg2000":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                compress_image(self.source_file, temp_output if self.use_encryption else self.destination_file)
            # Audio compression algorithms
            elif self.algorithm == "flac":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                compress_audio(self.source_file, temp_output if self.use_encryption else self.destination_file)
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")

            # If encryption is enabled, encrypt the compressed file
            if self.use_encryption and self.encryption_password:
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(95)  # Almost done with encryption
                
                self.encrypt_file(temp_output, self.destination_file, self.encryption_password)
                
                # Remove the temporary file
                if os.path.exists(temp_output):
                    os.remove(temp_output)

            self.compression_time = time.time() - start_time
            self._calculate_compression_ratio()

            result = {
                "original_size": os.path.getsize(self.source_file),
                "compressed_size": os.path.getsize(self.destination_file),
                "ratio": self.compression_ratio,
                "time": self.compression_time,
                "encrypted": self.use_encryption
            }
            
            # Emit completion signal
            if hasattr(self, 'operation_completed'):
                self.operation_completed.emit(result)
                
            return result
            
        except Exception as e:
            if hasattr(self, 'operation_failed'):
                self.operation_failed.emit(str(e))
            raise e

    def decompress(self, update_progress=None):
        """Decompress the source file using the selected algorithm"""
        if not self.source_file or not self.destination_file or not self.algorithm:
            raise ValueError("Source file, destination file, and algorithm must be set before decompression")

        start_time = time.time()
        
        # Emit initial progress
        if hasattr(self, 'progress_updated'):
            self.progress_updated.emit(0)

        try:
            # If encryption is enabled, decrypt the file first
            source_file = self.source_file
            if self.use_encryption and self.encryption_password:
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(10)  # Starting decryption
                
                # Create a temporary file for the decrypted content
                temp_input = self.source_file + '.decrypted'
                self.decrypt_file(self.source_file, temp_input, self.encryption_password)
                source_file = temp_input
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(20)  # Finished decryption
            
            # Get file size for progress calculation
            total_size = os.path.getsize(source_file)
            
            # Text decompression algorithms
            if self.algorithm == "deflate":
                # Emit progress updates during decompression
                def progress_callback(bytes_processed):
                    progress = min(20 + int((bytes_processed / total_size) * 80), 99)
                    if hasattr(self, 'progress_updated'):
                        self.progress_updated.emit(progress)
                
                deflate_decompress(source_file, self.destination_file, progress_callback)
            elif self.algorithm == "huffman":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(30)  # Starting
                
                huffman_coder = HuffmanCoding(source_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                output_path = huffman_coder.decompress(source_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(75)  # Almost done
                
                # Copy the decompressed file to the destination
                with open(output_path, 'rb') as f_in, open(self.destination_file, 'wb') as f_out:
                    f_out.write(f_in.read())
                # Delete the temporary file created by HuffmanCoding
                if os.path.exists(output_path):
                    os.remove(output_path)
            elif self.algorithm == "lzw":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(30)  # Starting
                
                lzw_decompress(source_file, self.destination_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(90)  # Almost done
            elif self.algorithm == "bwt":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(30)  # Starting
                
                bwt_decompress(source_file, self.destination_file)
                
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(90)  # Almost done
            # Image decompression algorithms
            elif self.algorithm == "jpeg2000":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                decompress_image(source_file, self.destination_file)
            # Audio decompression algorithms
            elif self.algorithm == "flac":
                # Emit progress at key points
                if hasattr(self, 'progress_updated'):
                    self.progress_updated.emit(50)  # Halfway
                
                decompress_audio(source_file, self.destination_file)
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")

            # Clean up temporary files
            if self.use_encryption and source_file != self.source_file:
                if os.path.exists(source_file):
                    os.remove(source_file)

            decompression_time = time.time() - start_time

            result = {
                "compressed_size": os.path.getsize(self.source_file),
                "decompressed_size": os.path.getsize(self.destination_file),
                "time": decompression_time,
                "encrypted": self.use_encryption
            }
            
            # Emit completion signal
            if hasattr(self, 'operation_completed'):
                self.operation_completed.emit(result)
                
            return result
            
        except Exception as e:
            if hasattr(self, 'operation_failed'):
                self.operation_failed.emit(str(e))
            raise e

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

    def process(self, algorithm, mode, input_file, output_file, use_threading=True, use_encryption=False, password=None):
        """
        Process a file using the specified algorithm and mode.

        Args:
            algorithm (str): The compression algorithm to use
            mode (str): Either 'compress' or 'decompress'
            input_file (str): Path to the input file
            output_file (str): Path to the output file
            use_threading (bool): Whether to run the operation in a separate thread
            use_encryption (bool): Whether to encrypt/decrypt the file
            password (str): Password for encryption/decryption

        Returns:
            dict: Information about the compression/decompression process
        """
        self.set_source_file(input_file)
        self.set_destination_file(output_file)
        self.set_algorithm(algorithm)
        self.set_encryption(use_encryption, password)

        # Emit initial progress
        if hasattr(self, 'progress_updated'):
            self.progress_updated.emit(0)

        if use_threading:
            # Run the operation in a separate thread
            if mode.lower() == 'compress':
                thread = threading.Thread(target=self.compress)
            elif mode.lower() == 'decompress':
                thread = threading.Thread(target=self.decompress)
            else:
                raise ValueError(f"Unsupported mode: {mode}. Use 'compress' or 'decompress'")
            
            thread.daemon = True  # Thread will exit when main program exits
            thread.start()
            return None  # Results will be emitted via signals
        else:
            # Run synchronously
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

        # Default to deflate if no appropriate algorithm is found
        return "deflate"
