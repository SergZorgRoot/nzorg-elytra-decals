"""sergzorg (formerly green_wings): the purple wings texture hue-shifted so every purple shade becomes the matching green
shade (saturation and brightness untouched). Target hue is taken from the green icon."""
import colorsys, statistics
from PIL import Image
SRC = '/Users/zorg/Downloads/purple-wings-for-elytra-2.png'
ICON = '/Users/zorg/Downloads/green-elytra.png'
ic = Image.open(ICON).convert('RGBA')
hues = [colorsys.rgb_to_hsv(r/255, g/255, b/255)[0] for r, g, b, a in ic.get_flattened_data() if a > 0 and max(r, g, b) - min(r, g, b) > 30]
target = statistics.median(hues)
src = Image.open(SRC).convert('RGBA'); out = src.copy(); px = out.load()
src_hues = [colorsys.rgb_to_hsv(r/255, g/255, b/255)[0] for r, g, b, a in src.get_flattened_data() if a > 0 and max(r, g, b) - min(r, g, b) > 30]
shift = target - statistics.median(src_hues)
for y in range(src.height):
    for x in range(src.width):
        r, g, b, a = px[x, y]
        if a == 0: continue
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        if max(r, g, b) - min(r, g, b) > 10:            # leave greys/blacks alone
            h = (h + shift) % 1.0
        nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
        px[x, y] = (round(nr*255), round(ng*255), round(nb*255), a)
out.save('decals/sergzorg.png'); ic.save('icons/sergzorg.png')
print(f'target hue {target*360:.0f} deg, shift {shift*360:+.0f} deg; written decals/sergzorg.png + icons/sergzorg.png')
