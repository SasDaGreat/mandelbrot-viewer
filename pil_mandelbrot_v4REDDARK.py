from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageColor import getrgb
from math import log as ln

# The complicated colour representation system sortaaa failed at being impressive, so I'm just going to use the normal one :c

# I'll also be using a sorta more complicated iteration scaling rule,
#one which I really don't know if it'll work properly or not... oh well, least there's a flag to turn it off.
# zoom is a measure of how zoomed in the graph is.
# Each time the graph zooms in, the ratio of prev width to current width is taken, 1 subtracted to get decrease in width,
#and added to zoom (could also be multiplied? really dk).
# iters against zoom is a quadratic graph; I'll be testing different quadratics to see which one works.
# current: iters = (zoom)^SENSITIVITY

# Other possible features:
# - using numpy or the Decimal module to handle the math w/ higher precision and possibly speed

def normalise(i,modulus): return round(i - ln( ln(modulus) )/LN_P, 3)

def get_hsv(i):
	hue = ((i%COLOURS)/COLOURS)*HUE_RANGE if INV_HUE_OFF else (1-(i%COLOURS)/COLOURS)*HUE_RANGE
	closeness_to_red = MAX_LRED_DISN-hue if hue < MAX_LRED_DISN else hue-MAX_RRED_DISN if hue > MAX_RRED_DISN else 0
	value = 100 - closeness_to_red/MAX_LRED_DISN * MAX_VALUE_DEC
	return getrgb(f"hsv({hue},100%,{value}%)")

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	z = INITIAL_Z

	for i in range(iters):
		z = z**POWER + c
		z_mod = abs(z)
		if z_mod > ESCAPE_LIMIT: return get_hsv(normalise(i, z_mod))
	else:
		return MANDEL_COLOUR


# colour shit:
MANDEL_COLOUR	= (  0,  0,  0)	# black
HUE_RANGE    	= 360
COLOURS 	 	= 60
INV_HUE_OFF	 	= True
MAX_LRED_DISN 	= 60*1			# max is 360/2, or 180. Difference betn this and the next constant is that this is left distance
MAX_RRED_DISN 	= HUE_RANGE - MAX_LRED_DISN
MAX_VALUE_DEC 	= 30			# maximum decrease in value possible in the HSV format

# changeable constants:
POWER		= 2
LN_P 		= ln(POWER)
ESCAPE_LIMIT= 10
INITIAL_Z	= complex(0,0)

# iteration shit:
SENSITIVITY = 2
iters = 120
scale_iter_limit = False		# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 800,600
graph_width	= 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

mandel_img	= Image.new("RGB", (WIDTH,HEIGHT))
drawer 		= Draw(mandel_img)


while 1:
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			drawer.point( (pil_x,pil_y), get_colour(graph_x,graph_y) ) 

	mandel_img.save(f"mandelpilv4REDDARK_{MAX_LRED_DISN}_{MAX_VALUE_DEC}_{int(INV_HUE_OFF)}_{POWER}_{ESCAPE_LIMIT}_{INITIAL_Z}_{COLOURS}_{iters},{topleft}_{graph_width}_{graph_height}.png")

	while 1:
		old_graph_width = graph_width

		topleft = ( float(input("Topleft x: ")), float(input("Topleft y: ")) )
		graph_width = float(input("Width of graph: "))
		graph_height= get_graph_height(graph_width)

		if scale_iter_limit:
			zoom += old_graph_width/graph_width - 1
			iters = int(zoom**SENSITIVITY)
		else:
			iters = int(input("New iters: "))

		break
