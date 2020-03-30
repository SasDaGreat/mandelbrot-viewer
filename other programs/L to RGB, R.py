from PIL import Image

while 1:
	filename= input("Filename: ")
	src 	= Image.open(filename).convert("L").convert("RGB")
	pix 	= src.load()

	for x in range(src.size[0]):
		for y in range(src.size[1]):
			pix[x,y] = (pix[x,y][0], 0, 0)

	src.save(f"R, {filename}")
