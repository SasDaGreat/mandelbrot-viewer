from cProfile import Profile
from pstats import Stats, SortKey

#from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Manager, cpu_count
from queue import Empty
from sys import stdout, argv

from colorsys import hsv_to_rgb
from math import log as ln
from cmath import phase, pi

#import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

'''
New features over v4.1:
- P A R A L L E L I S A T I O N, leading to > 5x speed at higher zooms on a 6-core CPU
- custom image data and unique IDs, leading to shorter filenames and being able to store all the info about an image
- sys.argv feature, so you can drag n drop a past image to copy over its conditions easily
- benchmarking mode, which repeatedly runs the program under initial conditions and saves the time elapsed
- profiling func, to check what functions take the most time (NOT YET TESTED WITH MULTIPROCESSING, works in nonparallel version)
- cool new rendering/visual effects, SHUFFLE_X (updates random lines of the screen) and SPREAD_EFFECT (updated line is spread over unrendered portion of screen)
- progress bar
- fixed bugs/oversights'''

#personal notes:
# pool.map_async(chunksize)?
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
	pygame.image.save(screen, f"{PATH_TO_IMG}{pic_id}.png")

	img = Image.open(f"{PATH_TO_IMG}{pic_id}.png")
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
	meta.add_text("ESCAPE_RADIUS", f"{ESCAPE_RADIUS}")
	meta.add_text("HUE_RANGE", f"{HUE_RANGE}")
	meta.add_text("CPUS", f"{CPUS}")
	meta.add_text("extras", f"vanilla v4.2")

	img.save(f"{PATH_TO_IMG}{pic_id}.png", pnginfo=meta)


def get_graph_x(pg_x, topleft_x, graph_width): return topleft_x + pg_x / WIDTH * graph_width
def get_graph_y(pg_y, topleft_y, graph_height): return topleft_y - pg_y / HEIGHT * graph_height

def get_graph_height(graph_w): return (HEIGHT / WIDTH) * graph_w


def normalise(i, modulus): return round(i - ln(ln(modulus), Z_POWER), 2)


def get_hue(i): return ((i % COLOURS) / COLOURS) * HUE_RANGE if INV_HUE_OFF else (1 - (i % COLOURS) / COLOURS) * HUE_RANGE


def map_rgb(rgb): return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]


def map_hsv(hue, sat=1, val=1):
	'''Maps HSV (0 - 1) to RGB (0 - 255), usually using a single hue value'''
	norm_rgb = hsv_to_rgb(hue, sat, val)
	return map_rgb(tuple(round(i*255) for i in norm_rgb))		# + (255,) if alpha is needed


def in_cardioid_or_bulb(x, y):
	y_sq = y**2
	q = (x - 0.25)**2 + y_sq
	if y_sq / 4 < q * (q + (x - 0.25)) and (x + 1)**2 + y_sq > 0.0625:
		return False
	return True


def corners_in_c_or_b(width_range, height_range, topleft, graph_width, graph_height):
	'''Check if any of the corners of the update area are in the main cardioid or side bulb (whose iterations can be avoided)'''
	if graph_width > 1:
		return True

	topright, bottomleft, bottomright = (
		(get_graph_x(width_range[1], topleft[0], graph_width), get_graph_y(height_range[0], topleft[1], graph_height)),
		(get_graph_x(width_range[0], topleft[0], graph_width), get_graph_y(height_range[1], topleft[1], graph_height)),
		(get_graph_x(width_range[1], topleft[0], graph_width), get_graph_y(height_range[1], topleft[1], graph_height)),
		)
	return (
		in_cardioid_or_bulb(*topleft) or
		in_cardioid_or_bulb(*topright) or
		in_cardioid_or_bulb(*bottomleft) or
		in_cardioid_or_bulb(*bottomright)
		)


