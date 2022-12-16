from cProfile import Profile
from pstats import Stats, SortKey

#from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Manager, cpu_count, parent_process
from queue import Empty
from sys import stdout, argv

import numpy as np

#import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

'''
New features over v4.2:
- numpy! vectorised generation of each line, leading to another great speed improvement (more than 4x at high levels of zoom)'''

#personal notes:
# if you rebuild this program, could group funcs and constants into classes. e.g. a Display class containing the display screen and screen update funcs
# IMP!!!! if you use current_w directly using "for w in np.linspace(W_START, W_END, W_NUM): put(w)", it ends in a pipe error. could be due to main func facing unrelated exceptions, tho?


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
	meta.add_text("extras", f"vanilla v4.3")

	img.save(f"{PATH_TO_IMG}{pic_id}.png", pnginfo=meta)


def get_graph_x(pg_x, topleft_x, graph_width): return topleft_x + pg_x / WIDTH * graph_width

def get_graph_y(pg_y, topleft_y, graph_height): return topleft_y - pg_y / HEIGHT * graph_height

def get_graph_height(graph_w): return (HEIGHT / WIDTH) * graph_w


def map_rgb(r, g, b):
	#if is_array:
	#	r, g = np.array(r, dtype=np.uint32), np.array(g, dtype=np.uint16)
	return (r << 16) + (g << 8) + b


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
	norm_hue_arr = (norm_i_arr % COLOURS) * HUE_RANGE/COLOURS if INV_HUE_OFF else (COLOURS - (norm_i_arr % COLOURS)) * HUE_RANGE/COLOURS
	return hsv_to_rgb(norm_hue_arr)


def calc_screen(data_tup):
	'''Calculates, packages, and sends colour data to the main thread for the entire screen for a single w'''
	global WIDTH, HEIGHT, Z_POWER, C_POWER, INITIAL_Z, ESCAPE_RADIUS, HUE_RANGE
	try:
		(
			width_range,
			height_range,
			iters,
			px_data_q,
			next_w_q,
			topleft,
			graph_width,
			graph_height,
			WIDTH,
			HEIGHT,
			Z_POWER,
			C_POWER,
			INITIAL_Z,
			ESCAPE_RADIUS,
			HUE_RANGE,
			W_START,
			W_RANGE,
			W_NUM,
		) = data_tup

		pg_width = width_range[1] - width_range[0]
		pg_height = height_range[1] - height_range[0]		
		x = np.linspace(topleft[0], topleft[0] + graph_width, num = pg_width).reshape((pg_width, 1))
		y = np.linspace(topleft[1], topleft[1] - graph_height, num = pg_height).reshape((1, pg_height))
		c_arr = x + y * 1j

		while 1:
			# w can be the variable for any condition in this execution loop; this will be manually changed at the start of each generation
			w_index = next_w_q.get()
			if w_index is None: break
			current_w = W_START + w_index/(W_NUM-1) * W_RANGE
			#INITIAL_Z = complex(current_w, 0)
			Z_POWER = current_w

			z_arr = np.full(c_arr.shape, INITIAL_Z, dtype=complex)
			iter_arr = np.zeros(c_arr.shape, dtype=int)									# logs the iters at which each point escapes. 0 = not diverged yet
			mandel_points = np.full(c_arr.shape, True, dtype=bool)
			# represents points that MIGHT be part of set. False = already diverged, True = will participate in next iteration

			if C_POWER < 0: mandel_points[np.where(c_arr == 0j)] = False 				# makes (0,0) diverge at 0 iters
			
			for i in range(iters):
				mask = mandel_points						# only compute points that MIGHT be in set, not those confirmed to be
				z_arr[mask] = z_arr[mask]**Z_POWER + c_arr[mask]**C_POWER
				currently_diverged = np.greater_equal(abs(z_arr), ESCAPE_RADIUS, out=np.full(c_arr.shape, False, dtype=bool), where=mask)
				# checks where current z_arr's modulus > ER, but checks ONLY at points where mandel_points = True (not yet diverged). currently_diverged = only new divergences
				mandel_points[currently_diverged] = False 								# mandel_points cumulates all the divergences as False
				iter_arr[currently_diverged] = i
			
			#return map_hsv((phase(z) + pi) * RAD_TO_DEG) if COLOUR_SET else MANDEL_COLOUR

			anti_mandels = np.logical_not(mandel_points)
			iter_arr[anti_mandels] = 0 #colour_from_i(iter_arr[anti_mandels], z_arr[anti_mandels])
			iter_arr[mandel_points] = M_COLOUR_MAP

			px_data_q.put((w_index, iter_arr))

	except Exception as e:
		printf(f"EXCEPTION!!!!!!!!!!!!!!! {e}")
		#logger.exception(e)


