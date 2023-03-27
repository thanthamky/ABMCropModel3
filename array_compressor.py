import numpy as np
import gzip
import base64
import sys

# Compress a numpy array into a short string
def compress_array(array):
    compressed_data = gzip.compress(array.tobytes())
    print(type(compressed_data))
    print(sys.getsizeof(compressed_data))
    encoded_data = base64.b64encode(compressed_data)
    return encoded_data.decode('utf-8')

# Compress a numpy array into a short string
def compress_array_noencode(array):
    return gzip.compress(array.tobytes())

# Decompress a short string back to a numpy array with the original shape
def decompress_array(encoded_data, dtype, shape):
    compressed_data = base64.b64decode(encoded_data.encode('utf-8'))
    decompressed_data = gzip.decompress(compressed_data)
    return np.frombuffer(decompressed_data, dtype=dtype).reshape(shape)

# Decompress a short string back to a numpy array with the original shape
def decompress_array_nodecode(compressed_data, dtype, shape):
    decompressed_data = gzip.decompress(compressed_data)
    return np.frombuffer(decompressed_data, dtype=dtype).reshape(shape)