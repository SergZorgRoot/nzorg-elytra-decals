"""Full wing texture 'sergzorg': black-shaded lattice wings (Cobalt-style pattern, drawn from scratch
over the vanilla silhouette and shading) to match the SergZorg skin (#0a0a0a body, white face)."""
from PIL import Image
van = Image.open('vanilla/elytra_wings.png').convert('RGBA')
out = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
for y in range(32):
    for x in range(64):
        r, g, b, a = van.getpixel((x, y))
        if a == 0:
            continue
        lum = (r + g + b) / (3 * 255)            # keep vanilla's light/shadow modelling
        base = 8 + int(lum * 30)                # 8..38: very dark greys
        # diagonal lattice: 2px cells, alternating; lattice lines a touch lighter
        cell = ((x // 2) + (y // 2)) % 2
        v = base + (16 if cell else 0)
        if (x + y) % 4 == 0:
            v += 10                             # thin highlight threads
        # leading edge (top rows of the wing face) slightly lighter, like a rim light
        if 2 <= y <= 4 and 30 <= x <= 46:
            v += 18
        v = max(0, min(72, v))
        out.putpixel((x, y), (v, v, v + 3, 255)) # hint of cold blue in the black
out.save('decals/sergzorg.png')
print('decals/sergzorg.png written')
