# squared complex no.s

import pygame
pygame.init()


DISPLAY = WIDTH,HEIGHT = 600,600
BLACK   = (0,0,0)
WHITE   = (255,255,255)
GRAY    = (100,100,100)
RED     = (255,0,0)

POWER = 1.75


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
	sqr_c  = orig_c**POWER

	adj_sqr_coords = sqr_c.real * scale_ratio, sqr_c.imag * scale_ratio
	sqr_coords = int(adj_sqr_coords[0] + WIDTH//2), int(HEIGHT//2 - adj_sqr_coords[1])

	print(f"{orig_c} --> {sqr_c}")


	screen.fill(WHITE)

	# draw the axes
	pygame.draw.line(screen, BLACK, (0,HEIGHT//2), (WIDTH, HEIGHT//2))
	pygame.draw.line(screen, BLACK, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

	pygame.draw.circle(screen, GRAY, orig_coords, 3)
	pygame.draw.circle(screen, RED,  sqr_coords,  3)

	pygame.display.flip()
