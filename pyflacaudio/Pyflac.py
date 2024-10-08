import soundfile as sf
import os

def compress_audio(input_file, output_file):
    """
    Compress audio using FLAC format.

    :param input_file: Path to the input WAV file
    :param output_file: Path to save the compressed FLAC file
    """
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

    audio_data, sample_rate = sf.read(input_file)

    sf.write(output_file, audio_data, sample_rate, format='FLAC')
    print(f"Compressed '{input_file}' to '{output_file}'.")


def decompress_audio(input_file, output_file):
    """
    Decompress FLAC audio to WAV format.

    :param input_file: Path to the input FLAC file
    :param output_file: Path to save the decompressed WAV file
    """
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

    audio_data, sample_rate = sf.read(input_file)

    sf.write(output_file, audio_data, sample_rate, format='WAV')
    print(f"Decompressed '{input_file}' to '{output_file}'.")
