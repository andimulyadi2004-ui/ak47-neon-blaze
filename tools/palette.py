"""Palet warna kontras untuk AK-47 "Neon Blaze".

Semua patch diletakkan di atlas 64x64. Setiap patch 16x16 piksel.
Warna sengaja dibuat kontras tinggi: baja gelap kebiruan vs kayu oranye
menyala vs aksen cyan menyala vs emas.
"""

ATLAS = 64

# nama patch -> (x, y, w, h)
PATCHES = {
    "steel_dark":  (0, 0, 16, 16),
    "steel_mid":   (16, 0, 16, 16),
    "wood":        (32, 0, 16, 16),
    "gold":        (48, 0, 16, 16),
    "cyan":        (0, 16, 16, 16),
    "black":       (16, 16, 16, 16),
    "red":         (32, 16, 16, 16),
    "steel_light": (48, 16, 16, 16),
    "wood_dark":   (0, 32, 16, 16),
    "gold_dark":   (16, 32, 16, 16),
    "cyan_dark":   (32, 32, 16, 16),
    "white":       (48, 32, 16, 16),
}

# patch -> (warna dasar, warna terang, warna gelap)
COLORS = {
    "steel_dark":  ("#23262E", "#33384A", "#14161C"),
    "steel_mid":   ("#3A3F4B", "#4E5566", "#252932"),
    "steel_light": ("#6B7385", "#8A93A8", "#4A5160"),
    "wood":        ("#E8722A", "#FF9A4D", "#B8501A"),
    "wood_dark":   ("#A8451A", "#C4551A", "#7A2E10"),
    "gold":        ("#F2C14E", "#FFE08A", "#C99A2E"),
    "gold_dark":   ("#B8862A", "#D9A63C", "#8A6118"),
    "cyan":        ("#35E0E8", "#8CF6FA", "#1FA8B8"),
    "cyan_dark":   ("#1B7F8C", "#2AA3B0", "#125A64"),
    "black":       ("#101216", "#1C1F26", "#08090B"),
    "red":         ("#E23B3B", "#FF6B6B", "#A81F1F"),
    "white":       ("#F2F4F8", "#FFFFFF", "#C8CDD8"),
}
