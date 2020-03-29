# squared complex no.s

import pygame
pygame.init()


DISPLAY = WIDTH,HEIGHT = 600,600
BLACK   = (0,0,0)
WHITE   = (255,255,255)
BLUE    = (0,0,255)
CIRCLE_SIZE = 3

min_power, max_power = 2,100
colour_decrement = 255/abs(max_power - min_power)


actual_width  = 4
scale_ratio   = WIDTH/actual_width


screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("Squaring complex numbers")


while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()

	# get the coordinates of the mouse on the complex plane; first raw coord data, adjusted coord data, then complex plane data
	orig_coords = pygame.mouse.get_pos()
	adj_orig_coords  = ( orig_coords[0] - WIDTH//2, HEIGHT//2 - orig_coords[1] )
	c_plane_coords = adj_orig_coords[0]/scale_ratio, adj_orig_coords[1]/scale_ratio
	# c is the original complex plane coordinate moused over
	orig_c = complex(c_plane_coords[0], c_plane_coords[1])


	screen.fill(WHITE)

	# draw the axes
	pygame.draw.line(screen, BLACK, (0,HEIGHT//2), (WIDTH, HEIGHT//2))
	pygame.draw.line(screen, BLACK, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

	pygame.draw.circle(screen, BLUE, orig_coords, 3)		# the original moused-over point


	colour = 255
	pow_c = 0

	for power in range(min_power, max_power+1):
		try:
			pow_c  = pow_c**power + orig_c

			adj_pow_coords = pow_c.real * scale_ratio, pow_c.imag * scale_ratio
			pow_coords = int(adj_pow_coords[0] + WIDTH//2), int(HEIGHT//2 - adj_pow_coords[1])
		except:
			break

		if pow_coords[0] < WIDTH + CIRCLE_SIZE and pow_coords[0] > -CIRCLE_SIZE and pow_coords[1] < HEIGHT + CIRCLE_SIZE and pow_coords[1] > -CIRCLE_SIZE:
			pygame.draw.circle(screen, (int(colour),0,0),  pow_coords,  CIRCLE_SIZE)
		
		colour -= colour_decrement

	pygame.display.flip()
