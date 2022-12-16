from cProfile import Profile
from pstats import Stats, SortKey

from sys import stdout, argv

import numpy as np
from math import log
from cmath import phase, pi

#import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

'''
Hover over Mandelbrot to generate corresponding Julia!
Can also set initial conditions to zoom into a part of the set, 'cept the Julia will be zoomed in too... could fix this later
Also, NO MULTIPROCESSING! Slows the program down tremendously for lower resos, as processes need to start and end on a dime'''

#personal notes:
# !could add a feature for showing progress by lowest number of iterations from all processes, updated after some INTERVAL
# if you rebuild this program, could group funcs and constants into classes. e.g. a Display class containing the display screen and screen update funcs


def printf(printstr):
	print(printstr, flush=True)
	stdout.flush()


def adios():
	pygame.quit()
	exit()


def profile_func(func, *args):
	with Profile() as prof:
		func(*args)

	stats = Stats(prof)
	stats.sort_stats(SortKey.TIME)
	stats.dump_stats(filename=f"{topleft} {graph_width} {ran_str(3)}.prof")


def ran_str(strlen=6):
	'''Generates random alphanumeric string for unique ID purposes. Chances of a collision for strlen=6 takes ~35000 files to be ~1%'''
	return "".join(choices(ascii_letters + digits, k=strlen))


def save_img(moved=False):
	'''Saves img to ./PATH_TO_IMG/, along with data to be able to produce the same image later on'''
	pic_id = ran_str()
	filename = f"{PATH_TO_IMG}{pic_id}.png"
	pygame.image.save(screen, filename)

	img = Image.open(filename)
	meta = PngInfo()
	meta.add_text("topleft", f"{topleft}")
	meta.add_text("graph_width", f"{graph_width}")
	meta.add_text("graph_height", f"{graph_height}")
	meta.add_text("id", f"{pic_id}")
	meta.add_text("iters", f"{iters}")
	meta.add_text("moved", f"{moved}")
	meta.add_text("COLOURS", f"{COLOURS}")
	meta.add_text("INV_HUE_OFF", f"{INV_HUE_OFF}")
	meta.add_text("Z_POWER", f"{Z_POWER}")
	meta.add_text("C_POWER", f"{C_POWER}")
	meta.add_text("INITIAL_Z", f"{INITIAL_Z}")
	meta.add_text("COLOUR_SET", f"{COLOUR_SET}")
	meta.add_text("ESCAPE_RADIUS", f"{ESCAPE_RADIUS}")
	meta.add_text("HUE_RANGE", f"{HUE_RANGE}")
	meta.add_text("ENABLE_TRULY_AMAZING_COLOUR_SCHEME", f"{ENABLE_TRULY_AMAZING_COLOUR_SCHEME}")
	meta.add_text("USE_LOG", f"{USE_LOG}")
	meta.add_text("extras", f"v4.2 interlaced pan")

	img.save(filename, pnginfo=meta)
	print(f"Saved as {pic_id}.png!")


def get_graph_x(pg_x, topleft_x, graph_width): return topleft_x + pg_x / WIDTH * graph_width

def get_graph_y(pg_y, topleft_y, graph_height): return topleft_y - pg_y / HEIGHT * graph_height

def get_graph_height(graph_w): return (HEIGHT / WIDTH) * graph_w


def map_rgb(r, g, b): return (r << 16) + (g << 8) + b


def hsv_to_rgb(h, s=1, v=255):
	'''code modified from colorsys for vectorisation'''
	#if s == 0.0: return v, v, v
	h *= 6
	i = h.astype(int)
	f = h - i
	p = np.full(h.shape, v * (1 - s), dtype=int)
	q = (v * (1 - s * f)).astype(int)
	t = (v * (1.0 - s * (1 - f))).astype(int)
	v = np.full(h.shape, v, dtype=int)

	for num in range(6):
		mask = ((i == 0) | (i == 6)) if (num == 0) else (i == num)

		match num:
			case 0:
				i[mask] = map_rgb(v[mask], t[mask], p[mask])
			case 1:
				i[mask] = map_rgb(q[mask], v[mask], p[mask])
			case 2:
				i[mask] = map_rgb(p[mask], v[mask], t[mask])
			case 3:
				i[mask] = map_rgb(p[mask], q[mask], v[mask])
			case 4:
				i[mask] = map_rgb(t[mask], p[mask], v[mask])
			case 5:
				i[mask] = map_rgb(v[mask], p[mask], q[mask])

	return i


