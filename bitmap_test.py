# from random import randrange
#
# from PIL import Image
# from itypes import List
#
#
# # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
# img = Image.new("1", (7, 48))  # create a new black image
# pixels = img.load()  # create the pixel map
#
# for i in range(img.size[0]):  # for every col:
#     for j in range(img.size[1]):  # For every row
#         pixels[i, j] = randrange(0, 2)  # set the colour accordingly
#
#
# print(img)
# img.tobitmap(name="img")
# img.show()
# img_bytes = img.tobytes()
#
# print(type(img_bytes))
# print(img_bytes)
from typing import List

from PIL import Image


# def create_bitmap_bytes(bytes_array: list[int]) -> bytes:
#     bitmap = Image.new("1", (1, 48))
#     pixel_map = bitmap.load()
#
#     for i in range(bitmap.size[1]):
#         pixel_map[0, i] = bytes_array[i]
#
#     return bitmap.tobytes()
#
#
# print(create_bitmap_bytes([0] * 48))
#
#
# def generate_random_bytes_array():
#     arr = []
#     for count in range(48):
#         arr.append(randrange(0, 2))
#     return arr
#
# print(generate_random_bytes_array())
#
# 0 - 검정색
def create_bitmap_bytes(bytes_array: List[List[int]]) -> bytes:
    bitmap = Image.new("1", (7, 48))
    pixel_map = bitmap.load()

    for i in range(bitmap.size[0]):
        for j in range(bitmap.size[1]):
            pixel_map[i, j] = bytes_array[i][j]

    # bitmap.tobitmap(name="img.png")
    # bitmap.show()
    print(type(bitmap))
    print(bitmap.tobytes())
    return bitmap.tobitmap()

print(create_bitmap_bytes([[0] * 48, [0] * 48, [0] * 48, [0] * 48, [0] * 48, [0] * 48, [0] * 48]))
