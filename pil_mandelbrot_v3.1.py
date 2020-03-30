from PIL import Image,ImageDraw
from PIL.ImageColor import getrgb

# I'll be using a linear representation of a 2D colour space, using the H and S from the HSV system,
#to try and use as many colours from the RGB colour space as possible.
# Another reason for the more complicated colour representation is to remove the rainbow pattern
#formed when colours are modulus'd in normal Mandelbrots, but I think I might be able to simplify all this...
# NOTE: The PERFECT COLOURS_RANGE needs to be found, and it isn't as simple as it was before.
# This is because the colour space is now 2D, so even if scaled colours are far enough apart,
#they may still be close together in 2D space.
# Thus, I need to find the perfect COLOURS_RANGE that spaces the pixels as far apart periodically as possible,
#while ideally keeping the distance between colours the same throughout.
# UPDATE: naw, I instead switched to a PIXELS_TO_MOVE constant,
#which instead specifies how many pixels each iteration moves along the snaking 1D curve on the HSV plane.
# The old algorithm, ((i%COLOURS_RANGE)/COLOURS_RANGE)*ITER_LIMIT, had lotsa problems.

# I'll also be using a sorta more complicated iteration scaling rule,
#one which I really don't know if it'll work properly or not... oh well, least there's a flag to turn it off.
# zoom is a measure of how zoomed in the graph is.
# Each time the graph zooms in, the ratio of prev width to current width is taken, 1 subtracted to get decrease in width,
#and added to zoom (could also be multiplied? really dk).
# iters against zoom is a quadratic graph; I'll be testing different quadratics to see which one works.
# current: iters = (zoom)^SENSITIVITY

# Other possible features:
# - using numpy or the Decimal module to handle the math w/ higher precision and possibly speed

def scale_iters(exit_iters): return (PIXELS_TO_MOVE * exit_iters)%ITER_LIMIT

def hsv(scaled_iters):
	hue = scaled_iters//SAT_RANGE
	satn = scaled_iters % SAT_RANGE
	satn = 100-satn if hue%2==0 else (100-(SAT_RANGE-1))+satn

	return getrgb(f"hsv({hue},{satn}%,100%)")

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	z = INITIAL_Z

	for i in range(iters):
		z = z**POWER + c
		if abs(z) > ESCAPE_LIMIT: return hsv(scale_iters(i))
	else:
		return MANDEL_COLOUR


# colour shit:
#COLOURS_RANGE 	= 726.78
SAT_RANGE 		= 76
PIXELS_TO_MOVE	= ((SAT_RANGE-1)/2) + SAT_RANGE*2 	# the lesser this is, the greater the number of colours in the set will be.
HUE_RANGE   	= 360
ITER_LIMIT  	= SAT_RANGE * HUE_RANGE 			# the max no. of iterations that can have a unique colour value
MANDEL_COLOUR	= (  0,  0,  0)		# black
print(f"The number of possible colours in this set will be {ITER_LIMIT//PIXELS_TO_MOVE}.")

# changeable constants:
POWER			= 2
ESCAPE_LIMIT	= 2
INITIAL_Z		= complex(0,0)

# iteration shit:
SENSITIVITY = 2
iters = 200
scale_iter_limit = False		# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 160,90
graph_width	= 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

mandel_img	= Image.new("RGB", (WIDTH,HEIGHT))
drawer 		= ImageDraw.Draw(mandel_img)


while 1:
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			graph_x = topleft[0] + (pil_x/WIDTH) * graph_width
			graph_y = topleft[1] - (pil_y/HEIGHT)* graph_height

			drawer.point((pil_x,pil_y), get_colour(graph_x, graph_y)) 

	mandel_img.save(f"mandelpilv3.1_{POWER}_{ESCAPE_LIMIT}_{INITIAL_Z}_{PIXELS_TO_MOVE}_{SAT_RANGE}_{iters},{topleft}_{graph_width}_{graph_height}.png")

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
