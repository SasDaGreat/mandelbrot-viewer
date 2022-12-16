from PIL import Image
from PIL.ImageDraw import Draw

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

def get_hue(iters): return int(((iters%COLOURS)/COLOURS)*HUE_RANGE) if INV_HUE_OFF else int((1-(iters%COLOURS)/COLOURS)*HUE_RANGE)

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	z = INITIAL_Z

	for i in range(iters):
		z = z**POWER + c
		if abs(z) > ESCAPE_LIMIT: return (get_hue(i), 255, 255)
	else:
		return MANDEL_COLOUR


# colour shit:
HUE_RANGE   = 256
COLOURS 	= 40
MANDEL_COLOUR	= (  0,  0,  0)		# black

# changeable constants:
POWER		= 2
ESCAPE_LIMIT= 2
INITIAL_Z	= complex(0,0)
INV_HUE_OFF	= True

# iteration shit:
SENSITIVITY = 2
iters = 100
scale_iter_limit = False		# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 160,90
graph_width	= 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

mandel_img	= Image.new("HSV", (WIDTH,HEIGHT))
drawer 		= Draw(mandel_img)


while 1:
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			drawer.point( (pil_x,pil_y), get_colour(graph_x,graph_y) ) 

	mandel_img.convert("RGB").save(f"mandelpilv3.2_{int(INV_HUE_OFF)}_{POWER}_{ESCAPE_LIMIT}_{INITIAL_Z}_{COLOURS}_{iters},{topleft}_{graph_width}_{graph_height}.png")

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
