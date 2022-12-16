import sys
from os import getcwd
filenames = sys.argv[1:]
from PIL import Image

def main(filename):
	src 	= Image.open(filename).convert("L")
	src_pix = src.load()
	img 	= Image.new("HSV",src.size)
	pix 	= img.load()

	for x in range(src.size[0]):
		for y in range(src.size[1]):
			pix[x,y] = (src_pix[x,y], 255, 255)

	filename = filename.replace(getcwd(),"")
	filename = filename.replace("\\","")
	img.convert("RGB").save(f"H, {filename}")

if filenames:
	for filename in filenames:
		main(filename)

while 1:
	filename= input("Filename: ")
	main(filename)