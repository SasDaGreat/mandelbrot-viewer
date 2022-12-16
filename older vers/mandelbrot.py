import turtle

# try using fractional powers sometime?
# turn off tracer until drawing for an entire iterations list is done
# make the program go through a number of iterations each time (probably incrementing a geometric progression upto infinity) to show the folding in of the set
# better precision with 2 decimal places
# convert turtle pos (x,y) to complex(x,y) and use it to do meth

'''
The entire set lies inside a square of length 4 centered at the origin.
Length is from -2 to 2.

Let us make a graph with values from 2.5 to -2.5 for both planes.
Ratio will be 5:800 for 800 as width, or 1:160.

800/160 = 5, 400/160 = 2.5, and so on.

Let us take 640 as width, because then we'll have a graph from 2i to -2i,
as 640/160 = 2.
'''

WIDTH,HEIGHT = 800,640
SCALED_WIDTH = 5
SCALE_RATIO  = WIDTH/SCALED_WIDTH
#ITERATIONS   = [5,20,50,500,4000]
ITERATIONS   = 500

scr = turtle.Screen()
scr.setup(WIDTH,HEIGHT)
scr.title("The Mandelbrot Set")
scr.bgcolor("gray")

pointer = turtle.Turtle()
pointer.ht()
pointer.up()
pointer.speed(0)

turtle.tracer(0,0)
for x in range(-WIDTH//2, (WIDTH//2)+1):
	scaled_x = x/SCALE_RATIO
	for y in range(-HEIGHT//2, (HEIGHT//2)+1):
		scaled_y = y/SCALE_RATIO

		z = 0
		c = complex(scaled_x,scaled_y)

		for i in range(ITERATIONS):
			z = z**4 + c

			if abs(z.real) > 2 or abs(z.imag) > 2:
				pointer.color("white")
				break
		else:
			pointer.color("black")

		pointer.goto(x,y)
		pointer.down()
		#pointer.fd(1)
		pointer.goto(x+1,y)
		pointer.up()

	turtle.update()
	print(f"one line updated, x = {x}, scaled x is {scaled_x}")