def colour_from_i(div_iter_arr, div_z_arr):
	'''Maps an iterations array to RGB (0 - 255) only over divergent points'''
	norm_i_arr = div_iter_arr - (np.log2(np.log(abs(div_z_arr))) if Z_POWER == 2 else (np.log(np.log(abs(div_z_arr))) / np.log(Z_POWER)))
	if USE_LOG: np.log2(norm_i_arr, out=norm_i_arr)
	np.nan_to_num(norm_i_arr, copy=False)
	norm_hue_arr = (norm_i_arr % COLOURS) * HUE_BY_COLOURS if INV_HUE_OFF else (COLOURS - (norm_i_arr % COLOURS)) * HUE_BY_COLOURS
	return hsv_to_rgb(norm_hue_arr)


def isnt_in_cardioid_or_bulb(x, y):
	'''True if outside of main cardioid or bulb, False otherwise. Can accept both numerical and array inputs and outputs'''
	y_2 = y**2
	q = (x - 0.25)**2 + y_2
	return ((y_2 / 4) < (q * (q + x - 0.25))) & ((x + 1)**2 + y_2 > 0.0625)


def corners_in_c_or_b(width_range, height_range, topleft, graph_width, graph_height):
	'''Check if any of the corners of the update area are in the main cardioid or side bulb (whose iterations can be avoided)'''
	if graph_width > 1: return True

	topright, bottomleft, bottomright = (
		(get_graph_x(width_range[1], topleft[0], graph_width), get_graph_y(height_range[0], topleft[1], graph_height)),
		(get_graph_x(width_range[0], topleft[0], graph_width), get_graph_y(height_range[1], topleft[1], graph_height)),
		(get_graph_x(width_range[1], topleft[0], graph_width), get_graph_y(height_range[1], topleft[1], graph_height)),
		)
	return not (
		isnt_in_cardioid_or_bulb(*topleft) and
		isnt_in_cardioid_or_bulb(*topright) and
		isnt_in_cardioid_or_bulb(*bottomleft) and
		isnt_in_cardioid_or_bulb(*bottomright)
		)


