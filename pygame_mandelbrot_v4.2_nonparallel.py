import pygame
from math import log as ln
from cmath import phase, pi
from colorsys import hsv_to_rgb

from string import ascii_letters, digits
from random import choices

import cProfile
import pstats

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from multiprocessing import Pool, Manager, cpu_count
from queue import Empty
from sys import stdout
#from concurrent.futures import ThreadPoolExecutor

#  for multiprocessing: could wrap update_screen in another function that inspects the area of graph to generate and splits it into chunks
# make update_screen iterative? passes new area to update after updating a line into another update_screen, so that processes can dynamically split chunks more and more as they finish; or just pass over execution in iteration only once another process finishes
# or hardcode chunks to be x lines long
# could also interlace lines! process always seeks for the next available line
# yield
# after a process finishes a line, it'll update the NEXT_LINE_X only if current NEXT_LINE_X is <= the process's x
# experiemnt with different ways of spawning new processes, and diff nums of processes? cpu-1 number of processes or more
# data to be transferred: next_update_x (global/shared), px (main process could receive info as list + x_value, and update process using pipes) (or each process could directly write to px somehow), 
# if processes can't directly write to the px array and you have to return a list to the main process, could shove the entire list thing into get_colour so that it returns the list

# remember to log which x values get updated,in case multiple processes update the same x for some reason

# pool.map_async(chunksize?)
# pygame.Clock.tick

# could still use concurrent.futures to switch betn threads and processes


# if you rebuild this program, could group funcs and constants into classes. e.g. a Display class containing the display screen and screen update funcs


def printf(printstr): print(printstr, flush=True)

def adios():
	pygame.quit()
	exit()

def profile_func(func, *args):
	with cProfile.Profile() as pr:
		func(*args)

	stats = pstats.Stats(pr)
	stats.sort_stats(pstats.SortKey.TIME)
	stats.dump_stats(filename=f"{topleft} {graph_width} {ran_str(3)}.prof")


def ran_str(strlen=6): return "".join(choices(ascii_letters + digits, k=strlen))


def save_img():
	pic_id = ran_str()
	pygame.image.save(screen, f"{PATH_TO_IMG}{pic_id}.png")

	img = Image.open(f"{PATH_TO_IMG}{pic_id}.png")
	meta = PngInfo()
	# will be used to save info about the particular image to be able to produce it later on
	meta.add_text("topleft", f"{topleft}")
	meta.add_text("graph_width", f"{graph_width}")
	meta.add_text("graph_height", f"{graph_height}")
	meta.add_text("id", f"{pic_id}")
	meta.add_text("iters", f"{iters}")
	meta.add_text("Z_POWER", f"{Z_POWER}")
	meta.add_text("C_POWER", f"{C_POWER}")
	meta.add_text("INITIAL_Z", f"{INITIAL_Z}")
	meta.add_text("ESCAPE_RADIUS", f"{ESCAPE_RADIUS}")
	meta.add_text("HUE_RANGE", f"{HUE_RANGE}")
	meta.add_text("extras", f"vanilla v4.2")
	img.save(f"{PATH_TO_IMG}{pic_id}.png", pnginfo=meta)


def get_graph_x(pg_x): return topleft[0] + pg_x / WIDTH * graph_width
def get_graph_y(pg_y): return topleft[1] - pg_y / HEIGHT * graph_height

def get_graph_height(graph_w): return (HEIGHT / WIDTH) * graph_w


def normalise(i, modulus): return round(i - ln(ln(modulus), Z_POWER), 3)


def get_hue(i): return ((i % COLOURS) / COLOURS) * HUE_RANGE if INV_HUE_OFF else (1 - (i % COLOURS) / COLOURS) * HUE_RANGE


def map_hsv(hue, sat=1, val=1):
	norm_rgb = hsv_to_rgb(hue, sat, val)
	return tuple(round(i*255) for i in norm_rgb)			# + (255,) if alpha is needed


def get_colour(x, y, iters):								# the bulk of the computation!
	if not COLOUR_SET and in_cardioid_or_bulb(x, y):		# program spends a lot of time here
		return MANDEL_COLOUR

	c = complex(x, y)
	#if C_POWER < 0 and c == 0 + 0j:						# enable only for inverse mandelbrots
	#	return (get_hue(0), 100, 80, 100)
	
	z = INITIAL_Z
	for i in range(iters):
		z = z**Z_POWER + c**C_POWER
		z_mod = abs(z)
		if z_mod > ESCAPE_RADIUS:
			return map_hsv(get_hue(normalise(i, z_mod)))
	else:
		return map_hsv((phase(z) + pi) * RAD_TO_DEG) if COLOUR_SET else MANDEL_COLOUR


