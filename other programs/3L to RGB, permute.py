from PIL import Image
from itertools import permutations

name 	= input("Name for output images: ")
imglist = (Image.open(input(f"Filename {i}: ")).convert("L") for i in range(3))

for i,rgb in enumerate(permutations(imglist)): Image.merge("RGB", rgb).save(f"{name} {i}.png")