import sys
from os import getcwd
filenames = sys.argv[1:]
from PIL import Image

def main(filename):
	src 	= Image.open(filename).convert("L").convert("RGB")
	pix 	= src.load()

	for x in range(src.size[0]):
		for y in range(src.size[1]):
			pix[x,y] = (pix[x,y][0], 0, 0)

	filename = filename.replace(getcwd(),"")
	filename = filename.replace("\\","")
	src.save(f"R, {filename}")

if filenames:
	for filename in filenames:
		main(filename)

while 1:
	filename= input("Filename: ")
	main(filename)