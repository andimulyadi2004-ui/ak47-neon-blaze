"""Generator geometri 3D AK-47 untuk Minecraft Bedrock (attachable item).

Orientasi: laras menghadap -Z (depan), gagang ke bawah (-Y), sama seperti
konvensi model item Bedrock (lihat trident.geo.json vanilla: +Y = atas).

Semua UV memakai per-face mapping ke atlas 64x64 (lihat palette.py), jadi
satu tekstur PNG dipakai untuk seluruh model.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from palette import PATCHES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "rp", "models", "entity", "ak47.geo.json")

GEO_ID = "geometry.ak47"


def face_uv(patch, w, h):
    """Ambil sub-rect dari patch, di-clamp ke ukuran patch (16x16)."""
    px, py, pw, ph = PATCHES[patch]
    w = max(0.5, min(w, pw))
    h = max(0.5, min(h, ph))
    return {"uv": [px, py], "uv_size": [w, h]}


def cube(origin, size, patch, rot=None, faces=None, inflate=None):
    sx, sy, sz = size
    if faces is None:
        faces = {
            "north": face_uv(patch, sx, sy),
            "south": face_uv(patch, sx, sy),
            "east": face_uv(patch, sz, sy),
            "west": face_uv(patch, sz, sy),
            "up": face_uv(patch, sx, sz),
            "down": face_uv(patch, sx, sz),
        }
    c = {"origin": origin, "size": size, "uv": faces}
    if rot:
        c["rotation"] = rot
    if inflate:
        c["inflate"] = inflate
    return c


def rot(px, py, pz, axis, angle):
    return {"origin": [px, py, pz], "axis": axis, "angle": angle}


# Titik pegang (gagang pistol) di ruang desain, dan skala akhir.
# Model didesain 1 unit = 1 piksel Bedrock, lalu diperkecil supaya panjang
# totalnya ~18 unit (sebanding pedang vanilla), bukan setinggi pemain.
GRIP = (0.0, -2.0, 5.0)
SCALE = 0.62


def _t(p):
    return [round((p[0] - GRIP[0]) * SCALE, 3),
            round((p[1] - GRIP[1]) * SCALE, 3),
            round((p[2] - GRIP[2]) * SCALE, 3)]


def _held_point(p):
    """Rotasi +90 derajat pada X: (x,y,z) -> (x, -z, y).

    Desain dibuat dalam pose membidik (laras ke -Z, gagang ke bawah). Model
    item Bedrock memakai +Y sebagai arah 'ke depan' (lihat trident vanilla:
    panjang batangnya di sumbu Y). Rotasi ini dieksekusi langsung ke angka
    geometri, bukan lewat rotasi bone, supaya tidak bisa tertimpa animasi.
    """
    return [p[0], -p[2], p[1]]


def normalize(cubes):
    """Geser ke titik pegang, perkecil, lalu ubah ke ruang 'held'."""
    for c in cubes:
        c["origin"] = _t(c["origin"])
        c["size"] = [round(v * SCALE, 3) for v in c["size"]]

        # rotasi lokal tetap pada sumbu X, jadi cukup pivot yang ikut berubah
        if "rotation" in c:
            c["rotation"]["origin"] = _t(c["rotation"]["origin"])

        # bake 90 derajat pada X: tukar dimensi Y dan Z
        ox, oy, oz = c["origin"]
        sx, sy, sz = c["size"]
        c["origin"] = [ox, round(-(oz + sz), 3), oy]
        c["size"] = [sx, sz, sy]

        if "rotation" in c:
            c["rotation"]["origin"] = _held_point(c["rotation"]["origin"])

        if "inflate" in c:
            c["inflate"] = round(c["inflate"] * SCALE, 3)
    return cubes


def build():
    cubes = []

    # ---------- RECEIVER / BODY ----------
    cubes.append(cube([-1.0, 0.0, -2.0], [2.0, 3.0, 8.0], "steel_dark"))
    # dust cover (atas receiver)
    cubes.append(cube([-1.0, 3.0, -2.0], [2.0, 0.7, 8.0], "steel_mid"))
    # cyan glow strip di atas dust cover
    cubes.append(cube([-0.7, 3.7, -1.4], [1.4, 0.3, 4.6], "cyan"))
    # panel line emas di sisi receiver
    cubes.append(cube([1.0, 1.1, -1.6], [0.18, 0.45, 5.2], "gold"))
    cubes.append(cube([-1.18, 1.1, -1.6], [0.18, 0.45, 5.2], "gold"))
    # charging handle
    cubes.append(cube([1.0, 2.1, 0.8], [0.9, 0.55, 1.3], "steel_light"))
    # selector switch
    cubes.append(cube([1.0, 1.9, 2.6], [0.35, 0.9, 0.5], "gold_dark"))

    # ---------- BARREL & GAS ----------
    cubes.append(cube([-0.5, 1.2, -12.0], [1.0, 1.0, 10.0], "black"))
    cubes.append(cube([-0.4, 2.6, -9.0], [0.8, 0.8, 7.0], "steel_mid"))
    # muzzle brake emas (kontras)
    cubes.append(cube([-0.75, 0.95, -14.0], [1.5, 1.5, 2.0], "gold"))
    cubes.append(cube([-0.55, 1.15, -14.6], [1.1, 1.1, 0.7], "gold_dark"))
    # front sight
    cubes.append(cube([-0.3, 2.2, -11.6], [0.6, 2.3, 0.6], "steel_light"))
    cubes.append(cube([-0.15, 4.3, -11.5], [0.3, 0.5, 0.4], "cyan"))
    # rear sight
    cubes.append(cube([-0.6, 3.7, -1.6], [1.2, 0.8, 0.9], "steel_light"))

    # ---------- HANDGUARD (kayu oranye) ----------
    cubes.append(cube([-1.1, 0.2, -9.0], [2.2, 2.3, 6.0], "wood"))
    cubes.append(cube([-1.0, 2.5, -9.0], [2.0, 0.9, 6.0], "wood_dark"))
    # ring emas di ujung handguard
    cubes.append(cube([-1.2, 0.1, -9.3], [2.4, 2.5, 0.5], "gold"))
    cubes.append(cube([-1.2, 0.1, -3.4], [2.4, 2.5, 0.5], "gold_dark"))

    # ---------- MAGAZIN MELENGKUNG (3 segmen, sudut makin besar) ----------
    cubes.append(cube([-0.9, -2.6, 0.4], [1.8, 2.6, 2.3], "steel_mid",
                      rot(0, 0, 1.4, "x", -8)))
    cubes.append(cube([-0.9, -4.9, 0.9], [1.8, 2.6, 2.2], "steel_dark",
                      rot(0, -2.4, 1.4, "x", -22)))
    cubes.append(cube([-0.9, -7.0, 1.9], [1.8, 2.4, 2.1], "steel_mid",
                      rot(0, -4.6, 1.4, "x", -36)))
    # bibir magasin emas
    cubes.append(cube([-0.95, -8.9, 3.2], [1.9, 0.7, 2.1], "gold",
                      rot(0, -6.4, 1.4, "x", -44)))
    # rusuk cyan di sisi magasin
    cubes.append(cube([0.9, -3.2, 0.6], [0.16, 4.6, 0.5], "cyan",
                      rot(0, -2.0, 1.4, "x", -20)))

    # ---------- PISTOL GRIP ----------
    cubes.append(cube([-0.8, -4.0, 4.3], [1.6, 4.4, 2.0], "wood_dark",
                      rot(0, 0, 5.2, "x", 20)))
    cubes.append(cube([-0.85, -4.2, 4.2], [1.7, 0.5, 2.1], "gold_dark",
                      rot(0, 0, 5.2, "x", 20)))
    # trigger guard + trigger
    cubes.append(cube([-0.3, -1.3, 2.4], [0.6, 0.35, 2.2], "black"))
    cubes.append(cube([-0.2, -1.0, 3.0], [0.4, 0.9, 0.4], "steel_light"))

    # ---------- STOCK (kayu, menyempit ke pangkal) ----------
    # leher stock
    cubes.append(cube([-0.75, 0.1, 5.6], [1.5, 2.0, 3.2], "wood_dark",
                      rot(0, 1.0, 6.0, "x", 3)))
    # badan stock
    cubes.append(cube([-0.9, -0.5, 8.4], [1.8, 2.9, 5.4], "wood",
                      rot(0, 1.0, 6.0, "x", 3)))
    # pangkal / buttplate emas
    cubes.append(cube([-1.0, -1.0, 13.4], [2.0, 3.6, 0.9], "gold_dark",
                      rot(0, 1.0, 6.0, "x", 3)))
    # aksen cyan di stock
    cubes.append(cube([-0.95, 1.5, 8.8], [1.9, 0.35, 4.4], "cyan",
                      rot(0, 1.0, 6.0, "x", 3)))

    normalize(cubes)

    return {
        "format_version": "1.16.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": GEO_ID,
                    "texture_width": 64,
                    "texture_height": 64,
                    "visible_bounds_width": 3,
                    "visible_bounds_height": 3,
                    "visible_bounds_offset": [0, 0.5, 0],
                },
                "bones": [
                    {
                        "name": "rightitem",
                        "binding": "q.item_slot_to_bone_name(c.item_slot)",
                        "pivot": [0, 0, 0],
                        "cubes": cubes,
                    }
                ],
            }
        ],
    }


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = build()
    with open(OUT, "w", encoding="utf-8") as f:
        # satu baris per cube supaya file tetap enak di-diff tapi tidak gemuk
        f.write(json.dumps(data, separators=(",", ":")))
        f.write("\n")
    n = len(data["minecraft:geometry"][0]["bones"][0]["cubes"])
    print("GEO  ->", os.path.relpath(OUT, ROOT), "|", n, "cubes")


if __name__ == "__main__":
    main()
