import pickle

DICTIONARY_SIZE = 256


def lzw_compress(input_data):
    global DICTIONARY_SIZE
    dictionary = {bytes([i]): i for i in range(DICTIONARY_SIZE)}
    result = []
    temp = b""

    for byte in input_data:
        temp2 = temp + bytes([byte])
        if temp2 in dictionary:
            temp = temp2
        else:
            result.append(dictionary[temp])
            dictionary[temp2] = DICTIONARY_SIZE
            DICTIONARY_SIZE += 1
            temp = bytes([byte])

    if temp:
        result.append(dictionary[temp])

    return result


def lzw_decompress(input_data):
    global DICTIONARY_SIZE
    dictionary = {i: bytes([i]) for i in range(DICTIONARY_SIZE)}
    result = bytearray()

    previous = bytes([input_data[0]])
    result.extend(previous)
    input_data = input_data[1:]

    for code in input_data:
        if code in dictionary:
            entry = dictionary[code]
        else:
            entry = previous + previous[:1]
        result.extend(entry)
        dictionary[DICTIONARY_SIZE] = previous + entry[:1]
        DICTIONARY_SIZE += 1
        previous = entry

    return result


def write_compressed_file(path, compressed_data):
    with open(path, "wb") as output:
        pickle.dump(compressed_data, output)


def read_compressed_file(path):
    with open(path, "rb") as input:
        return pickle.load(input)


def compress_file(input_path, output_path):
    with open(input_path, "rb") as file:
        input_data = file.read()
    compressed_data = lzw_compress(input_data)
    write_compressed_file(output_path, compressed_data)


def decompress_file(input_path, output_path):
    compressed_data = read_compressed_file(input_path)
    decompressed_data = lzw_decompress(compressed_data)
    with open(output_path, "wb") as output:
        output.write(decompressed_data)
