from PIL import Image

# in an actual project, I'd have these constants defined in a separate .py file
L 		= 100
D 		= 130
BLACK 	= (0,0,0)
WHITE 	= (255,255,255)
RED 	= (255,0,0)
GREEN 	= (0,255,0)
BLUE 	= (0,0,255)
ORANGE 	= (255,L,0)
L_RED 	= (255,L,L)
D_RED 	= (D,0,0)
L_GREEN	= (L,255,L)
D_GREEN	= (0,D,0)
L_BLUE 	= (0,L,255)
D_BLUE 	= (0,0,D)

H_RED 	= 0
H_GREEN = 85
H_BLUE 	= 170
VALUE_DEC = 50

img = Image.open("mandelpilv4BG_BR,(0, 0, 0)_1_2_10_0j_65_6000,(-2.0, 1.1244509516837482)_4_2.2489019033674964.png").convert("HSV")
pix = img.load()
WIDTH,HEIGHT = img.size
HUE 	= H_GREEN
REPLACE = H_RED

for x in range(WIDTH):
	for y in range(HEIGHT):
		current_hsv = pix[x,y]
		if current_hsv[0] == REPLACE and current_hsv[2] > 0: pix[x,y] = (HUE, current_hsv[1], current_hsv[2]-VALUE_DEC)

img.convert("RGB").save(f"mandelpilv4BG_{HUE}-W,B DEC_VAL_{VALUE_DEC}.png")
