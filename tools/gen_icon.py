"""Icon 2D (inventory) + pack icon, digambar sebagai SVG lalu di-rasterise.

Icon inventory memakai siluet samping AK-47 yang sama proporsinya dengan model
3D, jadi terlihat konsisten saat item ada di inventory vs di tangan.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "art")
RP = os.path.join(ROOT, "src", "rp")

S = 32  # ukuran icon item

# Bentuk AK-47 dilihat dari samping, dalam koordinat 0..32 (y ke bawah).
# x: 1..31 (laras ke kanan), y: 6..27
SHAPES = [
    # receiver
    ("steel_dark", 11, 12, 12, 5),
    # dust cover highlight
    ("steel_light", 11, 12, 12, 1.5),
    # laras
    ("black", 23, 13.5, 7, 1.6),
    ("black", 29, 13, 2, 2.6),
    # muzzle emas
    ("gold", 29.5, 12.6, 1.8, 3.4),
    # gas tube
    ("steel_mid", 22, 11.5, 6, 1.2),
    # handguard kayu
    ("wood", 19.5, 14.5, 6.5, 3.6),
    ("wood_dark", 19.5, 14.5, 6.5, 1.0),
    # ring emas
    ("gold", 19.2, 14.2, 0.9, 4.2),
    ("gold_dark", 25.5, 14.2, 0.9, 4.2),
    # front sight
    ("steel_light", 26.6, 9.6, 1.0, 2.4),
    ("cyan", 26.8, 9.1, 0.7, 0.7),
    # rear sight
    ("steel_light", 13.0, 10.4, 1.0, 1.8),
    # magasin melengkung (3 segmen)
    ("steel_mid", 14.2, 17.0, 3.6, 3.0),
    ("steel_dark", 14.6, 19.6, 3.4, 3.0),
    ("steel_mid", 15.3, 22.0, 3.2, 2.6),
    ("gold", 16.0, 24.2, 3.0, 1.2),
    # grip kayu
    ("wood_dark", 18.6, 17.4, 2.6, 4.4),
    ("gold_dark", 18.6, 21.0, 2.6, 1.0),
    # trigger guard
    ("black", 16.2, 16.6, 2.4, 0.8),
    ("steel_light", 16.9, 16.4, 0.8, 1.4),
    # stock
    ("wood_dark", 9.6, 13.2, 2.4, 3.0),
    ("wood", 5.0, 12.4, 4.8, 4.4),
    ("gold_dark", 4.2, 11.8, 1.2, 5.6),
    ("cyan", 5.2, 12.4, 4.4, 0.8),
    # charging handle + selector
    ("steel_light", 20.2, 12.6, 1.6, 0.9),
    ("gold_dark", 12.4, 14.6, 0.9, 1.6),
]

NEON = {
    "steel_dark": "#23262E",
    "steel_mid": "#3A3F4B",
    "steel_light": "#7C869B",
    "wood": "#FF8A3D",
    "wood_dark": "#C4561C",
    "gold": "#FFD25E",
    "gold_dark": "#B8862A",
    "cyan": "#5CF2F8",
    "black": "#14171D",
}


def silhouette_rects(scale=1.0, ox=0.0, oy=0.0):
    out = []
    for color, x, y, w, h in SHAPES:
        out.append(
            '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
            % (ox + x * scale, oy + y * scale, w * scale, h * scale, NEON[color])
        )
    return "\n".join(out)


def item_icon_svg():
    # outline gelap 1px supaya terbaca di slot inventory terang maupun gelap
    body = silhouette_rects(1.0, 0.55, 0.55)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" shape-rendering="crispEdges">\n'
        '<g fill="#05070A" opacity="0.55" transform="translate(1.6,1.6)">%s</g>\n'
        "<g>%s</g>\n</svg>\n"
    ) % (S, S, S, S, silhouette_rects(1.0, 0.55, 0.55), body)
    return svg


def pack_icon_svg():
    W = 128
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{w}" '
        'viewBox="0 0 {w} {w}" shape-rendering="crispEdges">\n'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#151A24"/>'
        '<stop offset="0.55" stop-color="#1E2533"/>'
        '<stop offset="1" stop-color="#0B0E14"/></linearGradient></defs>\n'
        '<rect width="{w}" height="{w}" rx="18" fill="url(#g)"/>\n'
        '<rect x="5" y="5" width="{i}" height="{i}" rx="14" fill="none" '
        'stroke="#F2C14E" stroke-width="2.5" opacity="0.9"/>\n'
        '<ellipse cx="64" cy="66" rx="44" ry="18" fill="#35E0E8" opacity="0.16"/>\n'
        '<g transform="translate(6,26) scale(3.7)">{gun}</g>\n'
        '<rect x="0" y="103" width="{w}" height="25" fill="#0B0E14" opacity="0.88"/>\n'
        '<text x="64" y="121" font-family="monospace" font-size="15" '
        'font-weight="bold" fill="#F2C14E" text-anchor="middle" '
        'letter-spacing="1.5">AK-47</text>\n'
        "</svg>\n"
    ).format(w=W, i=W - 10, gun=silhouette_rects(1.0, 0.55, 0.55))


def main():
    import cairosvg

    os.makedirs(ART, exist_ok=True)
    items_dir = os.path.join(RP, "textures", "items")
    os.makedirs(items_dir, exist_ok=True)

    icon_svg = item_icon_svg()
    with open(os.path.join(ART, "icon_ak47.svg"), "w", encoding="utf-8") as f:
        f.write(icon_svg)
    cairosvg.svg2png(bytestring=icon_svg.encode(), write_to=os.path.join(items_dir, "ak47_icon.png"),
                     output_width=S, output_height=S)
    print("icon  ->", os.path.relpath(os.path.join(items_dir, "ak47_icon.png"), ROOT))

    pack_svg = pack_icon_svg()
    with open(os.path.join(ART, "pack_icon.svg"), "w", encoding="utf-8") as f:
        f.write(pack_svg)
    for sub in ("bp", "rp"):
        d = os.path.join(ROOT, "src", sub)
        os.makedirs(d, exist_ok=True)
        cairosvg.svg2png(bytestring=pack_svg.encode(), write_to=os.path.join(d, "pack_icon.png"),
                         output_width=128, output_height=128)
    print("pack  -> src/bp/pack_icon.png, src/rp/pack_icon.png")


if __name__ == "__main__":
    main()