def get_colour(x, y, iters, optimise_cardioid):
	'''Bulk of the computation! Gets the mapped colour for a single pixel, given graphical x and y'''
	if optimise_cardioid and in_cardioid_or_bulb(x, y):	# enables ONLY when generating close to cardioid or bulb, since this takes a lot of computation
		return MANDEL_COLOUR

	c = complex(x, y)
	if C_POWER < 0 and c == 0j:						# enable only for inverse mandelbrots
		return map_hsv(get_hue(0))
	
	z = INITIAL_Z
	for i in range(iters):
		z = z**Z_POWER + c**C_POWER
		z_mod = abs(z)
		if z_mod > ESCAPE_RADIUS:
			return map_hsv(get_hue(normalise(i, z_mod)))
	else:
		return map_hsv(phase(z)) if COLOUR_SET else MANDEL_COLOUR


def calc_line(data_tup):
	'''Calculates, packages, and sends colour data to the main thread for a single vertical line'''
	global WIDTH, HEIGHT, Z_POWER, C_POWER, INITIAL_Z, ESCAPE_RADIUS, HUE_RANGE
	try:
		(
			height_range,
			iters,
			end_x,
			px_data_q,
			next_x_q,
			topleft,
			graph_width,
			graph_height,
			optimise_cardioid,
			WIDTH,
			HEIGHT,
			Z_POWER,
			C_POWER,
			INITIAL_Z,
			ESCAPE_RADIUS,
			HUE_RANGE,
			) = data_tup
		pg_x = next_x_q.get()

		while pg_x < end_x:
			y_colours = []														# format: [:-1] = data, [-1] = x of data
			graph_x = get_graph_x(pg_x, topleft[0], graph_width)
			for pg_y in range(*height_range):
				graph_y = get_graph_y(pg_y, topleft[1], graph_height)
				y_colours.append(get_colour(graph_x, graph_y, iters, optimise_cardioid))

			y_colours.append(pg_x)
			px_data_q.put(y_colours)
			pg_x = next_x_q.get()

	except Exception as e:
		printf(f"EXCEPTION!!!!!!!!!!!!!!! {e}")
		#logger.exception(e)


def update_screen(width_range, height_range, moved=False):
	'''Update a specified portion of the screen. Used to be able to control whether it updated horizontally or vertically, but removed coz useless feature'''
	with (
		Pool(CPUS) as pool,
		pygame.PixelArray(screen) as px_arr,
		Manager() as m
		):
		px_data_q = m.Queue()
		next_x_q = m.Queue()

		x_update_rect.height = height_range[1] - height_range[0]
		x_update_rect.top = height_range[0]
		last_updated_x = width_range[0]

		optimise_cardioid = Z_POWER == 2 and C_POWER == 1 and not COLOUR_SET and corners_in_c_or_b(width_range, height_range, topleft, graph_width, graph_height)

		if not SHUFFLE_X:
			for x in range(width_range[0], width_range[1] + CPUS):			# adding an extra CPUS number of xes means all the processes will exit, since pg_x > end_x
				next_x_q.put(x)
		else:			
			x_range = list(range(width_range[0], width_range[1]))
			shuffle(x_range)
			x_range += list(range(width_range[1], width_range[1] + CPUS))
			for x in x_range:
				next_x_q.put(x)			


		data = (
			height_range,
			iters,
			width_range[1],
			px_data_q,
			next_x_q,
			topleft,
			graph_width,
			graph_height,
			optimise_cardioid,
			WIDTH,
			HEIGHT,
			Z_POWER,
			C_POWER,
			INITIAL_Z,
			ESCAPE_RADIUS,
			HUE_RANGE,			
			)
		tasks = pool.map_async(calc_line, (data, ) * CPUS )

		running = True
		exit_now = False
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					exit_now = True

			if exit_now: break
			tasks_done = tasks.ready()

			try:
				# could've used px_data_q.empty() here but eh
				line_data = px_data_q.get(block = not tasks_done, timeout=PXDATA_TIMEOUT)		# if tasks aren't done, keep on using timeout
				line_x = line_data[-1]
				x_update_rect.left = line_x

				if not SPREAD_EFFECT or line_x <= last_updated_x or moved:
					px_arr[line_x, height_range[0]:height_range[1]] = line_data[:-1]
				else:
					for i,y in enumerate(range(*height_range)):
						px_arr[line_x:, y] = line_data[i]
					x_update_rect.width = width_range[1] - line_x
					last_updated_x = line_x

				pygame.display.update(x_update_rect)
				progress = round((1 - next_x_q.qsize() / (width_range[1] - width_range[0])) * 100, 1)
				# a bit inaccurate coz +CPUS and only measures progress of processes, not displaying
				pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations  ||  {progress}% done")
			except Empty:
				if tasks_done: break
				else: continue

	del pool, px_arr, m, next_x_q, px_data_q
	if exit_now:														# ensures with statement finishes first
		adios()

	save_img(moved)


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

	update_screen(width_range, height_range, moved=True)
	bg_display = screen.copy()


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
	if topleft_pg[0] == mouse_x:						# if both points are at same spot, shift 2nd point just 5 pixels to the right 
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

