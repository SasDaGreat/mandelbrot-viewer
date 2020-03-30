from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageColor import getrgb
from math import log as ln
from time import time

# The complicated colour representation system sortaaa failed at being impressive, so I'm just going to use the normal one :c

'''
I'll also be using a sorta more complicated iteration scaling rule,
 one which I really don't know if it'll work properly or not... oh well, least there's a flag to turn it off.
zoom is a measure of how zoomed in the graph is.
Each time the graph zooms in, the ratio of prev width to current width is taken, 1 subtracted to get decrease in width,
 and added to zoom (could also be multiplied? really dk).
iters against zoom plotted is a quadratic graph; I'll be testing different quadratics to see which one works.
current: iters = (zoom)^SENSITIVITY
UPDATE: naw, I'm not sure if this scaling system'll work, so I'll be turning off SCALE_ITERS most of the time.
'''

# Other possible features:
# - using numpy or the Decimal module to handle the math w/ higher precision and possibly speed

def normalise(i,modulus): return round(i+1 - ln(ln(modulus), POWER), 3)

def get_hue(i):	return ((i%COLOURS)/COLOURS)*HUE_RANGE

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	z = complex(x,y)

	for i in range(iters):
		z = z**POWER + c**C_PW
		
		z_mod = abs(z)
		if z_mod > ESCAPE_LIMIT: return getrgb(f"hsv({get_hue( normalise(i,z_mod) )},100%,100%)")
	else:
		return MANDEL_COLOUR


# colour shit:
HUE_RANGE   = 360
COLOURS 	= 50				# doesn't limit to this many colours, however, because of fractional iteration
MANDEL_COLOUR	= (  0,  0,  0)	# black

# changeable constants:
SCALE 		= 1/0.05				# 1/STEP
POWER 		= 2
C_PW 		= 1
ESCAPE_LIMIT= 1e12				# default: 10
INV_HUE_OFF	= True
PATH 		= "600x600 (-2,1.5) 4width 0.1step 80iter 1e12ER 50C v4 temp\\"

# iteration shit:
iters = 80

# actual graph shit:
WIDTH,HEIGHT= 600,600
graph_width	= 4
graph_height= get_graph_height(graph_width)
half_width, half_height = graph_width/2, graph_height/2
topleft		= (-half_width, half_height)

X_MIN,X_MAX = -5,195
Y_MIN,Y_MAX = int(-half_height* SCALE), int(half_height* SCALE)

mandel_img	= Image.new("RGB", (WIDTH,HEIGHT))
drawer 		= Draw(mandel_img)

for c_x in range(X_MIN, X_MAX+1, 10):
	c_x /= 100
	x_start_time = time()

	for c_y in range(Y_MIN, Y_MAX+1):
		c_y /= SCALE
		c = complex(c_x, c_y)
		y_start_time = time()

		for pil_x in range(WIDTH):
			for pil_y in range(HEIGHT):
				graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
				graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

				drawer.point( (pil_x,pil_y), get_colour(graph_x,graph_y) )

		elapsed = time() - y_start_time
		print(f"{c}: y = {c_y} out of {Y_MAX/SCALE},\t\ttook {elapsed} seconds.")
		mandel_img.save(f"{PATH}{c}.jpg")

	elapsed = time() - x_start_time
	print(f"x = {c_x} out of {X_MAX/SCALE},\t\ttook {elapsed} seconds.\n")