def calc_line(pg_x, height_range, iters):
	y_colours = []
	graph_x = get_graph_x(pg_x)

	for pg_y in range(*height_range):
		graph_y = get_graph_y(pg_y)
		y_colours.append(get_colour(graph_x, graph_y, iters))

	y_colours.append(pg_x)
	return y_colours


def update_screen(width_range, height_range):
	# used to be able to control whether it updated horizontally or vertically, but removed coz useless feature
	px_arr = pygame.PixelArray(screen)
	next_x = width_range[0]

	for pg_x in range(width_range[0], width_range[1]):				# set x_coord of vertical line
		px_arr[pg_x, height_range[0]:height_range[1]] = calc_line(pg_x, height_range, iters)[:-1]
		x_update_rect.left = pg_x
		pygame.display.update(x_update_rect)						# only update one vertical line at a time
		
		#Queue.receive(); while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()

	px_arr.close()
	save_img()


class IterText:
	def __init__(self, fontname, size, colour):
		self.font = pygame.font.SysFont(fontname, size)
		self.colour = colour
		self.centre_coords = WIDTH // 2, int(1.5 * size)

	def update(self, text, force_display=True):
		self.img = self.font.render(f"Iterations: {text}", True, self.colour)
		self.rect = self.img.get_rect()
		self.rect.center = self.centre_coords
		if force_display: self.display(True)

	def display(self, flip):
		if flip:
			screen.blit(bg_display, (0, 0))
			screen.blit(self.img, self.rect)
			pygame.display.flip()
		else:
			screen.blit(self.img, self.rect)


def move_graph(key):
	'''shift display to left to make it look as if screen moved right, etc'''
	global topleft, bg_display
	match key:
		case pygame.K_RIGHT:
			temp_rect.left -= MOVE_W
			topleft = (topleft[0] + MOVE_W / WIDTH * graph_width, topleft[1])
			width_range, height_range = (WIDTH - MOVE_W, WIDTH), (0, HEIGHT)
		case pygame.K_LEFT:
			temp_rect.left += MOVE_W
			topleft = (topleft[0] - MOVE_W / WIDTH * graph_width, topleft[1])
			width_range, height_range = (0, MOVE_W), (0, HEIGHT)
		case pygame.K_UP:
			temp_rect.top += MOVE_H
			topleft = (topleft[0], topleft[1] + MOVE_H / HEIGHT * graph_height)
			width_range, height_range = (0, WIDTH), (0, MOVE_H)
		case pygame.K_DOWN:
			temp_rect.top -= MOVE_H
			topleft = (topleft[0], topleft[1] - MOVE_H / HEIGHT * graph_height)
			width_range, height_range = (0, WIDTH), (HEIGHT - MOVE_H, HEIGHT)

	screen.blit(temp_display, temp_rect)
	pygame.display.flip()

	update_screen(width_range, height_range)
	bg_display = screen.copy()


def in_cardioid_or_bulb(x, y):
	if Z_POWER == 2:
		y_sq = y**2
		q = (x - 0.25)**2 + y_sq
		if 0.25 * y_sq >= q * (q + (x - 0.25)) or (x + 1)**2 + y_sq <= 0.0625:
			return True

	return False


def draw_circle(colour, pos, update_bg=True, colour_picker=False):
	global bg_display
	if not colour_picker:
		pygame.draw.circle(alpha_layer, colour, pos, CIRCLE_RADIUS)
	else:
		pygame.draw.circle(alpha_layer, colour, pos, BORDER_RADIUS, BORDER_THICC)

	if update_bg:											# keep last drawn circle instead of erasing it (like when updating mouse "cursor")
		screen.blit(alpha_layer, (0,0))
		bg_display = screen.copy()


def draw_rect_lines(topleft, bottomright):
	topright, bottomleft = (bottomright[0], topleft[1]), (topleft[0], bottomright[1])
	pygame.draw.lines(alpha_layer, LINE_COLOUR, True, (topleft, topright, bottomright, bottomleft), width=LINE_WIDTH)


