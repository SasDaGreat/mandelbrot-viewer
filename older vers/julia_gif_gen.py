import pygame
from PIL import Image
pygame.init()


POWER = 2
ITERATIONS = 500 
MAX_ITERS  = 50
GRAY  = (100,100,100)
DISPLAY = WIDTH,HEIGHT = 800,600
SCALED_WIDTH  = 4
SCALE_RATIO   = WIDTH/SCALED_WIDTH
SCALED_HEIGHT = HEIGHT/SCALE_RATIO 

current_colour = pygame.Color(0,0,0)	# initialised as black
current_colour.hsla = (0,100,50,100)

screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("The Julia Set")
screen.fill(GRAY)

C_y = 0
for pygame_C_x in range(-WIDTH//2,(WIDTH//2)+1):
	C_x = pygame_C_x/SCALE_RATIO		# scale down pygame coords to the complex plane coords
	C = complex(C_x,0)

	for pygame_original_x in range(WIDTH):
		# convert pygame_x to a graphical_x
		original_x = pygame_original_x - WIDTH//2
		scaled_x = original_x/SCALE_RATIO

		for pygame_original_y in range(HEIGHT):
			# convert pygame_y to a graphical_y
			original_y = (HEIGHT//2) - pygame_original_y
			scaled_y = original_y/SCALE_RATIO

			z = complex(scaled_x,scaled_y)

			for i in range(ITERATIONS):
				z = pow(z, POWER) + C

				if abs(z.real) > 2 or abs(z.imag) > 2:
					exited_at = i
					# now, map iterations exited at to a number in the range 0-255 for a hue value
					# let's assume > MAX_ITERS iters corresponds to blue colour

					if i > MAX_ITERS: 
						current_colour.hsla = (255,100,50,100)	# BLUE
					else: 
						hue_value = (1 - (i/MAX_ITERS)) * 255	# only the hue differs, changing the entire colour scale
						# 1 - fraction for bluish background, fraction only for reddish background (cooler imo :/)
						current_colour.hsla = (hue_value, 100, 50, 100)
					break
			else:
				current_colour.hsla = (0,100,0,100)				# BLACK

			screen.set_at((pygame_original_x, pygame_original_y), current_colour)

	pygame.display.flip()
	pygame.image.save(screen,f"j_{pygame_C_x+WIDTH//2}.png")	# pygame_C_x + WIDTH//2 should give a consistent 0 to WIDTH number

filenames = ["j_{}.png".format(i) for i in range(WIDTH+1)]
images    = [Image.open(file) for file in filenames]
# creating the list of images generated

images[0].save(f"julia_{-WIDTH//2}to{WIDTH//2}_{C_y}_{POWER}_{MAX_ITERS}.gif", save_all=True, append_images=images[1:], duration=100, loop=0)
