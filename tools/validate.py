"""Validator add-on AK-47.

Memeriksa hal-hal yang benar-benar bisa membuat add-on gagal di Minecraft:
  - manifest: format_version, min_engine_version, uuid unik, tipe modul
  - dependency RP -> BP menunjuk UUID yang benar
  - identifier item di BP == attachable == recipe result
  - setiap tekstur yang dirujuk benar-benar ada sebagai PNG dan bisa dibuka
  - icon shortname ada di item_texture.json DAN file PNG-nya ada
  - geometri: cube tidak nol, UV patch ada di dalam atlas, bone punya binding
  - file .lang memakai format key=value (bukan JSON)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "src", "bp")
RP = os.path.join(ROOT, "src", "rp")

errors = []
warns = []
checks = 0


def ok(msg):
    global checks
    checks += 1
    print("  PASS  " + msg)


def err(msg):
    errors.append(msg)
    print("  FAIL  " + msg)


def warn(msg):
    warns.append(msg)
    print("  WARN  " + msg)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rel(p):
    return os.path.relpath(p, ROOT)


# ---------------------------------------------------------------- manifest
print("\n[1] Manifest")
bp_man = load(os.path.join(BP, "manifest.json"))
rp_man = load(os.path.join(RP, "manifest.json"))

for name, man in (("BP", bp_man), ("RP", rp_man)):
    if man.get("format_version") != 2:
        err("%s manifest format_version bukan 2" % name)
    else:
        ok("%s manifest format_version = 2" % name)
    hdr = man["header"]
    mv = hdr.get("min_engine_version")
    if mv == [1, 26, 40]:
        ok("%s min_engine_version = [1, 26, 40]" % name)
    else:
        err("%s min_engine_version salah: %s" % (name, mv))

uuids = [bp_man["header"]["uuid"], rp_man["header"]["uuid"]]
uuids += [m["uuid"] for m in bp_man["modules"]]
uuids += [m["uuid"] for m in rp_man["modules"]]
if len(set(uuids)) == len(uuids):
    ok("%d UUID unik (header + module)" % len(uuids))
else:
    err("ada UUID duplikat")

mod_types = {m["type"] for m in rp_man["modules"]}
if mod_types == {"resources"}:
    ok("RP punya modul resources")
else:
    err("RP module type salah: %s" % mod_types)
if {m["type"] for m in bp_man["modules"]} == {"data"}:
    ok("BP punya modul data")
else:
    err("BP module type salah")

deps = rp_man.get("dependencies", [])
dep_uuids = [d["uuid"] for d in deps]
if bp_man["header"]["uuid"] in dep_uuids:
    ok("RP depends on BP (UUID cocok)")
else:
    err("RP dependency tidak menunjuk UUID BP")

if bp_man.get("metadata", {}).get("product_type") == "addon" and \
   rp_man.get("metadata", {}).get("product_type") == "addon":
    ok("product_type = addon di kedua pack")
else:
    err("product_type bukan addon")

# ---------------------------------------------------------------- item
print("\n[2] Item definition")
item_path = os.path.join(BP, "items", "ak47.json")
item = load(item_path)
idesc = item["minecraft:item"]["description"]
ident = idesc["identifier"]
if re.match(r"^[a-z0-9_]+:[a-z0-9_]+$", ident):
    ok("identifier valid: %s" % ident)
else:
    err("identifier tidak valid: %s" % ident)
if idesc.get("menu_category", {}).get("category"):
    ok("menu_category = %s" % idesc["menu_category"]["category"])
else:
    err("menu_category tidak ada (item tidak muncul di creative)")

comp = item["minecraft:item"]["components"]
if comp.get("minecraft:hand_equipped") is True:
    ok("hand_equipped = true (bisa dipegang 3D)")
else:
    err("hand_equipped harus true supaya model 3D dipakai")
if comp.get("minecraft:max_stack_size") == 1:
    ok("max_stack_size = 1")
else:
    err("max_stack_size harus 1 untuk senjata")
dmg = comp.get("minecraft:damage")
if isinstance(dmg, int) and dmg >= 1:
    ok("damage = %s" % dmg)
else:
    err("damage tidak valid: %s" % dmg)
if comp.get("minecraft:icon") == "ak47_icon":
    ok("minecraft:icon = ak47_icon")
else:
    err("minecraft:icon salah: %s" % comp.get("minecraft:icon"))

# ---------------------------------------------------------------- icon + texture
print("\n[3] Ikon & tekstur")
it = load(os.path.join(RP, "textures", "item_texture.json"))
td = it.get("texture_data", {})
short = comp.get("minecraft:icon")
if short in td:
    ok("shortname '%s' ada di item_texture.json" % short)
else:
    err("shortname '%s' TIDAK ada di item_texture.json" % short)
if it.get("texture_name") == "atlas.items":
    ok("texture_name = atlas.items")
else:
    err("texture_name harus atlas.items")

from PIL import Image

icon_rel = td[short]["textures"]
icon_png = os.path.join(RP, icon_rel + ".png")
if os.path.isfile(icon_png):
    im = Image.open(icon_png)
    if im.size == (32, 32):
        ok("icon PNG ada & 32x32 (%s)" % im.mode)
    else:
        warn("icon PNG ukuran %s (disarankan 32x32)" % (im.size,))
    if im.mode in ("RGBA", "LA", "P"):
        ok("icon punya alpha channel")
    else:
        warn("icon tanpa alpha (mode %s)" % im.mode)
else:
    err("icon PNG tidak ditemukan: %s" % icon_rel)

# ---------------------------------------------------------------- attachable
print("\n[4] Attachable")
att = load(os.path.join(RP, "attachables", "ak47.attachable.json"))
ad = att["minecraft:attachable"]["description"]
if ad["identifier"] == ident:
    ok("attachable identifier cocok dengan item: %s" % ad["identifier"])
else:
    err("attachable identifier beda: %s vs %s" % (ad["identifier"], ident))
if "geometry" in ad and ad["geometry"].get("default"):
    ok("attachable punya geometry: %s" % ad["geometry"]["default"])
else:
    err("attachable tanpa geometry (model 3D tidak akan tampil)")
tex = ad["textures"]["default"]
tex_png = os.path.join(RP, tex + ".png")
if os.path.isfile(tex_png):
    t = Image.open(tex_png)
    ok("tekstur model ada: %s %s" % (tex, t.size))
else:
    err("tekstur model hilang: %s" % tex)
if ad.get("materials", {}).get("default") == "entity_alphatest":
    ok("material default = entity_alphatest")
else:
    warn("material default = %s" % ad.get("materials", {}).get("default"))
if ad.get("render_controllers"):
    ok("render_controllers: %s" % ad["render_controllers"])
else:
    err("attachable tanpa render_controllers")

# ---------------------------------------------------------------- geometry
print("\n[5] Geometri")
geo = load(os.path.join(RP, "models", "entity", "ak47.geo.json"))
g = geo["minecraft:geometry"][0]
tw = g["description"]["texture_width"]
th = g["description"]["texture_height"]
if g["description"]["identifier"] == ad["geometry"]["default"]:
    ok("geometry identifier cocok dengan attachable")
else:
    err("geometry identifier beda: %s vs %s" % (g["description"]["identifier"],
                                                ad["geometry"]["default"]))
bone = g["bones"][0]
if bone.get("binding") == "q.item_slot_to_bone_name(c.item_slot)":
    ok("bone binding item-slot benar")
else:
    err("bone binding tidak benar: %s" % bone.get("binding"))
if bone.get("parent") is None and bone["name"].lower() in ("rightitem", "leftitem"):
    ok("bone root = %s (menempel ke tangan)" % bone["name"])

cubes = bone["cubes"]
ok("%d cube" % len(cubes))
bad = 0
for i, c in enumerate(cubes):
    if min(c["size"]) <= 0:
        err("cube #%d punya size 0" % i)
        bad += 1
    for face, f in c["uv"].items():
        u0, v0 = f["uv"]
        uw, vh = f["uv_size"]
        for uu in (u0, u0 + uw):
            for vv in (v0, v0 + vh):
                if not (0 <= uu <= tw and 0 <= vv <= th):
                    err("cube #%d face %s UV keluar atlas: %s" % (i, face, f))
                    bad += 1
if bad == 0:
    ok("semua cube punya size > 0 dan UV di dalam %dx%d atlas" % (tw, th))

xs = [c["origin"][0] for c in cubes] + [c["origin"][0] + c["size"][0] for c in cubes]
ys = [c["origin"][1] for c in cubes] + [c["origin"][1] + c["size"][1] for c in cubes]
zs = [c["origin"][2] for c in cubes] + [c["origin"][2] + c["size"][2] for c in cubes]
L = max(zs) - min(zs)
H = max(ys) - min(ys)
W = max(xs) - min(xs)
print("        bbox: panjang %.1f, tinggi %.1f, lebar %.1f" % (L, H, W))
if 8 <= L <= 24:
    ok("panjang model %.1f unit (masuk akal untuk senjata dipegang)" % L)
else:
    err("panjang model %.1f di luar rentang wajar 8..24" % L)
if W <= 4:
    ok("lebar model %.1f (tipis, tidak memotong badan pemain)" % W)
else:
    err("lebar model %.1f terlalu tebal" % W)

# ---------------------------------------------------------------- recipe
print("\n[6] Resep")
rc = load(os.path.join(BP, "recipes", "ak47.json"))
r = rc["minecraft:recipe_shaped"]
if r["result"]["item"] == ident:
    ok("hasil resep = %s" % ident)
else:
    err("hasil resep bukan item kita: %s" % r["result"]["item"])
if r["description"]["identifier"] == ident:
    ok("resep identifier = %s" % ident)
else:
    err("resep identifier beda: %s" % r["description"]["identifier"])
if "crafting_table" in r["tags"]:
    ok("tags = crafting_table")
else:
    err("tags resep salah: %s" % r["tags"])
rows = r["pattern"]
widths = {len(row) for row in rows}
if len(widths) == 1 and 1 <= len(rows) <= 3 and widths.pop() <= 3:
    ok("pattern %dx%d valid" % (len(rows[0]), len(rows)))
else:
    err("pattern resep tidak 2D valid: %s" % rows)
missing = [ch for row in rows for ch in row if ch != " " and ch not in r["key"]]
if not missing:
    ok("semua simbol pattern ada di key")
else:
    err("simbol tanpa key: %s" % missing)
bad_items = [k["item"] for k in r["key"].values()
             if not k["item"].startswith(("minecraft:", "ak47:"))]
if not bad_items:
    ok("semua bahan memakai identifier valid")
else:
    err("bahan tanpa namespace: %s" % bad_items)

# ---------------------------------------------------------------- lang
print("\n[7] Bahasa")
for pack, d in (("BP", BP), ("RP", RP)):
    p = os.path.join(d, "texts", "en_US.lang")
    if not os.path.isfile(p):
        err("%s tidak punya texts/en_US.lang" % pack)
        continue
    raw = open(p, encoding="utf-8").read()
    if raw.lstrip().startswith("{"):
        err("%s en_US.lang masih JSON, harus key=value" % pack)
        continue
    kv = [ln for ln in raw.splitlines() if "=" in ln]
    if kv:
        ok("%s en_US.lang format key=value (%d entri)" % (pack, len(kv)))
    else:
        err("%s en_US.lang tanpa key=value" % pack)
    if "item.ak47.ak47.name" in raw:
        ok("%s punya nama item" % pack)
    else:
        warn("%s tidak punya item.ak47.ak47.name" % pack)

# ---------------------------------------------------------------- pack icon
print("\n[8] Pack icon")
for pack, d in (("BP", BP), ("RP", RP)):
    p = os.path.join(d, "pack_icon.png")
    if os.path.isfile(p):
        im = Image.open(p)
        if im.size == (128, 128):
            ok("%s pack_icon.png 128x128" % pack)
        else:
            warn("%s pack_icon.png ukuran %s" % (pack, im.size))
    else:
        err("%s tanpa pack_icon.png" % pack)

# ---------------------------------------------------------------- summary
print("\n" + "=" * 58)
print("checks: %d   error: %d   warning: %d" % (checks, len(errors), len(warns)))
if errors:
    print("\nERROR:")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print("VALIDATION PASSED")
