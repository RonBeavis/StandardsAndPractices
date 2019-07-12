from PIL import Image
import os
import sys

pngs = os.listdir('png')
os.chdir('png')
imgs = []
for p in sorted(pngs):
	if not os.path.isfile(p) or p.find('.png') == -1:
		continue
	imgs.append(Image.open(p))
im1 = imgs.pop(0)
im1.save(sys.argv[1], save_all=True, append_images=imgs, duration=int(sys.argv[2]), loop=0)

