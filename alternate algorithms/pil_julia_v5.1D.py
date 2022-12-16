from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageColor import getrgb
from time import time
from decimal import getcontext,Decimal

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
# - how tf do I make Decimal run faster holy shit

class ComplexDec:
	def __init__(self,Re,Im):
		self.re, self.im = Decimal(Re), Decimal(Im)

	def mod(self):
		return (self.re*self.re + self.im*self.im).sqrt()

	def multiply_real(self,n):
		self.re *= n
		self.im *= n

	def multiply_complex(self,z):	# (a+bi)(x+yi) = (ax-by) + (ay+xb)i
		SELF_RE = self.re
		self.re = (self.re * z.re) - (self.im * z.im)
		self.im = (SELF_RE * z.im) + (z.re * self.im)

	def square(self):				# (a+bi)^2 = (a^2 - b^2) + (2ab)i
		self.re = self.re*self.re - self.im*self.im
		self.im = 2 * self.re * self.im

	def add(self,z):
		self.re += z.re
		self.im += z.im


def disn(abs_z,abs_dz, escaped):
	if abs_z==0: return  (0, 100, 0)
	if abs_dz==0: return (100,0,0)
	
	dis 	= (abs_z * abs_z.ln())/abs_dz
	frac 	= (dis * COLOURS).copy_abs()
	
	if escaped:
		if COLOUR_CAP and frac >= 1: return getrgb(f"hsv({HUE_RANGE},100%,100%)")

		frac = frac%MOD_BY * 2
		shade = int(frac * HUE_RANGE * 100)/100 if frac<1 else HUE_RANGE-int((frac-1) * HUE_RANGE * 100)/100
		return getrgb(f"hsv({shade},100%,100%)")

	# LOG HERE!
	frac = (frac%1) * 2
	shade = int( frac * MAX_RGB ) if frac<1 else MAX_RGB - int((frac-1) * MAX_RGB)
	return (shade,shade,shade)

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_colour(x,y):
	z = ComplexDec(x,y)
	#if c == 0+0j: return disn(0,0,False) 		# ENABLE ONLY WHEN GENERATING INVERSE MANDELBROTS
	dzBYdc = ComplexDec(1,0)

	for i in range(iters):
		dzBYdc.multiply_real(2); dzBYdc.multiply_complex(z)
		z.square(); z.add(c)

		z_mod = z.mod()
		if z_mod > ESCAPE_LIMIT: return disn( z_mod, dzBYdc.mod(), True )
	else:
		return disn( z_mod, dzBYdc.mod(), False )


# colour shit:
HUE_RANGE   = 360
RGB_RANGE 	= 256
RGB_MINUS_1 = RGB_RANGE-1
MAX_RGB 	= 200
COLOURS 	= 3					# doesn't limit to this many colours, just decreases radius of outside rings
COLOUR_CAP 	= False
MOD_BY 		= 1					# 1 for 0 to 1 and back to 0; 0.5 for 0 to 1 jump to 0

# changeable constants:
ESCAPE_LIMIT= 2 				# default: 10
c 			= ComplexDec(-1,0)
SHOW_PROGRESS = True 		# ONLY ENABLE THIS DURING LARGER RENDERS! Slows down the program considerably when it's loading fast
getcontext().prec = 513

# iteration shit:
SENSITIVITY = 2
iters 		= 10
SCALE_ITERS = False	# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
WIDTH,HEIGHT= 100,75			# default: 800 by 600
graph_width	= 4 				# default: 4
graph_height= get_graph_height(graph_width)
topleft		= (-graph_width/2, graph_height/2)

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
			digit_b	= "\b" * ( int(Decimal(percent).log10()) + 1)
			print(f" {percent}%\b\b\b\b{digit_b}", end="", flush=True)

	elapsed = time() - start_time
	print(f"\nDone! Took {elapsed} seconds.", flush=True)
	mandel_img.save(f"juliapilv5.1D_@{c.re}+{c.im}i_{MOD_BY}_2pw_{ESCAPE_LIMIT}_{COLOURS}_{iters},{topleft}_{graph_width}_{graph_height}.png")

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
