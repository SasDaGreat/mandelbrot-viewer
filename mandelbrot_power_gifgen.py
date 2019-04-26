import pygame
pygame.init()


ITERATIONS = 300 
MAX_ITERS  = 40
GRAY  = (100,100,100)
DISPLAY = WIDTH,HEIGHT = 800,600
SCALED_WIDTH  = 4			# render a lesser portion of the right side?
SCALE_RATIO   = WIDTH/SCALED_WIDTH
#SCALED_HEIGHT = HEIGHT/SCALE_RATIO 

current_colour = pygame.Color(0,0,0)	# initialised as black
#current_colour.hsla = (0,100,50,100)

screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("The Mandelbrot Set - Power Edition")
screen.fill(GRAY)

power_min, power_max = 0, 600

for unscaled_power in range(power_min, power_max+1):
	POWER = unscaled_power/100

	for pygame_original_x in range(WIDTH):
		# convert pygame_x to a graphical_x
		original_x = pygame_original_x - WIDTH//2
		scaled_x = original_x/SCALE_RATIO

		for pygame_original_y in range(HEIGHT):
			# convert pygame_y to a graphical_y
			original_y = (HEIGHT//2) - pygame_original_y
			scaled_y = original_y/SCALE_RATIO

			z = 0
			c = complex(scaled_x,scaled_y)
			#z = c

			for i in range(ITERATIONS):
				z = pow(z, POWER) + c

				if abs(z.real) > 2 or abs(z.imag) > 2:
					exited_at = i
					# now, map iterations exited at to a number in the range 0-255 for a hue value

					hue_value = (1 - ((i % MAX_ITERS)/MAX_ITERS)) * 255
					current_colour.hsla = (hue_value, 100, 50, 100)

					break
			else:
				current_colour.hsla = (0,100,0,100)				# BLACK

			screen.set_at((pygame_original_x, pygame_original_y), current_colour)

	pygame.display.flip()
	pygame.image.save(screen,f"mp_{unscaled_power}.png")

#filenames = ["mp_{}.png".format(power) for power in range(power_min, power_max+1)]
#images    = [Image.open(file) for file in filenames]
# creating the list of images generated

#images[0].save(f"mandelpower_{power_min}to{power_max}_at{ITERATIONS}_{WIDTH}x{HEIGHT}_{MAX_ITERS}.gif", save_all=True, append_images=images[1:], duration=100, loop=0)
