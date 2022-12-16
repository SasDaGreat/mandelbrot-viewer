import pygame
from math import log as ln
pygame.init()

def get_graph_x(pg_x): return topleft[0] + pg_x/WIDTH * graph_width
def get_graph_y(pg_y): return topleft[1] - pg_y/HEIGHT* graph_height

def get_pg_x(g_x): return round((g_x - topleft[0])/graph_width * WIDTH)
def get_pg_y(g_y): return round((topleft[1] - g_y)/graph_height* HEIGHT)

def update_screen(width_range, height_range, horizontal_scrolling):
	if horizontal_scrolling:
		for pg_x in range(width_range[0], width_range[1]):
			graph_x = get_graph_x(pg_x)

			for pg_y in range(height_range[0], height_range[1]):
				graph_y = get_graph_y(pg_y)

				draw_lines(graph_x,graph_y)

			print(pg_x)
			pygame.display.flip()
	else:
		for pg_y in range(height_range[0], height_range[1]):
			graph_y = topleft[1] - (pg_y/HEIGHT) * graph_height

			for pg_x in range(width_range[0], width_range[1]):
				graph_x = topleft[0] + (pg_x/WIDTH)  * graph_width

				draw_lines(graph_x,graph_y)

			pygame.display.flip()

	pygame.image.save(screen,f"mandelpygamev10 pz{Z_POWER},c{C_POWER} i{iters} c{MANDEL_COLOUR} z{INITIAL_Z}, tl{topleft} w{graph_width} h{graph_height}.png")

def update_iter_font(text):
	screen.blit(original_display, (0,0))		# clear the screen of the previous text

	font_img = iter_font.render(f"Iterations: {text}", True, FONT_COLOUR)
	font_rect= font_img.get_rect()
	font_rect.center = int(WIDTH//2), int(1.5*FONT_SIZE)

	screen.blit(font_img, font_rect)
	pygame.display.update(font_rect)


def move_right():
	global topleft
	temp_rect.left -= MOVE_W			# shift display to left to make it look as if screen moved right. Same for others
	topleft = ( topleft[0] + MOVE_W/WIDTH * graph_width, topleft[1] ) 	# topleft coords increase in the same direction
	screen.blit(temp_display, temp_rect)
	pygame.display.flip()

	update_screen((WIDTH-MOVE_W,WIDTH), (0,HEIGHT), True)

def move_left():
	global topleft
	temp_rect.left += MOVE_W
	topleft = ( topleft[0] - MOVE_W/WIDTH * graph_width, topleft[1] )
	screen.blit(temp_display, temp_rect)
	pygame.display.flip()

	update_screen((0,MOVE_W), (0,HEIGHT), True)

def move_up():
	global topleft
	temp_rect.top += MOVE_H
	topleft = ( topleft[0], topleft[1] + MOVE_H/HEIGHT * graph_height )
	screen.blit(temp_display, temp_rect)
	pygame.display.flip()

	update_screen((0,WIDTH), (0,MOVE_H), False)

def move_down():
	global topleft
	temp_rect.top -= MOVE_H
	topleft = ( topleft[0], topleft[1] - MOVE_H/HEIGHT * graph_height )
	screen.blit(temp_display, temp_rect)
	pygame.display.flip()

	update_screen((0,WIDTH), (HEIGHT-MOVE_H,HEIGHT), False)

MOVEMENT_VALUES = {
	pygame.K_RIGHT	: move_right,
	pygame.K_LEFT 	: move_left,
	pygame.K_UP 	: move_up,
	pygame.K_DOWN 	: move_down
}


def get_graph_height(graph_w): return (HEIGHT/WIDTH) * graph_w

def draw_lines(x,y):
	c = complex(x,y)
	if C_POWER < 1 and c == 0+0j: return 	# ENABLE ONLY FOR INVERSE MANDELBROTS
	z = INITIAL_Z
	escaped = False

	for i in range(iters):
		z = z**Z_POWER + c**C_POWER

		z_mod = abs(z)
		if z_mod > ESCAPE_RADIUS:
			escaped = True
			break

	if (escaped and DRAW_ESCAPED_LINES) or (not escaped and DRAW_MANDEL_LINES):
		pg_c = get_pg_x(c.real), get_pg_y(c.imag)
		pg_z = get_pg_x(z.real), get_pg_y(z.imag)
		#pygame.display.update(pygame.draw.lines(screen, MANDEL_COLOUR, (0,0), (pg_c, pg_z)))
		pygame.draw.lines(screen, MANDEL_COLOUR, (0,0), (pg_c, pg_z))

# colour shit:
MANDEL_COLOUR	= ( 0,100,100, 100)	# red
SCREEN_BG_COLOUR= (100,100,100)
CIRCLE_RADIUS 	= 5
circle_rec 		= pygame.Rect(0, 0, CIRCLE_RADIUS*2, CIRCLE_RADIUS*2)
DRAW_MANDEL_LINES 	= True
DRAW_ESCAPED_LINES 	= False

# changeable constants:
Z_POWER		= 2
C_POWER		= 1
INITIAL_Z	= complex(0,0)

# iteration shit:
SENSITIVITY = 2
iters 		= 50
SCALE_ITERS = False	# whether or not the program should increase the iterations limit as the graph is zoomed in
zoom = iters**0.5

# actual graph shit:
MOVEMENT_SCALE 	= 0.1									# default: 0.1
WIDTH,HEIGHT 	= 800,600								# default: 800,600
MOVE_W,MOVE_H 	= int(WIDTH*MOVEMENT_SCALE), int(HEIGHT*MOVEMENT_SCALE)
graph_width		= 4										# default: 4
graph_height 	= get_graph_height(graph_width)			# default: (calculated from graph_width)
topleft 		= (-graph_width/2, graph_height/2)		# default: (-graph_width/2, graph_height/2)
ESCAPE_RADIUS 	= max((graph_width**2 + graph_height**2)**0.5 / 2, 2)

# iter font shit:
FONT_SIZE 	= min(WIDTH//30, HEIGHT//30)
iter_font 	= pygame.font.SysFont("comicsansms",FONT_SIZE)		# other good fonts: Corbel
MAX_ITER_DIG= 20
FONT_COLOUR = (250,250,250)

pygame.event.set_blocked(None)		# block all events from entering the queue
pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.QUIT, pygame.KEYDOWN)) 	# "LET ME IN" - eric andre

