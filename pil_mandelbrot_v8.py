from PIL import Image
#from PIL.ImageDraw import Draw
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
	if in_cardioid_or_bulb(x,y): return

	c = complex(x,y)
	#if C_PW < 0 and c == 0+0j: return 		# ENABLE ONLY FOR INVERSE MANDELBROTS
	z = INITIAL_Z

	for i in range(iters):
		z = z**POWER + c**C_PW
		z_mod = abs(z)

		if z_mod > ESCAPE_RADIUS:	# if c makes z escape, redo the loop and keep track of the z's
			c = complex(x,y)
			z = INITIAL_Z

			for _ in range(i+1):
				z = z**POWER + c**C_PW
				add_orbit(z)

			break


# colour shit:
VALUE_RANGE		= 255
#INVERT_COLOUR 	= True
MIN_COLOUR 		= 0
MAX_COLOUR 		= 350

# changeable constants:
POWER			= 2
C_PW 			= 1
ESCAPE_RADIUS	= 5				# default: 10
INITIAL_Z		= complex(0,0)
SHOW_PROGRESS 	= True 		# ONLY ENABLE THIS DURING LARGER RENDERS! Slows down the program considerably when it's loading fast
iters 			= 50000
#VALUE_LIMIT 	= 

# actual graph shit:
WIDTH,HEIGHT= 800,600
graph_width	= 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

mandel_img	= Image.new("L", (WIDTH,HEIGHT))
#draw 		= Draw(mandel_img)
pix 		= mandel_img.load()
max_value 	= 0

while 1:
	print("Loading...", end="", flush=True)
	pixel_values= [[0 for y in range(HEIGHT)] for x in range(WIDTH)]
	start_time = time()

	for pil_x in range(WIDTH):
		graph_x = topleft[0] + (pil_x/WIDTH)  * graph_width
		for pil_y in range(HEIGHT):
			graph_y = topleft[1] - (pil_y/HEIGHT) * graph_height

			iterate(graph_x, graph_y)

		if SHOW_PROGRESS:
			percent = round((pil_x+1)/WIDTH * 100, 1)
			digit_b	= "\b" * ( int(ln(percent,10)) + 1)
			print(f" {percent}%\b\b\b\b{digit_b}", end="", flush=True)

	if max_value > MAX_COLOUR: max_value = MAX_COLOUR
	for pil_x in range(WIDTH):
		for pil_y in range(HEIGHT):
			#draw.point((pil_x,pil_y), int(pixel_values[pil_x][pil_y]/max_value * VALUE_RANGE))
			pix[pil_x,pil_y] = MIN_COLOUR + int(pixel_values[pil_x][pil_y]/max_value * (VALUE_RANGE-MIN_COLOUR))

	elapsed = time() - start_time
	mandel_img.save(f"mandelpilv8 i{iters} ER{ESCAPE_RADIUS} c{MIN_COLOUR}to{VALUE_RANGE},m{MAX_COLOUR} p{POWER},{C_PW} z{INITIAL_Z} tl{topleft} w{graph_width} {graph_height} W{WIDTH}xH{HEIGHT}.png")
	print(f"\nDone! Took {elapsed} seconds. Max value was {max_value}.", flush=True)

	while 1:
		old_graph_width = graph_width

		topleft = ( float(input("\nTopleft x: ")), float(input("Topleft y: ")) )
		graph_width = float(input("Width of graph: "))
		graph_height= get_graph_height(graph_width)

		iters = int(input("New iters: "))
		break
