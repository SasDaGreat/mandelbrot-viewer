from PIL import Image

FOLDER_NAME	= "600x600 (-2,2) 4width 0.1step 80iter 1e12ER 50C v4"

GRAPH_LENGTH= 4
TOPLEFT 	= (-2,2)
COORD_STEP  = 0.1
NO_OF_PICS 	= int((GRAPH_LENGTH/COORD_STEP + 1))

SCALE 		= 6
LENGTH 		= int(Image.open(f"{FOLDER_NAME}\\0j.jpg").size[0]/SCALE)
FULL_LENGTH = LENGTH * NO_OF_PICS
canvas 		= Image.new("RGB", (FULL_LENGTH, FULL_LENGTH))

for pil_topleft_x in range(NO_OF_PICS):
	c_x = round(TOPLEFT[0] + pil_topleft_x/(NO_OF_PICS-1) * GRAPH_LENGTH, 1)
	pil_topleft_x *= LENGTH

	for pil_topleft_y in range(NO_OF_PICS):
		c_y = round(TOPLEFT[1] - pil_topleft_y/(NO_OF_PICS-1) * GRAPH_LENGTH, 1)
		pil_topleft_y *= LENGTH

		img = Image.open(f"{FOLDER_NAME}\\{complex(c_x,c_y)}.jpg").resize((LENGTH,LENGTH))
		canvas.paste(img, (pil_topleft_x,pil_topleft_y))

canvas.save(f"canvas l{GRAPH_LENGTH} tl{TOPLEFT} step{COORD_STEP} scale{SCALE}.png")