UPDATE_THICC 	= 1
screen 			= pygame.display.set_mode((WIDTH,HEIGHT))
#pygame.display.set_icon(pygame.image.load("mandelbrot.ico"))
screen.fill(SCREEN_BG_COLOUR)
pygame.display.flip()

while 1:
	pygame.display.set_caption(f"The Mandelbrot Set @ power {Z_POWER}, {iters} iterations")
	start_time = pygame.time.get_ticks()

	update_screen((0,WIDTH), (0,HEIGHT), True)

	elapsed = (pygame.time.get_ticks() - start_time)/1000
	print(f"\nDone! Took {elapsed} seconds.\nClick to select the new topleft coordinate, or use the directional keys to move the graph.\n(If the screen doesn't change, move around a bit to refresh it)", flush=True)

	no_of_inputs_left = 3
	while no_of_inputs_left:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if no_of_inputs_left == 3:
					topleft_pg_x, topleft_pg_y = event.pos
					new_topleft = ( get_graph_x(topleft_pg_x), get_graph_y(topleft_pg_y) )

					pygame.draw.circle(screen, (255,255,255), event.pos, CIRCLE_RADIUS, 0)
					circle_rec.center = event.pos
					pygame.display.update(circle_rec)

					no_of_inputs_left -= 1
					print(f"New topleft: {new_topleft}\nClick again to determine the new graph width.", flush=True)
				elif no_of_inputs_left == 2:
					right_pg_x = event.pos[0]
					if topleft_pg_x == right_pg_x: right_pg_x += 1
					elif right_pg_x < topleft_pg_x: right_pg_x = topleft_pg_x + (topleft_pg_x - right_pg_x)

					old_graph_width = graph_width
					graph_width = get_graph_x(right_pg_x) - get_graph_x(topleft_pg_x)
					graph_height= get_graph_height(graph_width)
					topleft 	= new_topleft

					bottomright_pg = ( right_pg_x, int(topleft_pg_y + (right_pg_x - topleft_pg_x)/WIDTH * HEIGHT) )
					pygame.draw.circle(screen, (200,200,200), bottomright_pg, CIRCLE_RADIUS, 0)
					circle_rec.center = bottomright_pg
					pygame.display.update(circle_rec)

					print(f"Graph width: {graph_width},\tgraph height: {graph_height}", flush = True)

					if SCALE_ITERS:
						zoom += old_graph_width/graph_width - 1
						iters = int(zoom**SENSITIVITY)
						no_of_inputs_left -= 1
					else:
						print("Enter the new iterations number into the pygame window, and press enter.", flush=True)
						original_display = screen.copy()
						input_string = ""
						update_iter_font(input_string)

					no_of_inputs_left -= 1

			elif event.type == pygame.KEYDOWN:
				if no_of_inputs_left == 3 and event.key in (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT):
					temp_display= screen.copy()
					temp_rect 	= temp_display.get_rect()
					screen.fill(SCREEN_BG_COLOUR, temp_rect)

					MOVEMENT_VALUES[event.key]()
					print(f"Moved, new topleft: {topleft}", flush = True)

				elif no_of_inputs_left == 1:
					strlen = len(input_string)
					if (pygame.K_1 <= event.key <= pygame.K_9 and strlen < MAX_ITER_DIG) or (event.key == pygame.K_0 and strlen > 0):
						input_string = f"{input_string}{chr(event.key)}"
						update_iter_font(input_string)

					elif event.key == pygame.K_RETURN:
						if strlen > 0:
							iters = int(input_string)
							print(f"New iters: {iters}", flush = True)
							no_of_inputs_left -= 1
						else:
							print("enter the iterations first dummy", flush = True)

			elif event.type == pygame.QUIT: exit()
