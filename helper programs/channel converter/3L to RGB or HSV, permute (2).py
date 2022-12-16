import sys
from os import getcwd
filenames = sys.argv[1:4]
from PIL import Image
from itertools import permutations

COMBINE_AS_RGB = True
name 	= input("Name for output images: ")
imglist = (Image.open(i).convert("L") for i in filenames) if len(filenames)==3 else (Image.open(input(f"Filename {i}: ")).convert("L") for i in range(3))

for i,rgb in enumerate(permutations(imglist)): Image.merge("RGB" if COMBINE_AS_RGB else "HSV", rgb).save(f"{name} {i}.png")