def draw_spanning_lines(coords):
	pygame.draw.line(alpha_layer, LINE_COLOUR, (coords[0], 0), (coords[0], HEIGHT), width=LINE_WIDTH)
	pygame.draw.line(alpha_layer, LINE_COLOUR, (0, coords[1]), (WIDTH, coords[1]), width=LINE_WIDTH)


def calc_c2_coords(topleft_pg, mouse_x):
	if topleft_pg[0] == mouse_x:						# if both points are at same spot, shift 2nd point just 1 pixel to the right 
		mouse_x += 1
	elif mouse_x < topleft_pg[0]:						# if 2nd point is to the left of 1st, mirror it at 1st point
		mouse_x = topleft_pg[0] + (topleft_pg[0] - mouse_x)
	return mouse_x, int(topleft_pg[1] + (mouse_x - topleft_pg[0])/WIDTH * HEIGHT)


def update_pause_screen(circle_coords, circle_colour, inputs_left, topleft=None):
	screen.blit(bg_display, (0, 0))
	alpha_layer.fill((0,0,0,0))

	match inputs_left:
		case 3:
			draw_spanning_lines(circle_coords)
		case 2:
			draw_rect_lines(topleft, circle_coords)
		case 1:
			iter_font.display(False)

	draw_circle(circle_colour, circle_coords, update_bg=False, colour_picker=(inputs_left==1))

	screen.blit(alpha_layer, (0,0))
	pygame.display.flip()


# calculation constants
COLOUR_SET = False
MANDEL_COLOUR = (0, 0, 0)
Z_POWER = 2
C_POWER = 1
ESCAPE_RADIUS = 10
INITIAL_Z = complex(0, 0)
RAD_TO_DEG = 180 / pi


