from PIL import Image
from PIL.ImageDraw import Draw

WIDTH,HEIGHT = 361,1

img = Image.new("HSV",(WIDTH,HEIGHT))
drawer = Draw(img)

for x in range(WIDTH): drawer.point((x,0), (x,255,255))

img = img.resize((WIDTH,100), Image.NEAREST).convert("RGB")
img.save("test.png")