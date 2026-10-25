"""Build the elytra decal datapack + resource pack from decals.json and decals/*.png.

Usage:
  python build.py                      -> writes out/<title> DP.zip and out/<title> RP.zip
  python build.py --install "<world>"  -> also copies the DP zip into <world>/datapacks/
                                          and the RP zip into the game's resourcepacks/

How it works in game:
  * Rename an elytra in an anvil to one of the decal names (e.g. "Star") and equip it or
    hold it: the datapack sets its equippable asset_id + item_model.  Rename to "Default"
    to get the vanilla look back.
  * Operators can also run /function <namespace>:give/<id>.
  * The resource pack renders the decal as a second wings layer on top of the vanilla
    wings (so capes still show through), and gives the item a badged icon.
"""
import json, shutil, sys, zipfile
from pathlib import Path
from PIL import Image, ImageColor

ROOT = Path(__file__).parent
SPEC = json.loads((ROOT / 'decals.json').read_text())
NS = SPEC['namespace']
TITLE = SPEC['pack_title']
OUT = ROOT / 'out'
GAME_DIR = Path.home() / 'Library/Application Support/minecraft'

DP_FORMAT = [121, 0]            # 26.3 data pack format
RP_FORMAT_MIN, RP_FORMAT_MAX = [69, 0], [97, 1]   # 1.21.9 .. 26.3 resource pack formats

ELYTRA_SOUND = 'minecraft:item.armor.equip_elytra'
SLOTS = ['armor.chest', 'weapon.mainhand', 'weapon.offhand']


def equippable(asset_id):
    return {'slot': 'chest', 'equip_sound': ELYTRA_SOUND, 'asset_id': asset_id, 'damage_on_hurt': False}


def equippable_snbt(asset_id):
    return ('{slot:"chest",equip_sound:"%s",asset_id:"%s",damage_on_hurt:false}' % (ELYTRA_SOUND, asset_id))


def j(obj):
    return json.dumps(obj, indent=2) + '\n'


def description(suffix):
    return [
        {'text': TITLE, 'color': 'aqua', 'bold': True},
        {'text': f' {suffix}', 'color': 'gray', 'bold': False},
    ]


def build_datapack(decals):
    """Generic data pack: any elytra renamed to a lowercase id gets asset <NS>:<id>.
    Adding a decal later only needs a new resource pack, the data pack never changes.
    Checked slots: chest, both hands, hotbar and main inventory (so the icon updates right
    after the anvil). The wings are re-applied whenever another pack resets them."""
    files = {}
    files['pack.mcmeta'] = j({'pack': {'min_format': DP_FORMAT, 'max_format': DP_FORMAT, 'description': description('(data pack)')}})
    files['data/minecraft/tags/function/load.json'] = j({'values': [f'{NS}:load']})
    files[f'data/{NS}/function/load.mcfunction'] = (
        f'tellraw @a [{{"text":"[{TITLE}] ","color":"aqua","bold":true}},'
        f'{{"text":"loaded. Rename an elytra to a decal id (e.g. {", ".join(d["id"] for d in decals[:4])}) or Default","color":"gray"}}]\n')
    files[f'data/{NS}/advancement/elytra_changed.json'] = j({
        'criteria': {'elytra_changed': {'trigger': 'minecraft:inventory_changed',
                                        'conditions': {'items': [{'items': 'minecraft:elytra'}]}}},
        'rewards': {'function': f'{NS}:on_elytra_changed'},
    })
    files[f'data/{NS}/function/revoke.mcfunction'] = f'advancement revoke @a only {NS}:elytra_changed\n'  # scheduled: no @s

    slots = [('armor.chest', 'equipment.chest'), ('weapon.mainhand', 'equipment.mainhand'), ('weapon.offhand', 'equipment.offhand')]
    slots += [(f'hotbar.{i}', f'Inventory[{{Slot:{i}b}}]') for i in range(9)]
    slots += [(f'inventory.{i}', f'Inventory[{{Slot:{i + 9}b}}]') for i in range(27)]
    lines = [f'schedule function {NS}:revoke 1t']
    lines += [f'function {NS}:check {{slot:"{slot}",path:"{path}"}}' for slot, path in slots]
    files[f'data/{NS}/function/on_elytra_changed.mcfunction'] = '\n'.join(lines) + '\n'

    # item_model is a default component on every item, so setting it back to minecraft:elytra leaves a clean item
    reset = ('{type:"minecraft:set_components",components:{"minecraft:equippable":%s,"minecraft:item_model":"minecraft:elytra"}}'
             % equippable_snbt('minecraft:elytra'))
    icon_reset = '{type:"minecraft:set_components",components:{"minecraft:item_model":"minecraft:elytra"}}'
    check = [
        '$execute unless items entity @s $(slot) minecraft:elytra run return 0',
        f'$execute if items entity @s $(slot) minecraft:elytra[minecraft:custom_name="Default"] run return run item modify entity @s $(slot) {reset}',
        f'$execute if items entity @s $(slot) minecraft:elytra[minecraft:custom_name="default"] run return run item modify entity @s $(slot) {reset}',
        # name removed again: back to vanilla wings + icon
        f'$execute if items entity @s $(slot) minecraft:elytra[!minecraft:custom_name] if data entity @s $(path).components."minecraft:item_model" run return run item modify entity @s $(slot) {reset}',
        '$execute unless items entity @s $(slot) minecraft:elytra[minecraft:custom_name] run return 0',
        f'$data modify storage {NS}:tmp name set from entity @s $(path).components."minecraft:custom_name"',
        f'$data modify storage {NS}:tmp slot set value "$(slot)"',
        f'$data modify storage {NS}:tmp path set value "$(path)"',
        f'data modify storage {NS}:tmp ok set value 0b',
        f'function {NS}:apply with storage {NS}:tmp',
        # apply only parses for a valid id; otherwise the name belongs to another pack or is junk:
        # drop a stale icon of ours and leave the wings alone
        f'execute if data storage {NS}:tmp {{ok:1b}} run return 1',
        f'$execute if data entity @s $(path).components."minecraft:item_model" run item modify entity @s $(slot) {icon_reset}',
    ]
    files[f'data/{NS}/function/check.mcfunction'] = '\n'.join(check) + '\n'
    apply = [
        # re-apply whenever the wings are not ours (another pack may have reset them)
        '$execute unless data entity @s $(path).components."minecraft:equippable"{asset_id:"%s:$(name)"} run item modify entity @s $(slot) '
        '{type:"minecraft:set_components",components:{"minecraft:equippable":{slot:"chest",equip_sound:"%s",asset_id:"%s:$(name)",damage_on_hurt:false},'
        '"minecraft:item_model":"%s:$(name)"}}' % (NS, ELYTRA_SOUND, NS, NS),
        f'data modify storage {NS}:tmp ok set value 1b',
    ]
    files[f'data/{NS}/function/apply.mcfunction'] = '\n'.join(apply) + '\n'

    for d in decals:
        asset = f'{NS}:{d["id"]}'
        files[f'data/{NS}/function/give/{d["id"]}.mcfunction'] = (
            f'give @s minecraft:elytra[minecraft:custom_name="{d["id"]}",minecraft:item_model="{asset}",'
            f'minecraft:equippable={equippable_snbt(asset)}]\n')
    return files


