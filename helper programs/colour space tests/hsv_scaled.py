from PIL import Image
from PIL.ImageColor import getrgb

def scale_iters(exit_iters): return (PIXELS_TO_MOVE * exit_iters)%ITER_LIMIT

def hsv(scaled_iters):
	hue = scaled_iters//SAT_RANGE
	satn = scaled_iters % SAT_RANGE
	satn = 100-satn if hue%2==0 else (100-(SAT_RANGE-1))+satn

	if scaled_iters >= ITER_LIMIT/2: hue = (HUE_RANGE-1) - (hue - HUE_RANGE)

	return getrgb(f"hsv({hue},{satn}%,100%)")


SAT_RANGE 		= 76
HUE_RANGE   	= 361		# won't be changed; we want to use as many hues as possible
ITER_LIMIT  	= SAT_RANGE * HUE_RANGE * 2
PIXELS_TO_MOVE	= (SAT_RANGE-1)/2 + 76*2
print(f"The number of possible colours in this image will be {(ITER_LIMIT/2)//PIXELS_TO_MOVE}.")

# x-axis is hue, y-axis is saturation
WIDTH,HEIGHT= 80,60
RESIZE_W 	= 800
RESIZE_H	= round((RESIZE_W/WIDTH) * HEIGHT)

colour_img	= Image.new("RGB", (WIDTH,HEIGHT))
colours		= colour_img.load()

iters = 0
for x in range(WIDTH):
	for y in range(HEIGHT):
		colours[x,y] = hsv(scale_iters(iters))
		iters += 1

colour_img = colour_img.resize((RESIZE_W, RESIZE_H), Image.NEAREST)
colour_img.save(f"hsvscaled_{PIXELS_TO_MOVE}_{SAT_RANGE}_{WIDTH}x{HEIGHT}.png")
