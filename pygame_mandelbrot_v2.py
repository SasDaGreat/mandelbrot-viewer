import pygame
pygame.init()

'''
All the math for this thing was done, yes,
but I don't know how the fuck I can make this readable and understandable.
Don't try to decrypt this, only Poseidon knows how this works if I manage to finish this.
'''

# pygame coordinates count from 0,0 being the topleft of the screen, and WIDTH,HEIGHT being the bottomright.
# there are two planes: the pygame graph and the complex plane graph, which is not *always* centered at 0 once zoomed in.
# to zoom in, two points must be clicked: first to determine x,y coords of the topleft corner of the zoomed screen,
#  and another coordinate to determine the x coordinate of the bottomright corner
#  (the y coordinate will be found by scaling down the pygame screen to that corner, since width is dependent on length)
# to find the complex plane coords of a clicked (or well, any) point, i need:
#  the topleft coords, the bottomright coords, the current length_scale_ratio (can be easily calculated)
# length_scale_ratio = WIDTH/abs(x2 - x1), where x2 is the bottomright x, x1 is the topleft x
# x3 = x1 + ((pygame_x3/WIDTH) * abs(x2 - x1)), where x3 is the complex plane coords of the clicked coords,
#  pygame_x3 is the raw clicked x coordinate i get
# y3 = y1 - ((pygame_y3/HE5IGHT) * abs(y2 - y1)); note the negative sign here
# x2 =/= x1, so i'll need to make some kind of protection for that
# i can convert the x and y values to a complex number right before doing the calculation, or before if i want
# starting with complex because 1) why not, 2) should be easier to add and subtract

# print the coordinates of topleft and bottomright corners whenever zooming in, along with other stuff
# initialise length_scale_ratio in the while loop itself, 
#  and at the end of each mandelbrot drawing do a event checker loop that sends back to the start
# scale no_of_iterations according to length_scale_ratio?
# turn the coordinates formula calculating from topleft into a function?



POWER     = 2
# MAX_ITERS' purpose is to make the colour changes between pixels more visible, and not a continuous barely recognisable shade
# but then i limit my number of possible colours to MAX_ITERS, something like 40...
MAX_ITERS = 40
DISPLAY   = WIDTH,HEIGHT = 800,600
# i need to increase the number of iterations every time i zoom in to get more accurate results
# the only variable that changes accurately as the amount zoomed in by changes is length_scale_ratio
# length_scale_ratio/iter_scale_ratio will scale the length_scale_ratio down to a number that can be added to iterations
# 60 should work fine
ITER_SCALE_RATIO = 1000

# number of iterations will probably be scaled once i get to 
no_of_iterations = 25
# y or imaginary values of topleft and bottomright corners still not initialised
topleft_x     = -2
bottomright_x = 2
# real is the x value of each pair of coordinates
actual_width  = abs(bottomright_x - topleft_x)
length_scale_ratio   = WIDTH/actual_width
# whereas imag is the y coordinate
actual_height = HEIGHT/length_scale_ratio	
topleft_coords = complex(topleft_x, actual_height/2)
#bottomright_coords = complex(bottomright_x, -actual_height/2)
current_colour = pygame.Color(0,0,0)	# initialised as black

screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("The Mandelbrot Set")
screen.fill((100,100,100))


while 1:
	# real is the x value of each pair of coordinates
	actual_width  = abs(bottomright_x - topleft_coords.real)
	length_scale_ratio   = WIDTH/actual_width
	actual_height = HEIGHT/length_scale_ratio
	#bottomright_coords = complex(bottomright_x, topleft_coords.imag - actual_height/2)
	print("Actual width: {0}; actual height: {1}".format(actual_width,actual_height))

	no_of_iterations += int(length_scale_ratio//ITER_SCALE_RATIO)
	print("Number of iterations: {}".format(no_of_iterations))

	for pygame_x in range(WIDTH+1):
		# selected x coordinate is topleft_x + ratio_of_pygamex_to_totalwidth * actual_totalwidth
		current_x = topleft_coords.real + ((pygame_x/WIDTH) * actual_width)
		# in all of those calculations, i count from the topleft point as reference as that's what pygame does

		for pygame_y in range(HEIGHT+1):
			# selected y coordinate is... you get the gist.
			current_y = topleft_coords.imag - ((pygame_y/HEIGHT) * actual_height)
			#print(current_y)

			# initialising c and z(0)
			c = complex(current_x,current_y)
			z = c

			'''if pygame_x == 0 and pygame_y == 0:
				print("Topleft_calculated coords: {0}; Topleft_real coords: {1}".format(topleft_coords,c))
			elif pygame_x == WIDTH and pygame_y == HEIGHT:
				print("Bottomright_calculated coords: {0}; Bottomright_real_coords: {1}".format(complex(bottomright_x, topleft_coords.imag - actual_height), c))'''


			for current_iteration in range(no_of_iterations):
				z = pow(z,POWER) + c

				if abs(z.real) > 2 or abs(z.imag) > 2:
					# now, map iterations exited at to a number in the range 0-255 for a hue value
					# if i > MAX_ITERS, loop it back to get a repeating loop of colours as the iterations exited at gets bigger

					# only the hue differs, changing the entire colour scale
					#hue_value = (1 - ((current_iteration % MAX_ITERS)/MAX_ITERS)) * 255
					hue_value = ((current_iteration % MAX_ITERS)/MAX_ITERS) * 255	
					# 1 - fraction for bluish background, fraction only for reddish background (cooler imo :/)
					current_colour.hsla = (hue_value, 100, 50, 100)

					break
			else:
				current_colour.hsla = (0,100,0,100)				# BLACK

			screen.set_at((pygame_x, pygame_y), current_colour)

		pygame.display.flip()

	pygame.image.save(screen,f"mandelbrotzoom_{POWER}_{MAX_ITERS}_{no_of_iterations}_{topleft_coords.real}x{topleft_coords.imag}y_{length_scale_ratio}_{actual_height}.png")

	print("\nNow choose two points to zoom in.")

	topleft_coords_chosen = False
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if not topleft_coords_chosen:
					tl_pygame_x, tl_pygame_y = event.pos
					# pygame_xy vars are always temporary, but these topleft_pygame values will be needed
					# set the selected coordinate white - white's not part of the mandelbrot set colours, so no problem
					screen.set_at((tl_pygame_x, tl_pygame_y), (255,255,255))
					pygame.display.flip()

					new_topleft_x = topleft_coords.real + ((tl_pygame_x/WIDTH) * actual_width)
					new_topleft_y = topleft_coords.imag - ((tl_pygame_y/HEIGHT) * actual_height)

					topleft_coords_chosen = True

				else:
					br_pygame_x = event.pos[0]
					# if x2 = x1, then scale = WIDTH/(x2-x1) = WIDTH/0, which would result in an error
					# let's take care of that by shifting the x just one pygame pixel right
					if br_pygame_x == tl_pygame_x: br_pygame_x += 1
					# again, set the selected coordinate white
					screen.set_at(event.pos, (255,255,255))
					pygame.display.flip()

					bottomright_x = topleft_coords.real + ((br_pygame_x/WIDTH) * actual_width)

					# now that our work with the old topleft_coords are done,
					#  we can now move the topleft_coords to the topleft_coords of the new zoomed screen
					topleft_coords = complex(new_topleft_x, new_topleft_y)
					print("Topleft coords: {}".format(topleft_coords))
					print("Bottomright coords: {0}; Actual pygame x: {1}".format(bottomright_x, br_pygame_x))
					
					screen.fill((100,100,100))
					running = False
					break
			elif event.type == pygame.QUIT: exit()

