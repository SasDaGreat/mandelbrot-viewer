import pygame
from time import sleep as zzz
pygame.init()

def hsv(scaled_iters):
	hue = (scaled_iters//SAT_RANGE) % HUE_RANGE
	satn = scaled_iters % SAT_RANGE
	satn = 100-satn if hue%2==0 else (100-(SAT_RANGE-1))+satn

	if scaled_iters >= ITER_LIMIT/2: hue = (HUE_RANGE-1) - hue

	c = pygame.Color(0,0,0)
	c.hsva = (hue, satn, 100, 100)
	return c

def update(x,y,i):
	pygame.display.flip()
	cc = hsv(i)
	zzz( (cc.hsva[0]**50)/10**129.85 )        # integration says it'll take 12.15 seconds to reach 360 hue, accounting for evaluation delay
	# pygame printing takes 3.05 seconds, so total time should be 15.20 seconds
	# ...actually takes 50 seconds
	screen.set_at((x,y), cc)
	return (i+1)%ITER_LIMIT


SAT_RANGE 		= 76
HUE_RANGE   	= 361
ITER_LIMIT  	= SAT_RANGE * HUE_RANGE * 2
#COLOUR_RANGE	= 361

# x-axis is hue, y-axis is saturation
WIDTH,HEIGHT= 900,SAT_RANGE
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("HSV shite")
screen.fill((100,100,100))


iters = 0
for x in range(0,WIDTH,2):
	for y in range(0,HEIGHT,1): iters = update(x,y,iters)

	if x!= WIDTH-1:
		x += 1
		for y in range(HEIGHT-1,-1,-1): iters = update(x,y,iters)

pygame.image.save(screen,f"hsvrange_vPygame_{WIDTH}x{HEIGHT}.png")

