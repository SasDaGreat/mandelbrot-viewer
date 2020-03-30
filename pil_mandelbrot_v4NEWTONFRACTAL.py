from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageColor import getrgb
from math import log as ln
from time import time
from cmath import sin,cos,phase,pi,cosh,sinh
from math import isnan

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

def get_hue(i):	return ((i%COLOURS)/COLOURS)*HUE_RANGE if INV_HUE_OFF else (1-(i%COLOURS)/COLOURS)*HUE_RANGE

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	#if c == 0+0j: return getrgb(f"hsv({get_hue(0)},100%,80%)") 		# ENABLE ONLY WHEN GENERATING INVERSE MANDELBROTS
	z = INITIAL_Z

	for i in range(iters):
		try:
			z -= sin(z) * cos(z) - c * cos(z)**2
			z_mod = abs(z)
		except:
			return getrgb(f"hsv({get_hue(i)},100%,100%)")
		
		if z_mod > ESCAPE_LIMIT: return getrgb(f"hsv({(phase(z)+pi) * RAD_TO_DEG},100%,100%)") if COLOUR_OUT else getrgb(f"hsv({get_hue( i )},100%,100%)")
	else:
		try:
			return getrgb(f"hsv({(phase(z)+pi) * RAD_TO_DEG},100%,100%)") if COLOUR_SET else MANDEL_COLOUR
		except:
			return (255,0,0)


# colour shit:
HUE_RANGE   = 360
COLOURS 	= 50				# doesn't limit to this many colours, just increases "thickness" of each smooth colour band
MANDEL_COLOUR = (  0,  0,  0)	# black
RAD_TO_DEG 	= 180/pi
COLOUR_SET 	= True
COLOUR_OUT 	= False

# changeable constants:
POWER		= 2
ESCAPE_LIMIT= 1e12				# default: 10
INITIAL_Z	= complex(0,0)
INV_HUE_OFF	= True
SHOW_PROGRESS = True 		# ONLY ENABLE THIS DURING LARGER RENDERS! Slows down the program considerably when it's loading fast
EQN 		= "arctanz"

# iteration shit:
SENSITIVITY = 2
iters 		= 900
SCALE_ITERS = False	# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5
 	
# actual graph shit:
WIDTH,HEIGHT= 1920,1080
graph_width	= 0.17842097244858768
graph_height= get_graph_height(graph_width)
topleft		= (-1.317002406296134, 1.0723862635254862)

mandel_img	= Image.new("RGB", (WIDTH,HEIGHT))
drawer 		= Draw(mandel_img)

while 1:
	print("Loading...", end="", flush=True)
	start_time = time()

	for pil_x in range(WIDTH):
		graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
		for pil_y in range(HEIGHT):
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			drawer.point( (pil_x,pil_y), get_colour(graph_x,graph_y) )

		
		if SHOW_PROGRESS:
			percent = round((pil_x+1)/WIDTH * 100, 1)
			digit_b	= "\b" * ( int(ln(percent,10)) + 1)
			print(f" {percent}%\b\b\b\b{digit_b}", end="", flush=True)

	elapsed = time() - start_time
	print(f"\nDone! Took {elapsed} seconds.", flush=True)
	mandel_img.save(f"mandelpilv4NEWTONFRACTAL_{EQN}_{int(INV_HUE_OFF)}_{POWER}_{ESCAPE_LIMIT}_{INITIAL_Z}_{COLOURS}_{iters},{topleft}_{graph_width}_{graph_height}.png")

	while 1:
		old_graph_width = graph_width

		topleft = ( float(input("\nTopleft x: ")), float(input("Topleft y: ")) )
		graph_width = float(input("Width of graph: "))
		graph_height= get_graph_height(graph_width)

		if SCALE_ITERS:
			zoom += old_graph_width/graph_width - 1
			iters = int(zoom**SENSITIVITY)
		else:
			iters = int(input("New iters: "))

		break