from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageColor import getrgb
from math import log as ln
from time import time

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

def disn(abs_z,abs_dz, escaped):
	if abs_z==0: return (MAX_RGB, 0, 0)
	
	dis 	= (abs_z * ln(abs_z))/abs_dz
	frac 	= (dis * COLOURS)%1 * 2
	
	if escaped:
		shade = int(frac * VALUE_RANGE * 100)/100 if frac<1 else VALUE_RANGE-int((frac-1) * VALUE_RANGE * 100)/100
		return getrgb(f"hsv({FIXED_HUE},100%,{shade}%)")

	shade = MAX_RGB-int(frac * MAX_RGB) if frac<1 else int((frac-1) * MAX_RGB)
	return (MIN_RGB + shade,0,0)

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	if c == 0+0j: return disn(0,0,False) 		# ENABLE ONLY WHEN GENERATING INVERSE MANDELBROTS
	z = INITIAL_Z
	dzBYdc = 0+0j

	for i in range(iters):
		dzBYdc = POWER * (z**P_MINUS_1) * dzBYdc + C_PW * c**C_P_MINUS_1
		z = z**POWER + c**C_PW

		z_mod = abs(z)
		if z_mod > ESCAPE_LIMIT: return disn( z_mod, abs(dzBYdc), True )
	else:
		return disn( z_mod, abs(dzBYdc), False )


# colour shit:
VALUE_RANGE = 87
RGB_RANGE 	= 256
RGB_MINUS_1 = RGB_RANGE-1
MAX_RGB 	= 110
MIN_RGB 	= 30
COLOURS 	= 4					# doesn't limit to this many colours, just decreases radius of outside rings
FIXED_HUE 	= 0

# changeable constants:
POWER		= 2
P_MINUS_1 	= POWER-1
C_PW 		= 1
C_P_MINUS_1 = C_PW - 1
ESCAPE_LIMIT= 1e12 				# default: 10
INITIAL_Z	= complex(0,0)
SHOW_PROGRESS = True 		# ONLY ENABLE THIS DURING LARGER RENDERS! Slows down the program considerably when it's loading fast

# iteration shit:
SENSITIVITY = 2
iters 		= 500
SCALE_ITERS = False	# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 1366,768			# default: 800 by 600
graph_width	= 4 				# default: 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

mandel_img	= Image.new("RGB", (WIDTH,HEIGHT))
drawer 		= Draw(mandel_img)

while 1:
	print("Loading...", end="", flush=True)
	start_time = time()
	
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			drawer.point( (pil_x,pil_y), get_colour(graph_x,graph_y) )

		
		if SHOW_PROGRESS:
			percent = round((pil_x+1)/WIDTH * 100, 1)
			digit_b	= "\b" * ( int(ln(percent,10)) + 1)
			print(f" {percent}%\b\b\b\b{digit_b}", end="", flush=True)

	elapsed = time() - start_time
	print(f"\nDone! Took {elapsed} seconds.", flush=True)
	mandel_img.save(f"mandelpilv5.1BG_{FIXED_HUE}_{MAX_RGB}_{VALUE_RANGE}_{POWER}_{C_PW}_{ESCAPE_LIMIT}_{INITIAL_Z}_{COLOURS}_{iters},{topleft}_{graph_width}_{graph_height}.png")

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
