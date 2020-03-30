from PIL import Image
from math import log as ln
from time import time
from random import random

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
# - colours: grayscale, black to red, nebulabread, antibuddhabread
# - buddhabrot class that stores values for each pixel as well as a MAX_PIXEL_VALUE counter to divide all the pixel counters by;
#    also a temporary store of pixel increment values that can be added or not added if the pixel doesn't escape (anitBuddhabrot)
# - test whether pix[] or draw.point is better 

def in_cardioid_or_bulb(x,y):
	if POWER == 2:
		y_sq = y**2
		q = (x-0.25)**2 + y_sq
		if 0.25 * y_sq >= q*(q + (x-0.25)) or (x+1)**2 + y_sq <= 0.0625: return True

	return False

def add_orbit(z):
	global max_value
	pil_x = round((z.real - topleft[0])/graph_width * WIDTH)
	pil_y = round((topleft[1] - z.imag)/graph_height* HEIGHT)

	try:
		pixel_values[pil_x][pil_y] += 1
		if pixel_values[pil_x][pil_y] > max_value: max_value = pixel_values[pil_x][pil_y]
	except IndexError:
		pass

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def iterate(x,y):
	if not ANTIBUDDHA_ON and in_cardioid_or_bulb(x,y): return

	c = complex(x,y)
	#if C_PW < 0 and c == 0+0j: return 		# ENABLE ONLY FOR INVERSE MANDELBROTS
	z = INITIAL_Z
	z_list	= []
	escaped = False

	for i in range(iters):
		z = z**POWER + c**C_PW
		z_list.append(z)

		z_mod = abs(z)
		if z_mod > ESCAPE_RADIUS:
			escaped = True
			break

	if escaped or ANTIBUDDHA_ON:
		for old_z in z_list: add_orbit(old_z)


# colour shit:
VALUE_RANGE		= 255
MAX_COLOUR_VAL 	= 290
#INVERT_COLOUR 	= True

# changeable constants:
POWER			= 2
C_PW 			= 1
ESCAPE_RADIUS	= 5				# default: 10
INITIAL_Z		= complex(0,0)
SHOW_PROGRESS 	= True 		# ONLY ENABLE THIS DURING LARGER/ALREADY LONGER RENDERS! Slows down the program considerably
iters 			= 5000
C_ITERS 		= 1600000		# default: 1000000, or 1e6
#VALUE_LIMIT 	= 
ANTIBUDDHA_ON 	= False

# actual graph shit:
WIDTH,HEIGHT= 600,600		# NOTE!!! For buddhabrots, changing the WIDTH or HEIGHT shouldn't affect rendering time
graph_width	= 3				# BUT!!!! graph_width will
graph_height= get_graph_height(graph_width)
topleft		= (-2, graph_height/2)
C_RANGE_EXT = 0				# there's some bug with this, idk how to fix it so here it stays at 0 ig :/

mandel_img	= Image.new("L", (WIDTH,HEIGHT))
pix 		= mandel_img.load()
max_value 	= 0

while 1:
	print("Loading...", end="", flush=True)

	c_range 	= (graph_width + graph_width*C_RANGE_EXT*2, graph_height+ graph_height*C_RANGE_EXT*2) 
	c_topleft 	= (topleft[0]  - graph_width*C_RANGE_EXT, 	topleft[1] 	+ graph_height*C_RANGE_EXT)
	pixel_values= [[0 for y in range(HEIGHT)] for x in range(WIDTH)]
	start_time 	= time()

	for c_i in range(C_ITERS):
		c_x = c_topleft[0] + random() * c_range[0]
		c_y = c_topleft[1] - random() * c_range[1]
		iterate(c_x, c_y)

		if SHOW_PROGRESS:
			percent = str(round((c_i+1)/C_ITERS * 100, 2))
			digit_b	= "\b" * len(percent)
			print(f" {percent}%\b\b{digit_b}", end="", flush=True)

	if max_value > MAX_COLOUR_VAL: max_value = MAX_COLOUR_VAL
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			pix[pil_x,pil_y] = int(pixel_values[pil_x][pil_y]/max_value * VALUE_RANGE)

	elapsed = time() - start_time
	mandel_img.save(f"mandelpilv8.1 i{iters},c{C_ITERS} e{C_RANGE_EXT} ab{int(ANTIBUDDHA_ON)} ER{ESCAPE_RADIUS} c{VALUE_RANGE} m{MAX_COLOUR_VAL} p{POWER},{C_PW} z{INITIAL_Z} tl{topleft} w{graph_width} {graph_height} W{WIDTH}xH{HEIGHT}.png")
	print(f"\nDone! Took {elapsed} seconds. Max value was {max_value}.", flush=True)

	while 1:
		topleft = ( float(input("\nTopleft x: ")), float(input("Topleft y: ")) )
		graph_width = float(input("Width of graph: "))
		graph_height= get_graph_height(graph_width)

		iters = int(input("New iters: "))
		break
