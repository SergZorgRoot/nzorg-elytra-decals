# NZorg Elytra Decals

Custom elytra "decals" for the My-N-Craft Realm: a data pack (goes into the world) plus a
resource pack (every player installs it once). Works on vanilla clients, no mods needed.
Minecraft Java 26.3.

**Download:** grab `NZorg Elytra Decals RP.zip` from the
[latest release](https://github.com/SergZorgRoot/nzorg-elytra-decals/releases/latest) and drop it
into your `resourcepacks` folder (Options → Resource Packs → Open Pack Folder), then enable it.
Short link: https://tinyurl.com/nzorg-elytra
Realm owners also need `NZorg Elytra Decals DP.zip` in the world's `datapacks` folder.
Every player gets a one-time greeting with the link on login; `/function nzorg_elytra:greet` repeats it for all.

## How players use it
1. Install the resource pack (from the release, or `out/` after building) via Options → Resource Packs.
2. Rename an elytra in an anvil to a decal id (lowercase, no spaces): `star`, `heart`, `stripes`,
   `flame`, `bolt`, `n`, `ocean`. Hold it or equip it and the decal appears on the wings.
   Rename to `Default` (or remove the name) to reset.
   The data pack is generic: it maps ANY lowercase name to `nzorg_elytra:<name>`, so new decals
   only need the resource pack updated on each client. The Realm world never needs a re-upload.
   A lowercase name with no matching decal shows invisible wings until renamed.
3. Operators can also run `/function nzorg_elytra:give/<id>` (e.g. `give/star`).

Decals are drawn as a second layer on top of the normal wings, so capes still show.

## Adding your own decals
- Put a 64x32 PNG in `decals/` (transparent everywhere except the wing face, roughly x 34-45, y 3-21;
  see `vanilla/elytra_wings.png` for the layout, or edit the ASCII art in `make_samples.py`).
- Add an entry to `decals.json` (`id` = file name = anvil name, `badge` = icon colour).
- Rebuild: `python build.py --install "<path to world>"` (needs Pillow: `pip install Pillow`).

## Testing locally
`build.py --install` copies the data pack into `<world>/datapacks/` and the resource pack into
`~/Library/Application Support/minecraft/resourcepacks/`. New data packs in the folder are
enabled automatically when the world loads.

## Putting it on the Realm
Java Realms cannot push a resource pack to players, and data packs can only be added by
uploading a world. So: download the latest Realm backup, copy `out/NZorg Elytra Decals DP.zip`
into its `datapacks/` folder, upload that world to the Realm (Configure Realm → world slot →
Reset/Upload world), and send every player the RP zip.

## Full custom wing textures (not just decals)
Set `"full": true` on the entry in `decals.json` and the PNG replaces the whole wing texture
(capes are ignored for that elytra). Any 2:1 size works: 64x32, 128x64, 256x128, 512x256.
Templates to paint over are in `template/`: `elytra_64x32.png`, `elytra_512x256.png` and
`guide_512x256.png` (shows the wing face; it is mirrored onto both wings). Any Minecraft
cape texture (64x32) also works as-is, since elytra use the cape layout.
Example: `ocean` is a full texture (rename an elytra to `Ocean`).

## Re-uploading after a data pack change
`./prepare_upload.sh "<freshly downloaded Realm backup>"` creates `<world> UPLOAD` next to it with
never-visited chunks pruned (MCA Selector, InhabitedTime = 0) and both data packs in place.
Upload that one. Only needed when a data pack changes; new decals need just the resource pack.

## Included designs from Custom Elytra by XAVI333
The 53 wing textures and icons of "Custom Elytra" v1.3 by XAVI333 (CC-BY-NC-ND-4.0) are bundled
unmodified as full-texture decals, so his pack is not needed: rename to `cobalt`, `cherry_blossom`,
`minecon_2016`, `zombie_horse` ... (ids = his texture names, see decals.json). Private use only.
