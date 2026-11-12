"""Generate atlas tekstur AK-47 sebagai SVG, lalu konversi ke PNG.

Minecraft hanya menerima PNG, jadi SVG dibuat dulu (mudah diedit / di-diff),
baru di-rasterise. Setiap patch 16x16 diisi pixel-art deterministik supaya
tidak terlihat flat dan tetap tajam saat di-scale.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from palette import ATLAS, PATCHES, COLORS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SVG = os.path.join(ROOT, "art", "ak47_atlas.svg")
OUT_PNG = os.path.join(ROOT, "src", "rp", "textures", "items", "ak47.png")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def build_svg():
    rnd = random.Random(20261112)
    rects = []
    grid = {}

    for name, (px, py, pw, ph) in PATCHES.items():
        base, light, dark = (hex_to_rgb(c) for c in COLORS[name])
        for y in range(ph):
            for x in range(pw):
                r = rnd.random()
                if r < 0.18:
                    c = light
                elif r < 0.38:
                    c = dark
                else:
                    c = base
                # hanya tiga tingkat warna per patch: tekstur tetap pixel-art
                # tapi jumlah run per baris kecil, jadi SVG-nya ringan
                grid[(px + x, py + y)] = rgb_to_hex(*c)

    def line(x1, y1, x2, y2, color):
        for yy in range(y1, y1 + max(1, y2 - y1)):
            for xx in range(x1, x1 + max(1, x2 - x1)):
                grid[(xx, yy)] = color

    sx, sy, sw, sh = PATCHES["steel_dark"]
    for i in range(0, sh, 5):
        line(sx, sy + i, sx + sw, sy + i + 1, COLORS["steel_dark"][2])
    sx, sy, sw, sh = PATCHES["wood"]
    for i in range(0, sh, 3):
        line(sx, sy + i, sx + sw, sy + i + 1, COLORS["wood"][2])
    sx, sy, sw, sh = PATCHES["gold"]
    for i in range(0, sh, 4):
        line(sx, sy + i, sx + sw, sy + i + 1, COLORS["gold"][2])
    sx, sy, sw, sh = PATCHES["cyan"]
    for i in range(0, sh, 4):
        line(sx, sy + i, sx + sw, sy + i + 1, COLORS["cyan"][1])

    # Gabungkan pixel sebaris yang warnanya sama jadi satu <rect> (run-length).
    for y in range(ATLAS):
        run_start = None
        run_color = None
        for x in range(ATLAS + 1):
            c = grid.get((x, y))
            if c != run_color:
                if run_color is not None:
                    rects.append(
                        '<rect x="%d" y="%d" width="%d" height="1" fill="%s"/>'
                        % (run_start, y, x - run_start, run_color)
                    )
                run_start = x
                run_color = c

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" shape-rendering="crispEdges">\n'
        '<rect width="%d" height="%d" fill="#000000" fill-opacity="0"/>\n'
        "%s\n</svg>\n"
    ) % (ATLAS, ATLAS, ATLAS, ATLAS, ATLAS, ATLAS, "\n".join(rects))
    return svg


def main():
    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    svg = build_svg()
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print("SVG  ->", os.path.relpath(OUT_SVG, ROOT), len(svg), "bytes")

    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=OUT_PNG,
                     output_width=ATLAS, output_height=ATLAS)
    print("PNG  ->", os.path.relpath(OUT_PNG, ROOT))


if __name__ == "__main__":
    main()
