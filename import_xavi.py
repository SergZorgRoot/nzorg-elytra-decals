"""Import the XAVI333 'Custom Elytra' wing textures + icons as full-texture decals (unmodified, credited)."""
import json, shutil, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).parent
rp = ROOT / 'third_party/originals/Custom Elytra RP (v1.3) [1.21.9 - 26.3].zip'
spec = json.loads((ROOT / 'decals.json').read_text())
have = {d['id'] for d in spec['decals']}
(ROOT / 'icons').mkdir(exist_ok=True)
added = []
with zipfile.ZipFile(rp) as z:
    names = z.namelist()
    for n in sorted(names):
        if not n.startswith('assets/custom_elytra/textures/entity/equipment/wings/') or not n.endswith('.png'):
            continue
        did = Path(n).stem
        if did in have:
            print('skip (id exists):', did); continue
        (ROOT / 'decals' / f'{did}.png').write_bytes(z.read(n))
        icon = f'assets/custom_elytra/textures/item/{did}.png'
        if icon in names:
            (ROOT / 'icons' / f'{did}.png').write_bytes(z.read(icon))
        spec['decals'].append({'id': did, 'name': did, 'badge': '#8888ff', 'full': True, 'source': 'XAVI333'})
        added.append(did)
(ROOT / 'decals.json').write_text(json.dumps(spec, indent=2) + '\n')
print(f'imported {len(added)}:', ', '.join(added))
