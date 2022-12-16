from PIL import Image
from math import log as ln
from time import time
from itertools import permutations

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


def escape_time(i): return int((i%ET_COLOURS)/ET_COLOURS * RGB_RANGE)

def fractional_iteration(i, z_mod):
	i -= ln(ln(z_mod), POWER)
	return round((i%FI_COLOURS)/FI_COLOURS * RGB_RANGE)

def distance_estimation(abs_z, abs_dz, escaped):
	if abs_z==0: return 0
	
	dis 	= (abs_z * ln(abs_z))/abs_dz
	frac 	= dis * DE_MULTIPLY
	
	if escaped:
		frac 	= frac%MOD_BY * 2
		shade 	= int(frac * RGB_RANGE) if frac<1 else RGB_RANGE-int( (frac-1) * RGB_RANGE)
		return shade

	frac 		= frac%1 * 2
	shade 		= int(frac * MAX_RGB )  if frac<1 else MAX_RGB - int( (frac-1) * MAX_RGB)
	return shade

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	c = complex(x,y)
	if C_PW < 0 and c == 0+0j: return (0, 0, distance_estimation(0,0,False))		# ENABLE ONLY FOR INVERSE MANDELBROTS
	z = INITIAL_Z
	dzBYdc = 0+0j

	for i in range(iters):
		dzBYdc = POWER * (z**P_MINUS_1) * dzBYdc + C_PW * c**C_P_MINUS_1
		z = z**POWER + c**C_PW

		z_mod = abs(z)
		if z_mod > ESCAPE_LIMIT: return ( escape_time(i), fractional_iteration(i,z_mod), distance_estimation(z_mod,abs(dzBYdc),True) )
	else:
		return (0, 0, distance_estimation(z_mod,abs(dzBYdc),False))


# colour shit:
RGB_RANGE 	= 256
RGB_MINUS_1 = RGB_RANGE-1
MAX_RGB 	= RGB_RANGE
ET_COLOURS 	= 32
FI_COLOURS 	= 27
DE_MULTIPLY	= 3					# doesn't limit to this many colours, just decreases radius of outside rings
MOD_BY 		= 1					# 1 for 0 to 1 and back to 0; 0.5 for 0 to 1 jump to 0
NO_OF_PERM 	= 6	# 3!

# changeable constants:
POWER		= 3
P_MINUS_1 	= POWER-1
C_PW 		= -1
C_P_MINUS_1 = C_PW - 1
ESCAPE_LIMIT= 1e21 				# default: 10
INITIAL_Z	= complex(0,0)
SHOW_PROGRESS = True 		# ONLY ENABLE THIS DURING LARGER RENDERS! Slows down the program considerably when it's loading fast

# iteration shit:
SENSITIVITY = 2
iters 		= 100
SCALE_ITERS = False	# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 200,150			# default: 800 by 600
graph_width	= 7 				# default: 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

img_list 	= [Image.new("RGB", (WIDTH,HEIGHT)) for p in range(NO_OF_PERM)]
pix_list 	= [img.load() for img in img_list]

while 1:
	print("Loading...", end="", flush=True)
	start_time = time()
	
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			colour_permutations = tuple(permutations( get_colour(graph_x,graph_y) ))
			for index in range(NO_OF_PERM): pix_list[index][pil_x,pil_y] = colour_permutations[index]

		if SHOW_PROGRESS:
			percent = round((pil_x+1)/WIDTH * 100, 1)
			digit_b	= "\b" * ( int(ln(percent,10)) + 1)
			print(f" {percent}%\b\b\b\b{digit_b}", end="", flush=True)

	elapsed = time() - start_time
	print(f"\nDone! Took {elapsed} seconds.", flush=True)
	
	for index,img in enumerate(img_list): img.save(f"mandelpil_v6 img{index} p{POWER},{C_PW} c{ET_COLOURS},{FI_COLOURS},{DE_MULTIPLY} el{ESCAPE_LIMIT} z{INITIAL_Z} i{iters}, {topleft} w{graph_width} h{graph_height}.png")

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
