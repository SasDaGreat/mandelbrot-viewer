import pygame
from math import log as ln
pygame.init()

# Other possible features:
# - please just work first

def blit_c_font(text):
	font_img = c_font.render(f"c: {text}", True, FONT_COLOUR)
	font_rect= font_img.get_rect()
	font_rect.center = int(WIDTH//2), int(1.5*FONT_SIZE)

	screen.blit(font_img, font_rect)

def update_screen(lmb_is_clicked, mouse_pos):
	c_real, c_imag = get_graph_x(mouse_pos[0]), get_graph_y(mouse_pos[1])
	if c_real == 0: c_real = int(c_real)
	if c_imag == 0: c_imag = int(c_imag)
	c 	= complex( c_real, c_imag )
	pygame.display.set_caption(f"The Julia set of point {c}, of power {Z_POWER} Mandelbrot at 80 iterations")

	img = mandel_img if lmb_is_clicked else pygame.image.load(f"{FOLDER_NAME}\\{c}.jpg")
	cursor_colour = CURSOR_COLOUR_M if lmb_is_clicked else CURSOR_COLOUR_J

	screen.blit(img, (0,0))
	blit_c_font(c)
	pygame.draw.circle(screen, cursor_colour, mouse_pos, CURSOR_RADIUS, 0)

	pygame.display.flip()

def round_to(number, nearest):
	nearest = 1/nearest
	return round(number * nearest)/nearest

def in_cardioid_or_bulb(x,y):
	if Z_POWER == 2:
		y_sq = y**2
		q = (x-0.25)**2 + y_sq
		if 0.25 * y_sq >= q*(q + (x-0.25)) or (x+1)**2 + y_sq <= 0.0625: return True
	return False

def normalise(i,modulus): return round(i - ln(ln(modulus), Z_POWER), 3)

def get_hue(i):	return ((i%COLOURS)/COLOURS)*HUE_RANGE if INV_HUE_OFF else (1-(i%COLOURS)/COLOURS)*HUE_RANGE

def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def get_graph_x(pg_x): return round_to(topleft[0] + pg_x/WIDTH * graph_width, ROUND_TO)
def get_graph_y(pg_y): return round_to(topleft[1] - pg_y/HEIGHT* graph_height,ROUND_TO)

def get_colour(x,y):
	if in_cardioid_or_bulb(x,y): return MANDEL_COLOUR

	c = complex(x,y)
	if C_POWER < 0 and c == 0+0j: return (get_hue(0),100,80,100) 	# ENABLE ONLY FOR INVERSE MANDELBROTS
	z = INITIAL_Z

	for i in range(iters):
		z = z**Z_POWER + c**C_POWER
		z_mod = abs(z)
		if z_mod > ESCAPE_RADIUS: return (get_hue( normalise(i,z_mod) ),100,100,100)
	else:
		return MANDEL_COLOUR


# colour shit:
HUE_RANGE   = 360
COLOURS 	= 60					# doesn't limit to this many colours, however, because of fractional iteration
MANDEL_COLOUR	= ( 0, 0, 0, 100)	# black
SCREEN_BG_COLOUR= (100,100,100)
current_colour 	= pygame.Color(0,0,0)

# cursor shite:
CURSOR_RADIUS 	= 4
CURSOR_COLOUR_M = (170,170,170)
CURSOR_COLOUR_J = (255,255,255)

# changeable constants:
Z_POWER		= 2
C_POWER		= 1
ESCAPE_RADIUS = 1e9
INITIAL_Z	= complex(0,0)
INV_HUE_OFF	= True
iters 		= 100
FOLDER_NAME = "600x600 (-2,2) 4width 0.1step 80iter 1e12ER 50C v4"
ROUND_TO 	= 0.1

# actual graph shit:
WIDTH,HEIGHT 	= 600,600								# default: 800,600
graph_width		= 4										# default: 4
graph_height 	= get_graph_height(graph_width)			# default: (calculated from graph_width)
topleft 		= (-graph_width/2, graph_height/2)		# default: (-graph_width/2, graph_height/2)

# iter font shit:
FONT_SIZE 	= min(WIDTH//30, HEIGHT//30)
c_font 		= pygame.font.SysFont("Corbel",FONT_SIZE)		# other good fonts: Corbel
FONT_COLOUR = (0,0,240)

pygame.event.set_blocked(None)		# block all events from entering the queue
pygame.event.set_allowed(pygame.QUIT)

UPDATE_THICC 	= 1
screen 			= pygame.display.set_mode((WIDTH,HEIGHT))
screen.fill(SCREEN_BG_COLOUR)
pygame.display.flip()
x_update_rect 	= pygame.Rect(0,0,UPDATE_THICC,HEIGHT)

pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations")
start_time = pygame.time.get_ticks()

for pg_x in range(WIDTH):
	graph_x = topleft[0] + (pg_x/WIDTH) * graph_width

	for pg_y in range(HEIGHT):
		graph_y = topleft[1] - (pg_y/HEIGHT) * graph_height

		current_colour.hsva = get_colour(graph_x,graph_y)
		screen.set_at( (pg_x,pg_y), current_colour )

	x_update_rect.left = pg_x
	pygame.display.update(x_update_rect)

elapsed = (pygame.time.get_ticks() - start_time)/1000
mandel_img 	= screen.copy()

pygame.mouse.set_visible(False)

print(f"\nDone! Took {elapsed} seconds.\n\nMousing over any part of the graph will display the Julia set for that coordinate.\nIf you want to switch back to the Mandelbrot set, hold the LMB!", flush=True)

while 1:
	for event in pygame.event.get(): exit() 		# only allowed event is pygame.QUIT
	
	update_screen(pygame.mouse.get_pressed()[0], pygame.mouse.get_pos())
