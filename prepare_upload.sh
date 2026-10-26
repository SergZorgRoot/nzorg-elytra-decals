#!/bin/zsh
# Usage: ./prepare_upload.sh "<path to freshly downloaded Realm backup world>"
# Makes "<world> UPLOAD" next to it: never-visited chunks pruned, both elytra data packs added.
set -e
SRC="$1"; [ -f "$SRC/level.dat" ] || { echo "not a world folder: $SRC"; exit 1; }
DST="${SRC} UPLOAD"
HERE="$(cd "$(dirname "$0")" && pwd)"
JAVA="$(find ~/.gradle/jdks -maxdepth 6 -type d -name Home -path '*25*' | head -1)/bin/java"
[ -x "$JAVA" ] || JAVA=java
JAR="$HERE/third_party/mcaselector-2.9.jar"
[ -f "$JAR" ] || curl -sL -o "$JAR" https://github.com/Querz/mcaselector/releases/download/2.9/mcaselector-2.9.jar
rm -rf "$DST"; cp -Rc "$SRC" "$DST"; rm -f "$DST/session.lock"; rm -rf "$DST/gc-logs"
for dim in overworld the_nether the_end; do
  D="$DST/dimensions/minecraft/$dim"; [ -d "$D/region" ] || continue
  echo "pruning never-visited chunks: $dim"
  "$JAVA" -Xmx8G -jar "$HERE/third_party/mcaselector-2.9.jar" --mode delete --world "$DST" \
    --region "$D/region" --poi "$D/poi" --entities "$D/entities" --query "InhabitedTime < 1" >/dev/null 2>&1
done
mkdir -p "$DST/datapacks"
rm -rf "$DST/datapacks/NZorg Elytra Decals DP.zip"  # Realm backups store it unpacked under the zip name
cp "$HERE/out/NZorg Elytra Decals DP.zip" "$DST/datapacks/"
echo "ready: $DST"; du -sh "$DST"; ls "$DST/datapacks"
