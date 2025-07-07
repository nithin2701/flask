# You can replace this with your real logo
from PIL import Image, ImageDraw
img = Image.new('RGBA', (180, 60), (255, 215, 0, 255))
d = ImageDraw.Draw(img)
d.text((20, 15), "RK GOLD", fill=(80, 60, 0))
img.save('static/logo.png')
