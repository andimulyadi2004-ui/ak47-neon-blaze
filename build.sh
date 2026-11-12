#!/usr/bin/env bash
# Build add-on AK-47 Neon Blaze jadi .mcaddon / .mcpack
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/dist"
NAME="AK47_NeonBlaze"

cd "$ROOT"

echo "==> 1/4 generate tekstur (SVG -> PNG)"
python3 tools/gen_texture.py

echo "==> 2/4 generate geometri 3D"
python3 tools/gen_model.py

echo "==> 3/4 generate ikon & pack icon (SVG -> PNG)"
python3 tools/gen_icon.py

echo "==> 4/4 validasi"
python3 tools/validate.py

rm -rf "$OUT"
mkdir -p "$OUT/_pack/ak47_bp" "$OUT/_pack/ak47_rp"

cp -r src/bp/. "$OUT/_pack/ak47_bp/"
cp -r src/rp/. "$OUT/_pack/ak47_rp/"

# buang artefak yang tidak boleh ikut terpaket
find "$OUT/_pack" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "$OUT/_pack" -name ".DS_Store" -delete

( cd "$OUT/_pack" && zip -qr "../${NAME}_BP.mcpack" ak47_bp -x ".*" )
( cd "$OUT/_pack" && zip -qr "../${NAME}_RP.mcpack" ak47_rp -x ".*" )
( cd "$OUT/_pack" && mkdir -p combined && rm -rf combined/* && \
  cp -r ak47_bp ak47_rp combined/ && \
  cd combined && zip -qr "../../${NAME}.mcaddon" ak47_bp ak47_rp -x ".*" )
rm -rf "$OUT/_pack"

echo
echo "==> selesai"
ls -lh "$OUT"/*.mcaddon "$OUT"/*.mcpack
