from PIL import Image

# in an actual project, I'd have these constants defined in a separate .py file
L 		= 170
D 		= 70
BLACK 	= (0,0,0)
WHITE 	= (255,255,255)
RED 	= (255,0,0)
GREEN 	= (0,255,0)
BLUE 	= (0,0,255)
ORANGE 	= (255,127,0)
L_ORANGE= (255,127,L)
YELLOW 	= (255,255,0)
L_RED 	= (255,L,L)
D_RED 	= (D,0,0)
L_GREEN	= (L,255,L)
D_GREEN	= (0,D,0)
L_BLUE 	= (0,L,255)
D_BLUE 	= (0,0,D)
CUSTOM 	= (168,7,7)

filename = input("name: ")
img = Image.open(filename).convert("RGB")
pix = img.load()
WIDTH,HEIGHT = img.size
COLOUR = WHITE
REPLACE= BLACK

for x in range(WIDTH):
	for y in range(HEIGHT):
		if pix[x,y] == REPLACE: pix[x,y] = COLOUR

img.save(f"{COLOUR} {filename}.png")