def update_screen(width_range = None, height_range = None, GENERATE_BROT=True, julia_on_alpha=True):
	'''Update a specified portion of the screen. Used to be able to control whether it updated horizontally or vertically, but removed coz useless feature'''
	if width_range == None: width_range = (0, WIDTH)
	if height_range == None: height_range = (0, HEIGHT)

	optimise_cardioid = Z_POWER == 2 and C_POWER == 1 and GENERATE_BROT and INITIAL_Z == complex(0,0) and not COLOUR_SET and corners_in_c_or_b(width_range, height_range, topleft, graph_width, graph_height)

	width_diff = width_range[1] - width_range[0]
	height_diff = height_range[1] - height_range[0]

	update_surf = pygame.Surface((width_diff, height_diff))
	update_topleft = width_range[0], height_range[0]
	update_array = np.empty(update_surf.get_size(), dtype=int)


	x_range = get_graph_x(width_range[0], topleft[0], graph_width), get_graph_x(width_range[1], topleft[0], graph_width)
	y_range = get_graph_y(height_range[0], topleft[1], graph_height), get_graph_y(height_range[1], topleft[1], graph_height)


	x = np.linspace(*x_range, num=width_diff).reshape((width_diff, 1))
	y = np.linspace(*y_range, num=height_diff).reshape((1, height_diff))

	if GENERATE_BROT:
		c_arr = x + y * 1j
		z_arr = np.full(c_arr.shape, INITIAL_Z, dtype=complex)
	else:
		z_arr = x + y * 1j
		c_arr = np.full(z_arr.shape, INITIAL_Z, dtype=complex)

	iter_arr = np.zeros(c_arr.shape, dtype=int)									# logs the iters at which each point escapes. 0 = not diverged yet
	mandel_points = np.full(c_arr.shape, True, dtype=bool)
	# represents points that MIGHT be part of set. False = already diverged, True = will participate in next iteration

	if optimise_cardioid: not_in_c_or_b = isnt_in_cardioid_or_bulb(c_arr.real, c_arr.imag)

	if C_POWER < 0: mandel_points[np.where(c_arr == 0j)] = False 				# makes (0,0) diverge at 0 iters
	
	for i in range(iters):
		mask = mandel_points & not_in_c_or_b if optimise_cardioid else mandel_points			# only compute points that MIGHT be in set, not those confirmed to be
		z_arr[mask] = z_arr[mask]**Z_POWER + c_arr[mask]**C_POWER
		currently_diverged = np.greater_equal(abs(z_arr), ESCAPE_RADIUS, out=np.full(c_arr.shape, False, dtype=bool), where=mask)
		# checks where current z_arr's modulus > ER, but checks ONLY at points where mandel_points = True (not yet diverged). currently_diverged = only new divergences
		mandel_points[currently_diverged] = False 								# mandel_points cumulates all the divergences as False
		iter_arr[currently_diverged] = i
	
	#return map_hsv((phase(z) + pi) * RAD_TO_DEG) if COLOUR_SET else MANDEL_COLOUR

	anti_mandels = np.logical_not(mandel_points)
	iter_arr[anti_mandels] = colour_from_i(iter_arr[anti_mandels], z_arr[anti_mandels])
	iter_arr[mandel_points] = M_COLOUR_MAP if not COLOUR_SET else hsv_to_rgb((np.angle(z_arr[mandel_points]) + np.pi) / (2 * np.pi), s=CSET_SAT, v=CSET_VAL)

	# CAN ENABLE THIS FOR ANOTHER COLOURING SCHEME
	# iter_arr = abs(iter_arr - 2**31)
	
	if ENABLE_TRULY_AMAZING_COLOUR_SCHEME:
		# for some reason, using integer/mapped colour values for make_surface results in very wonky colours. very cool, though!
		update_surf = pygame.surfarray.make_surface(iter_arr)
	else:
		pygame.surfarray.blit_array(update_surf, iter_arr)
	
	if not GENERATE_BROT and julia_on_alpha: update_surf.set_alpha(JULIA_ALPHA)
	pygame.display.update(screen.blit(update_surf, update_topleft))


def update_pause_screen(circle_coords, lmb_held):
	global INITIAL_Z
	if not lmb_held: screen.blit(mandel_bg, (0,0))
	INITIAL_Z = complex(
		get_graph_x(circle_coords[0], topleft[0], graph_width),
		get_graph_y(circle_coords[1], topleft[1], graph_height),
		)
	update_screen(GENERATE_BROT=False, julia_on_alpha=not lmb_held)

INV_HUE_OFF = True
USE_LOG = False
COLOURS = 44											# default: 44. doesn't limit to this many colours, however, because of fractional iteration
COLOUR_SET = True
CSET_VAL = 255
CSET_SAT = 0.75
MANDEL_COLOUR = (0, 0, 0)
M_COLOUR_MAP = map_rgb(*MANDEL_COLOUR)
RAD_TO_DEG = 180 / pi


