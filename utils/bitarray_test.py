from bitmap import BitMap
from sys import getsizeof

# def blob_to_string(bolb):

bm = BitMap(48)
# print(bm.tostring())

zero_arr = [1] * 48

zero = bytes(zero_arr)
ones = bytes([1] * 48)
print(zero)
#
# print(len(zero))
# print(ones)
# print(type(ones))
# print(zero and ones)
# print(getsizeof(zero))
# print(getsizeof(ones))
# print(getsizeof(bytearray(48)))