if __name__ == "__main__":
	pygame.init()

	# colour stuff:
	HUE_RANGE = 1 #360
	COLOURS = 44					# doesn't limit to this many colours, however, because of fractional iteration
	SCREEN_BG_COLOUR = (100, 100, 100)
	CIRCLE1_COLOUR = (160, 120, 120, 180)
	CIRCLE2_COLOUR = (80, 80, 120, 180)
	LINE_COLOUR = (250, 250, 250, 130)
	#current_colour = pygame.Color(0, 0, 0)

	# constants:
	CIRCLE_RADIUS = 6
	LINE_WIDTH = 3
	CPUS = cpu_count()
	PATH_TO_IMG = "generated imgs\\"

	# changeable constants/vars:
	INV_HUE_OFF = False
	BENCHMARK_MODE = False
	DARKEN_TRANSITION = True
	MOVEMENT_SCALE = 0.1								# default: 0.1
	iters = 200

	# actual graph stuff:
	WIDTH, HEIGHT = 800, 600							# default: 1200, 900 OR 800, 600
	MOVE_W, MOVE_H = int(WIDTH * MOVEMENT_SCALE), int(HEIGHT * MOVEMENT_SCALE)
	graph_width = 4										# default: 4
	graph_height = get_graph_height(graph_width)		# default: (calculated from graph_width)
	topleft = (-graph_width / 2, graph_height / 2)		# default: (-graph_width/2, graph_height/2)

	# reactive stuff:
	BORDER_RADIUS = max(WIDTH, HEIGHT)//40
	BORDER_THICC = int(BORDER_RADIUS*0.5)
	FONT_SIZE = min(WIDTH // 30, HEIGHT // 30)

	# font stuff:
	FONT_COLOUR = (250, 250, 250)
	ITER_MAX_DIGITS = 20
	iter_font = IterText("comicsansms", FONT_SIZE, FONT_COLOUR)		# other good fonts: Corbel

	pygame.event.set_blocked(None)						# block all events from entering the queue
	pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.QUIT, pygame.KEYDOWN))			# "LET ME IN" - eric andre
	pygame.event.set_grab(True)							# so that the window doesn't lose focus and pause

	UPDATE_THICC = 1
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_icon(pygame.image.load("mandelbrot.ico"))
	screen.fill(SCREEN_BG_COLOUR)
	pygame.display.flip()
	
	alpha_layer = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)			# used to blit translucent stuff
	debug_alpha = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
	px_data = Manager().JoinableQueue(1)									# only 1 iterable allowed; each process can be sure its result is received, computed, and a new task issued back
	#ctypes
	alpha_layer.fill((0,0,0,0))
	x_update_rect = pygame.Rect(0, 0, UPDATE_THICC, HEIGHT)
	BENCHMARK_NAME = f"bench v4.2nonparallel {WIDTH}x{HEIGHT} i{iters} {ran_str(3)}.txt"

	if BENCHMARK_MODE:
		with open(BENCHMARK_NAME, "w") as bench_file:
			bench_file.write(f"v4.2nonparallel, {WIDTH=}, {HEIGHT=}, {iters=}, {topleft=}, {graph_width=}\n(bench ver made on 15.06.22 1:30)")	

	while 1:
		pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations")
		#profile_func(update_screen, (0, WIDTH), (0, HEIGHT))

		while 1:
			if DARKEN_TRANSITION:
				alpha_layer.fill(MANDEL_COLOUR + (150,))
				screen.blit(alpha_layer, (0,0))
				pygame.display.flip()

			start_time = pygame.time.get_ticks()
			update_screen((0, WIDTH), (0, HEIGHT))
			elapsed = (pygame.time.get_ticks() - start_time) / 1000				

			if BENCHMARK_MODE:
				with open(BENCHMARK_NAME, "a") as bench_file:
					bench_file.write(f"\n{elapsed}")
			else:
				break

		printf(f"\nDone! Took {elapsed} seconds.\n\nClick to select the new topleft coordinate, or use the directional keys to move the graph.\n(If the screen doesn't change, move around a bit to refresh it)")

		bg_display = screen.copy()													# used to clear screen, so updated only when inputs_left changes 
		inputs_left = 3
		while inputs_left:
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if inputs_left == 3:
						topleft_pg = event.pos  						# used to store pygame coords of placed topleft circle
						draw_circle(CIRCLE1_COLOUR, event.pos)
						new_topleft = (get_graph_x(event.pos[0]), get_graph_y(event.pos[1]))
						inputs_left -= 1

						printf(f"New topleft: {new_topleft}\nClick again to determine the new graph width.")
					elif inputs_left == 2:
						c2_coords = calc_c2_coords(topleft_pg, event.pos[0])
						draw_circle(CIRCLE2_COLOUR, c2_coords)

						# prepare program for next loop
						old_graph_width = graph_width
						graph_width = get_graph_x(event.pos[0]) - get_graph_x(topleft_pg[0])
						graph_height = get_graph_height(graph_width)
						topleft = new_topleft
						printf(f"Graph width: {graph_width},\tgraph height: {graph_height}")

						input_string = ""
						iter_font.update(input_string)
						printf("Enter the new iterations number into the pygame window, and press enter. Backspace to delete.")
						inputs_left -= 1

				#elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
				#	save_img()
				#	print("saved")

				elif event.type == pygame.KEYDOWN:
					if inputs_left == 3 and event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
						screen.blit(bg_display, (0, 0))							# to clear mouse white circle from screen
						temp_display = screen.copy()							# difference between temp and bg_display: temp is for moving with arrow keys exclusively
						temp_rect = temp_display.get_rect()
						screen.fill(SCREEN_BG_COLOUR, temp_rect)

						move_graph(event.key)
						printf(f"Moved, new topleft: {topleft}")

					elif inputs_left == 1:
						strlen = len(input_string)
						if (pygame.K_1 <= event.key <= pygame.K_9 and strlen < ITER_MAX_DIGITS) or (event.key == pygame.K_0 and strlen > 0):		# update iterations input if numeric
							input_string = f"{input_string}{chr(event.key)}"
							iter_font.update(input_string)

						elif event.key == pygame.K_RETURN:
							if strlen > 0:
								iters = int(input_string)
								printf(f"New iters: {iters}")
								inputs_left -= 1
							else:
								printf("enter the iterations first dummy")

						elif event.key == pygame.K_BACKSPACE and strlen > 0:
							input_string = input_string[:-1]
							iter_font.update(input_string)

				elif event.type == pygame.MOUSEMOTION:
					match inputs_left:
						case 3:
							update_pause_screen(event.pos, CIRCLE1_COLOUR, inputs_left)
						case 2:
							update_pause_screen(calc_c2_coords(topleft_pg, event.pos[0]), CIRCLE2_COLOUR, inputs_left, topleft=topleft_pg)
						case 1:
							update_pause_screen(event.pos, bg_display.get_at(event.pos), inputs_left)

				elif event.type == pygame.QUIT:
					pygame.quit()
					exit()
