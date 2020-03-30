from PIL import Image

while 1:
	filename= input("Filename: ")
	src 	= Image.open(filename).convert("L")
	src_pix = src.load()
	img 	= Image.new("HSV",src.size)
	pix 	= img.load()

	for x in range(src.size[0]):
		for y in range(src.size[1]):
			pix[x,y] = (src_pix[x,y], 255, 255)

	img.convert("RGB").save(f"H, {filename}")
