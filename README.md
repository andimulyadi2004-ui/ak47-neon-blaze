# AK-47 Neon Blaze — Minecraft Bedrock Add-on

Add-on senjata **AK-47** dengan **model 3D penuh** (bukan sekadar ikon 2D) untuk
**Minecraft Bedrock / MCPE 1.26.40+**. Warna sengaja dibuat kontras tinggi:
baja gelap kebiruan, kayu oranye menyala, aksen emas, dan garis cyan neon.

![preview](preview/ak47_preview.png)

## Isi add-on

| Bagian | Detail |
|---|---|
| Item | `ak47:ak47` — "AK-47 Neon Blaze", rarity epic, durability 1561, damage 9 |
| Model 3D | 31 cube, 1 tekstur atlas 64×64, tampil saat dipegang (first & third person) |
| Ikon inventory | PNG 32×32 dengan alpha |
| Pack icon | PNG 128×128 (BP + RP) |
| Resep | Shaped 3×3 di crafting table |
| Amunisi | Panah (`minecraft:arrow`) via `minecraft:shooter` |

## Warna

| Elemen | Warna |
|---|---|
| Receiver, laras | `#23262E` / `#3A3F4B` baja gelap |
| Handguard, grip, stock | `#E8722A` / `#A8451A` kayu oranye |
| Muzzle brake, ring, bibir magasin | `#F2C14E` / `#B8862A` emas |
| Garis neon, front sight | `#35E0E8` cyan |
| Body, trigger guard | `#101216` hitam |

## Tekstur: SVG → PNG

Minecraft hanya menerima **PNG**, jadi semua tekstur digambar dulu sebagai SVG
pixel-art (`shape-rendering="crispEdges"`), lalu di-rasterise ke PNG. Sumber SVG
disimpan di `art/`, jadi bisa diedit ulang:

```
art/ak47_atlas.svg   -> src/rp/textures/items/ak47.png      (64x64 atlas model)
art/icon_ak47.svg    -> src/rp/textures/items/ak47_icon.png (32x32 ikon inventory)
art/pack_icon.svg    -> src/bp/pack_icon.png, src/rp/pack_icon.png (128x128)
```

## Struktur

```
src/
  bp/                          behavior pack
    manifest.json              format_version 2, min_engine_version [1,26,40]
    items/ak47.json            definisi item
    recipes/ak47.json          resep crafting
    texts/en_US.lang
    pack_icon.png
  rp/                          resource pack
    manifest.json              + dependencies ke UUID BP
    attachables/ak47.attachable.json
    models/entity/ak47.geo.json
    textures/item_texture.json
    textures/items/ak47.png        atlas model 64x64
    textures/items/ak47_icon.png   ikon 32x32
    texts/en_US.lang
    pack_icon.png
tools/
  palette.py       palet warna + posisi patch atlas
  gen_texture.py   SVG -> PNG atlas
  gen_model.py     generator geometri 3D
  gen_icon.py      SVG -> PNG ikon & pack icon
  render.py        renderer preview (bukan emulator Minecraft)
  validate.py      validator add-on
build.sh           build -> .mcaddon / .mcpack
```

## Build

```bash
pip install cairosvg pillow
./build.sh
```

Output di `dist/`:

- `AK47_NeonBlaze.mcaddon` — paket gabungan BP + RP (yang ini yang dipakai)
- `AK47_NeonBlaze_BP.mcpack`
- `AK47_NeonBlaze_RP.mcpack`

`build.sh` selalu menjalankan `validate.py` dan **berhenti kalau ada error**.

## Ambil add-on lewat Termux (`gh`)

```bash
pkg update && pkg install -y gh unzip
gh auth login

# folder Downloads Android
termux-setup-storage
mkdir -p ~/storage/downloads/AK47

# unduh paket siap pasang
gh release download v1.0.1 \
  -R andimulyadi2004-ui/ak47-neon-blaze \
  -p "AK47_NeonBlaze.mcaddon" \
  -D ~/storage/downloads/AK47 --clobber

ls -lh ~/storage/downloads/AK47
```

Ambil semua aset (BP, RP, dan paket gabungan) sekaligus:

```bash
gh release download v1.0.1 \
  -R andimulyadi2004-ui/ak47-neon-blaze \
  -D ~/storage/downloads/AK47 --clobber
```

Kalau ingin build sendiri dari source di Termux:

```bash
pkg install -y python git librsvg
pip install cairosvg pillow
gh repo clone andimulyadi2004-ui/ak47-neon-blaze
cd ak47-neon-blaze && ./build.sh
```

Lalu buka `AK47_NeonBlaze.mcaddon` dari aplikasi Files → **Open with Minecraft**.

## Pasang di Minecraft

1. Buka `AK47_NeonBlaze.mcaddon` → otomatis diimpor Minecraft.
2. Buat/edit world → **Behavior Packs** → aktifkan **AK-47 Neon Blaze BP**
   (RP ikut otomatis karena ada dependency).
3. Tidak perlu experimental toggle.
4. Craft dengan resep di bawah, atau langsung:

```
/give @s ak47:ak47
```

## Resep

```
Iron   Gold   Gold
Iron   Stick  Stick
Plank  Redstone Plank
```

(3×3 di crafting table; Iron = Iron Ingot, Gold = Gold Ingot, Plank = Oak Planks)

## Cara pakai

Tahan tombol use seperti memanah — item memakai `minecraft:shooter` +
`minecraft:projectile` sehingga menembak panah dari inventory. Siapkan
`minecraft:arrow` dulu.

## Verifikasi

`python3 tools/validate.py` — 43 pemeriksaan, semua PASS:

- manifest: `format_version` 2, `min_engine_version` `[1,26,40]`, 4 UUID unik,
  tipe modul `data` / `resources`, dependency RP→BP cocok
- identifier item == attachable == hasil resep
- `minecraft:icon` shortname ada di `item_texture.json` **dan** PNG-nya ada
  dengan alpha channel
- geometri: 31 cube, semua `size` > 0, semua UV di dalam atlas 64×64, bone
  `rightitem` punya binding item-slot
- bbox model: panjang 17.9, tinggi 8.5, lebar 1.9 unit
- resep: pattern 3×3 valid, semua simbol punya key, semua bahan ber-namespace
- `.lang` benar-benar `key=value` (bukan JSON)
- pack icon 128×128 di kedua pack

**Yang belum terverifikasi:** tampilan di dalam game. Tidak ada Minecraft di
lingkungan build, jadi posisi akhir model di tangan dan animasi memanah belum
dicek secara visual in-game.

## Catatan teknis

- Rotasi 90° dari pose desain ke pose "held" **di-bake ke angka geometri**,
  tidak memakai `rotation` di bone. Alasannya: rotasi bone bisa tertimpa oleh
  animasi model, sedangkan nilai geometri tidak.
- Model memakai konvensi yang sama dengan `trident.geo.json` vanilla: bone
  bernama `rightitem` dengan `binding: q.item_slot_to_bone_name(c.item_slot)`,
  panjang senjata di sumbu **+Y**.
- `minecraft:shooter` + `minecraft:projectile` dipakai karena paling stabil
  lintas versi; tidak butuh script API.

## Lisensi

MIT — lihat [LICENSE](LICENSE).