def badge_icon(color):
    """Vanilla elytra icon with a small coloured badge on each wing."""
    icon = Image.open(ROOT / 'vanilla' / 'elytra_item.png').convert('RGBA')
    rgba = ImageColor.getrgb(color) + (255,)
    for (x0, y0) in [(2, 5), (10, 5)]:
        for dx in range(4):
            for dy in range(4):
                if icon.getpixel((x0 + dx, y0 + dy))[3] > 0:
                    icon.putpixel((x0 + dx, y0 + dy), rgba)
    return icon


def build_resourcepack(decals):
    files = {}
    files['pack.mcmeta'] = j({'pack': {'min_format': RP_FORMAT_MIN, 'max_format': RP_FORMAT_MAX, 'description': description('(resource pack)')}})
    for d in decals:
        png = ROOT / 'decals' / f'{d["id"]}.png'
        img = Image.open(png).convert('RGBA')
        if img.size[0] != 2 * img.size[1]:
            sys.exit(f'{png}: expected a 2:1 texture (64x32, 128x64, 256x128 ...), got {img.size}')
        if d.get('full'):
            # whole-wing texture: replaces the vanilla wings (and any cape) completely
            layers = [{'texture': f'{NS}:{d["id"]}'}]
        else:
            # decal: drawn on top of the vanilla wings, capes still show through
            layers = [{'texture': 'minecraft:elytra', 'use_player_texture': True},
                      {'texture': f'{NS}:{d["id"]}'}]
        files[f'assets/{NS}/equipment/{d["id"]}.json'] = j({'layers': {'wings': layers}})
        files[f'assets/{NS}/textures/entity/equipment/wings/{d["id"]}.png'] = png.read_bytes()
        files[f'assets/{NS}/items/{d["id"]}.json'] = j({'model': {
            'type': 'minecraft:condition', 'property': 'minecraft:broken',
            'on_false': {'type': 'minecraft:model', 'model': f'{NS}:item/{d["id"]}'},
            'on_true': {'type': 'minecraft:model', 'model': 'minecraft:item/elytra_broken'},
        }})
        files[f'assets/{NS}/models/item/{d["id"]}.json'] = j({'parent': 'minecraft:item/generated',
                                                               'textures': {'layer0': f'{NS}:item/{d["id"]}'}})
        icon = ROOT / 'icons' / f'{d["id"]}.png'
        if icon.exists():
            files[f'assets/{NS}/textures/item/{d["id"]}.png'] = icon.read_bytes()
        else:
            import io
            buf = io.BytesIO(); badge_icon(d['badge']).save(buf, 'PNG')
            files[f'assets/{NS}/textures/item/{d["id"]}.png'] = buf.getvalue()
    return files


def write_zip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(name, data)
    print('wrote', path, f'({len(files)} files)')


def main():
    decals = SPEC['decals']
    missing = [d['id'] for d in decals if not (ROOT / 'decals' / f'{d["id"]}.png').exists()]
    if missing:
        sys.exit(f'missing decal PNGs in decals/: {missing} (run make_samples.py or add your own)')
    dp = OUT / f'{TITLE} DP.zip'
    rp = OUT / f'{TITLE} RP.zip'
    write_zip(dp, build_datapack(decals))
    write_zip(rp, build_resourcepack(decals))

    if '--install' in sys.argv:
        world = Path(sys.argv[sys.argv.index('--install') + 1])
        if not (world / 'level.dat').exists():
            sys.exit(f'{world} is not a world folder (no level.dat)')
        (world / 'datapacks').mkdir(exist_ok=True)
        shutil.copy2(dp, world / 'datapacks' / dp.name)
        (GAME_DIR / 'resourcepacks').mkdir(exist_ok=True)
        shutil.copy2(rp, GAME_DIR / 'resourcepacks' / rp.name)
        print('installed ->', world / 'datapacks' / dp.name)
        print('installed ->', GAME_DIR / 'resourcepacks' / rp.name)


if __name__ == '__main__':
    main()