if __name__ == "__main__":
	from string import ascii_letters, digits
	from random import choices, shuffle, randint

	from PIL import Image
	from PIL.PngImagePlugin import PngInfo

	from os import environ
	environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
	import pygame
	pygame.init()

	if len(argv) > 1: 
		img = Image.open(argv[1])

		# calculation constants, needed by subprocesses
		WIDTH, HEIGHT = img.size
		Z_POWER = int(img.text["Z_POWER"])					# use float() if image had non-integer powers
		C_POWER = int(img.text["C_POWER"])					# ^
		INITIAL_Z = complex(img.text["INITIAL_Z"])
		ESCAPE_RADIUS = int(img.text["ESCAPE_RADIUS"])
		HUE_RANGE = int(img.text["HUE_RANGE"])	
		CPUS = int(img.text["CPUS"])

		# initialisation constants, needed only by main process
		iters = int(img.text["iters"])
		graph_width = float(img.text["graph_width"])
		graph_height = float(img.text["graph_height"])
		topleft = img.text["topleft"][1:-1].split(", ")
		topleft = float(topleft[0]), float(topleft[1])			
	else:
		WIDTH, HEIGHT = 300, 200							# default: 1200, 900 OR 800, 600
		Z_POWER = 2
		C_POWER = 1
		INITIAL_Z = complex(0, 0)
		ESCAPE_RADIUS = 5
		HUE_RANGE = 1

		# changeable constants/init vars:
		iters = 50
		graph_width = 4									# default: 4. NOTE!!! at ~1e-13 graph_width, precision errors start showing up. Decimals fix?
		graph_height = get_graph_height(graph_width)	# default: (calculated from graph_width). disabling might result in a stretched graph
		topleft = (-graph_width/2, graph_height/2)		# default: (-graph_width/2, graph_height/2)
	
	ENABLE_TRULY_AMAZING_COLOUR_SCHEME = False			# not available in interlaced mode due to generation technique, pensive
	AUTO_SAVE = False
	DRAW_BORDER = True

	# "constant" constants:
	MOVEMENT_SCALE = 0.1								# default: 0.1
	MOVE_W, MOVE_H = int(WIDTH * MOVEMENT_SCALE), int(HEIGHT * MOVEMENT_SCALE)
	PXDATA_TIMEOUT = 0.05		################### could tweak to see what value works best	# acts like a clock/framerate limiter
	PATH_TO_IMG = "generated imgs\\"
	ZOOM_PERCENT = 0.1
	HUE_BY_COLOURS = HUE_RANGE / COLOURS

	# reactive stuff:
	BORDER_RADIUS = max(WIDTH, HEIGHT)//40
	BORDER_THICC = int(BORDER_RADIUS*0.5)

	# colours:
	SCREEN_BG_COLOUR = (100, 100, 100)
	CIRCLE1_COLOUR = (160, 120, 120, 180)
	CIRCLE2_COLOUR = (80, 80, 120, 180)
	BG_COLOUR_MAP = map_rgb(*SCREEN_BG_COLOUR)
	JULIA_ALPHA = 180

	pygame.event.set_blocked(None)						# block all events from entering the queue
	pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL))			# "LET ME IN" - eric andre
	pygame.event.set_grab(True)							# so that the window doesn't lose focus and pause

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_icon(pygame.image.load("mandelbrot.ico"))
	pygame.display.set_caption(f"The Mandelbrot Set's Julia Sets")
	screen.fill(SCREEN_BG_COLOUR)
	pygame.display.flip()
	
	alpha_layer = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)			# used to overlay Julia
	alpha_layer.fill((0,0,0,0))	

	while 1:
		#profile_func(update_screen, (0, WIDTH), (0, HEIGHT))

		start_time = pygame.time.get_ticks()
		update_screen()
		elapsed = (pygame.time.get_ticks() - start_time) / 1000			
		pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations")

		printf(f"\nDone! Took {elapsed} seconds.\n\nNow move the mouse to where you want to generate the Julia Set. Hold left click to hide the Mandelbrot overlay.")

		mandel_bg = screen.copy()										# used to clear screen, so updated only when inputs_left changes

		if AUTO_SAVE: save_img()
		while 1:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN and event.key == pygame.K_s: save_img()

				elif event.type == pygame.MOUSEMOTION:
					update_pause_screen(event.pos, pygame.mouse.get_pressed()[0])

				elif event.type == pygame.QUIT:
					adios()
