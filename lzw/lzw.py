# lzw/lzw.py
import pickle

DICTIONARY_SIZE = 256

def lzw_compress(input):
    global DICTIONARY_SIZE
    dictionary = {}
    result = []
    temp = ""

    for i in range(0, DICTIONARY_SIZE):
        dictionary[str(chr(i))] = i

    for c in input:
        temp2 = temp + str(chr(c))
        if temp2 in dictionary.keys():
            temp = temp2
        else:
            result.append(dictionary[temp])
            dictionary[temp2] = DICTIONARY_SIZE
            DICTIONARY_SIZE += 1
            temp = "" + str(chr(c))

    if temp != "":
        result.append(dictionary[temp])  
        
    return result

def lzw_decompress(input):
    global DICTIONARY_SIZE
    dictionary = {}
    result = []

    for i in range(0, DICTIONARY_SIZE):
        dictionary[i] = str(chr(i))

    previous = chr(input[0])
    input = input[1:]
    result.append(previous)

    for bit in input:
        aux = ""
        if bit in dictionary.keys():
            aux = dictionary[bit]
        else:
            aux = previous + previous[0]
        result.append(aux)
        dictionary[DICTIONARY_SIZE] = previous + aux[0]
        DICTIONARY_SIZE += 1
        previous = aux
    return result

def write_compressed_file(path, compressed_data):
    with open(path, 'wb') as output:
        pickle.dump(compressed_data, output)

def read_compressed_file(path):
    with open(path, 'rb') as input:
        return pickle.load(input)

def compress_file(input_path, output_path):
    with open(input_path, 'rb') as file:
        input_data = file.read()
    compressed_data = lzw_compress(input_data)
    write_compressed_file(output_path, compressed_data)

def decompress_file(input_path, output_path):
    compressed_data = read_compressed_file(input_path)
    decompressed_data = lzw_decompress(compressed_data)
    with open(output_path, 'w') as output:
        for data in decompressed_data:
            output.write(data)
