from PIL import Image
from PIL.ImageColor import getrgb

def hsv(scaled_iters):
	hue = scaled_iters//SAT_RANGE
	satn = scaled_iters % SAT_RANGE
	satn = 100-satn if hue%2==0 else (100-(SAT_RANGE-1))+satn

	if scaled_iters >= ITER_LIMIT/2: hue = (HUE_RANGE-1) - (hue - HUE_RANGE)

	return getrgb(f"hsv({hue},{satn}%,100%)")


SAT_RANGE 		= 101
HUE_RANGE   	= 361
ITER_LIMIT  	= SAT_RANGE * HUE_RANGE * 2
#COLOUR_RANGE	= 361

# x-axis is hue, y-axis is saturation
WIDTH,HEIGHT= 900,SAT_RANGE

colour_img	= Image.new("RGB", (WIDTH,HEIGHT))
colours		= colour_img.load()

iters = 0
for x in range(0,WIDTH,2):
	for y in range(0,HEIGHT,1):
		colours[x,y] = hsv(iters)
		iters = (iters+1)%ITER_LIMIT

	if x!= WIDTH-1:
		x += 1
		for y in range(HEIGHT-1,-1,-1):
			colours[x,y] = hsv(iters)
			iters = (iters+1)%ITER_LIMIT

colour_img.save(f"hsvrange_v2_{WIDTH}x{HEIGHT}.png")