def update_screen(width_range, height_range):
	'''Update a specified portion of the screen. Used to be able to control whether it updated horizontally or vertically, but removed coz useless feature'''
	with (
			Pool(CPUS) as pool,
			Manager() as m
		):
		px_data_q = m.Queue()
		next_w_q = m.Queue()

		w_list = list(range(W_NUM))
		shuffle(w_list)
		# ensures that the done% is accurate
		for w_index in w_list:
			next_w_q.put(w_index)

		data = (
			width_range,
			height_range,
			iters,
			px_data_q,
			next_w_q,
			topleft,
			graph_width,
			graph_height,
			WIDTH,
			HEIGHT,
			Z_POWER,
			C_POWER,
			INITIAL_Z,
			ESCAPE_RADIUS,
			HUE_RANGE,
			W_START,
			W_RANGE,
			W_NUM,
		)
		tasks = pool.map_async(calc_screen, (data, ) * CPUS )
		full_arr = np.zeros((width_range[1] - width_range[0], height_range[1] - height_range[0], W_NUM))
		w_left = W_NUM

		exit_now = False
		while w_left:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					exit_now = True
			if exit_now: break

			try:
				w, scr_data = px_data_q.get(timeout=PXDATA_TIMEOUT)
				full_arr[:, :, w] = scr_data
				w_left -= 1

				surf = pygame.Surface(scr_data.shape)
				pygame.surfarray.blit_array(surf, scr_data)
				screen.blit(surf, (0,0))
				pygame.display.flip()

				# a bit inaccurate coz +CPUS and only measures progress of processes, not displaying
				pygame.display.set_caption(f"MSet @ power {Z_POWER}, {iters} iters  ||  {round(100 - w_left/W_NUM * 100, 2)}% done")

			except Empty:
				continue

		for _ in range(CPUS):
			next_w_q.put(None)

	del pool, m, next_w_q, px_data_q

	mandel_points_arr = full_arr > 0
	np.save(f"mandel_3dw_c-({CURRENT_W_CONDN})_i{iters}_t{topleft}_{ran_str()}", mandel_points_arr)
	if exit_now:														# ensures with statement finishes first
		adios()


INV_HUE_OFF = True
COLOURS = 44											# default: 44. doesn't limit to this many colours, however, because of fractional iteration
COLOUR_SET = False
MANDEL_COLOUR = (255, 255, 255)
M_COLOUR_MAP = map_rgb(*MANDEL_COLOUR)
RAD_TO_DEG = 180 / 3.14159


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
		try:
			img = Image.open(argv[1])

			# calculation constants, needed by subprocesses
			WIDTH, HEIGHT = img.size
			Z_POWER = int(img.text["Z_POWER"])					# use float() if image had non-integer powers
			C_POWER = float(img.text["C_POWER"])					# ^
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
		except Exception as e:
			input(e)		
	else:
		WIDTH, HEIGHT = 200, 150							# matplotlib voxels cant handle more than 200x150 even for me
		Z_POWER = 2
		C_POWER = 1
		INITIAL_Z = complex(0, 0)
		ESCAPE_RADIUS = 5
		HUE_RANGE = 1
		CPUS = cpu_count()								# more testing needed! for now, seems like cpu_count() is the optimal number

		# changeable constants/init vars:
		iters = 100
		graph_width = 4									# default: 4. NOTE!!! at ~1e-13 graph_width, precision errors start showing up. Decimals fix?
		graph_height = get_graph_height(graph_width)	# default: (calculated from graph_width). disabling might result in a stretched graph
		topleft = (-graph_width/2, graph_height/2)		# default: (-graph_width/2, graph_height/2)

	W_START, W_END, W_NUM = 1, 5, 201
	W_RANGE = W_END - W_START
	CURRENT_W_CONDN = "Z_POWER"

	# "constant" constants:
	PXDATA_TIMEOUT = 0.05		################### could tweak to see what value works best	# acts like a clock/framerate limiter
	PATH_TO_IMG = "generated imgs\\"
	SCREEN_BG_COLOUR = (100, 100, 100)

	pygame.event.set_blocked(None)						# block all events from entering the queue
	pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.QUIT, pygame.KEYDOWN))			# "LET ME IN" - eric andre
	pygame.event.set_grab(True)							# so that the window doesn't lose focus and pause

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_icon(pygame.image.load("mandelbrot.ico"))
	pygame.display.set_caption(f"The Mandelbrot Set")
	screen.fill(SCREEN_BG_COLOUR)
	pygame.display.flip()

	#profile_func(update_screen, (0, WIDTH), (0, HEIGHT))
	
	start_time = pygame.time.get_ticks()
	update_screen((0, WIDTH), (0, HEIGHT))
	elapsed = (pygame.time.get_ticks() - start_time) / 1000	

	printf(f"\nDone! Took {elapsed} seconds.\n")