INV_HUE_OFF = True
COLOURS = 44											# default: 44. doesn't limit to this many colours, however, because of fractional iteration
COLOUR_SET = True
MANDEL_COLOUR = (0, 0, 0)
RAD_TO_DEG = 180 / pi


if __name__ == "__main__":
	from string import ascii_letters, digits
	from random import choices, shuffle

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

		# initialisation constants, needed only by main process
		CPUS = int(img.text["CPUS"])
		iters = int(img.text["iters"])
		graph_width = float(img.text["graph_width"])
		graph_height = float(img.text["graph_height"])
		topleft = img.text["topleft"][1:-1].split(", ")
		topleft = float(topleft[0]), float(topleft[1])			
	else:
		WIDTH, HEIGHT = 1200, 900							# default: 1200, 900 OR 800, 600
		Z_POWER = 2
		C_POWER = 1
		INITIAL_Z = complex(0, 0)
		ESCAPE_RADIUS = 5
		HUE_RANGE = 1
		CPUS = cpu_count()								# more testing needed! for now, seems like cpu_count() is the optimal number

		# changeable constants/init vars:
		iters = 200
		graph_width = 4									# default: 4. NOTE!!! at ~1e-13 graph_width, precision errors start showing up. Decimals fix?
		graph_height = get_graph_height(graph_width)	# default: (calculated from graph_width). disabling might result in a stretched graph
		topleft = (-graph_width/2, graph_height/2)		# default: (-graph_width/2, graph_height/2)
	
	SHUFFLE_X = True									# has a cool transition effect between generations
	SPREAD_EFFECT = False								# enable only if SHUFFLE_X is true. might affect performance. VERY COOL EFFECT THO!
	BENCHMARK_MODE = False
	DARKEN_TRANSITION = True

	# "constant" constants:
	MOVEMENT_SCALE = 0.1								# default: 0.1
	MOVE_W, MOVE_H = int(WIDTH * MOVEMENT_SCALE), int(HEIGHT * MOVEMENT_SCALE)
	UPDATE_THICC = 1
	CIRCLE_RADIUS = 6
	LINE_WIDTH = 3
	PXDATA_TIMEOUT = 0.05		################### could tweak to see what value works best	# acts like a clock/framerate limiter
	PATH_TO_IMG = "generated imgs\\"
	BENCHMARK_NAME = f"bench v4.2 {WIDTH}x{HEIGHT} i{iters} {ran_str(3)}.txt"

	# reactive stuff:
	BORDER_RADIUS = max(WIDTH, HEIGHT)//40
	BORDER_THICC = int(BORDER_RADIUS*0.5)
	FONT_SIZE = min(WIDTH // 30, HEIGHT // 30)

	# colours:
	SCREEN_BG_COLOUR = (100, 100, 100)
	CIRCLE1_COLOUR = (160, 120, 120, 180)
	CIRCLE2_COLOUR = (80, 80, 120, 180)
	LINE_COLOUR = (250, 250, 250, 100)

	FONT_COLOUR = (250, 250, 250)
	ITER_MAX_DIGITS = 20
	iter_font = IterText("bahnschrift", FONT_SIZE, FONT_COLOUR)		# other good fonts: Corbel

	pygame.event.set_blocked(None)						# block all events from entering the queue
	pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.QUIT, pygame.KEYDOWN))			# "LET ME IN" - eric andre
	pygame.event.set_grab(True)							# so that the window doesn't lose focus and pause

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_icon(pygame.image.load("mandelbrot.ico"))
	pygame.display.set_caption(f"The Mandelbrot Set")
	screen.fill(SCREEN_BG_COLOUR)
	pygame.display.flip()
	
	alpha_layer = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)			# used to blit translucent stuff
	alpha_layer.fill((0,0,0,0))
	x_update_rect = pygame.Rect(0, 0, UPDATE_THICC, HEIGHT)

	if BENCHMARK_MODE:
		with open(BENCHMARK_NAME, "w") as bench_file:
			bench_file.write(f"v4.2, {WIDTH=}, {HEIGHT=}, {iters=}, {topleft=}, {graph_width=}, {CPUS=}, {PXDATA_TIMEOUT=}\n(bench ver made on 15.06.22 1:30)")		

	while 1:
		#profile_func(update_screen, (0, WIDTH), (0, HEIGHT))

		while 1:
			if DARKEN_TRANSITION:
				alpha_layer.fill(MANDEL_COLOUR + (150,))
				screen.blit(alpha_layer, (0,0))
				pygame.display.flip()
			
			start_time = pygame.time.get_ticks()
			update_screen((0, WIDTH), (0, HEIGHT))
			elapsed = (pygame.time.get_ticks() - start_time) / 1000			
			pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations")

			if BENCHMARK_MODE:
				with open(BENCHMARK_NAME, "a") as bench_file:
					bench_file.write(f"\n{elapsed}")

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						adios()
			else:
				break

		printf(f"\nDone! Took {elapsed} seconds.\n\nLeft click to select the new topleft coordinate, right click to show coordinates of a point, or use arrow keys to move the graph.")

		bg_display = screen.copy()										# used to clear screen, so updated only when inputs_left changes 
		inputs_left = 3
		while inputs_left:
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if inputs_left == 3:
						topleft_pg = event.pos  						# stores pygame coords of placed topleft circle
						draw_circle(CIRCLE1_COLOUR, event.pos)
						new_topleft = (
							get_graph_x(event.pos[0], topleft[0], graph_width),
							get_graph_y(event.pos[1], topleft[1], graph_height)
							)
						inputs_left -= 1

						printf(f"New topleft: {new_topleft}\nClick again to determine the new graph width.")
					elif inputs_left == 2:
						c2_coords = calc_c2_coords(topleft_pg, event.pos[0])
						draw_circle(CIRCLE2_COLOUR, c2_coords)

						# prepare program for next loop
						old_graph_width = graph_width
						graph_width = (
							get_graph_x(c2_coords[0], topleft[0], graph_width)
							- get_graph_x(topleft_pg[0], topleft[0], graph_width)
							)
						graph_height = get_graph_height(graph_width)
						topleft = new_topleft
						printf(f"Graph width: {graph_width},\tgraph height: {graph_height}")

						input_string = ""
						iter_font.update(input_string)
						printf("Enter the new iterations number into the pygame window, and press enter. Backspace to delete.")
						inputs_left -= 1

				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
					print(f"Pygame coords: {event.pos}\tgraph coords: {(get_graph_x(event.pos[0], topleft[0], graph_width), get_graph_y(event.pos[1], topleft[1], graph_height))}")

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
					adios()
