from PIL import Image

RGB = ("R","G","B")

while 1:
	filename= input("Filename: ")
	src 	= Image.open(filename).convert("RGB")

	for i,band in enumerate(src.split()): band.convert("L").save(f"{RGB[i]} {filename}")