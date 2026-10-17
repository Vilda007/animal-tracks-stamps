#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_makerworld_scad.py - builds ONE universal parametric OpenSCAD generator
for MakerWorld: dropdown to pick any of the animals, L/R, scale, relief,
bevel, base, handle and text all customizable (Magic comment syntax).

Output: MakerWorld-Generatory/Animal_Tracks_Stamp_Generator.scad

The animal footprint polygons are baked in (already extracted, rotated,
scaled, simplified by the pipeline), user-facing params are OpenSCAD
Customizer variables compatible with MakerWorld (OpenSCAD 2021.01).
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Scripts-Skripty"))

import generate_stamp as gs  # noqa: E402

AZD = os.path.join(ROOT, "Animals-Zvirata")
ALL_DIRS = sorted(os.listdir(AZD))

# display order: the reference animals first
ORDER = ["Fox-Liska", "Wolf-Vlk", "Bear-Medved", "Boar-PraseDivoke",
         "Hare-Zajic", "Dog-Pes", "Cat-Kocka", "Badger-Jezevec",
         "Pig-Prase", "Sheep-Ovce", "Bull-Byk", "Cow-Krava", "Horse-Kun",
         "Squirrel-Veverka", "Hedgehog-Jezek", "Mole-Krtek", "Mouse-Mys",
         "Polecat-Tchor", "Frog-Zaba", "Grouse-Tetrev", "Chicken-Kure",
         "Pigeon-Holub", "Duck-Kachna", "Penguin-Tucnak", "Kangaroo-Klokan",
         "Opossum-Vacice", "Monkey-Opice", "Coati-Nosal", "Lion-Lev",
         "Antelope-Antilopa", "Llama-Lama", "Camel-Velbloud",
         "Rhino-Nosorozec", "Elephant-Slon", "Crocodile-Krokodyl",
         "Reindeer-Sob"]

entries = []
for d in ORDER:
    p = os.path.join(AZD, d, "params.json")
    if not os.path.exists(p):
        continue
    cfg = json.load(open(p, encoding="utf-8"))
    scad_cfg = dict(cfg["stamp"])
    polys, _ = gs.extract_paw_polys(scad_cfg)
    t = scad_cfg["track"]
    h = t["handle"]
    cz, en = cfg["animal"]["cz"], cfg["animal"]["en"]
    L = t["length_mm"]
    entries.append(dict(
        dir=d, cz=cz, en=en, latin=cfg["animal"]["latin"], L=L,
        relief=t["relief_depth_mm"], bevel=t.get("bevel_mm", 10.0),
        margin=t.get("base_margin_mm", 5.0),
        hw=h["width_mm"], hd=h["height_mm"], hh=h["thickness_mm"],
        hr=h["corner_r_mm"],
        base_h=t.get("base_thickness_mm", 4.0),
        polys=[[[round(float(x), 2), round(float(y), 2)] for x, y in S]
               for S, _, _ in polys],
    ))

data_js = json.dumps(
    [[e["cz"], e["en"], e["latin"], e["L"], e["relief"], e["bevel"],
      e["margin"], [e["hw"], e["hd"], e["hh"], e["hr"]], e["base_h"],
      e["polys"]] for e in entries],
    ensure_ascii=False, separators=(",", ":"))

dropdown = ", ".join("%d:%s (%s) %g mm" % (i, e["cz"], e["en"], e["L"])
                     for i, e in enumerate(entries))

scad = """// Animal Tracks Stamp Generator / Generátor razítek stop zvěře
// Pick an animal, left/right paw, tweak sizes - download, print, press into mud.
// Vyberte zvíře, levou/pravou tlapku, upravte rozměry - stáhněte, vytiskněte,
// zatlačte do bláta.
//
// Track outlines are real-size (verified against field guides) or scaled for
// tiny/huge animals (scale noted in each animal's label). Model made with the
// open-source pipeline at github.com/Vilda007/animal-tracks-stamps
// (OpenSCAD 2021.01 compatible).

/* [Zvíře / Animal] */
// Vyberte zvíře - stopa / Pick the animal's track
animal = 0; // [%s]
side = "L"; // [L:levá/left, R:pravá/right]
// Měřítko razítka (100 = reálná stopa) / stamp scale, %% of real size
scale_pct = 100; // [40:5:250]

/* [Reliéf (hloubka otisku) / Imprint] */
// výška reliéfu mm; 0 = doporučeno pro vybrané zvíře
relief_mm = 0; // [0:0.5:10]
// poloměr zaoblení hran polštářků; 0 = doporučeno
bevel_r = 0; // [0:0.5:16]
// počet kroků zaoblení (jemnost) / bevel steps
bevel_steps = 12; // [6:1:24]

/* [Základna / Base] */
// tloušťka základní desky mm; 0 = doporučeno
base_h = 0; // [0:0.5:10]
// okraj desky kolem stopy mm; 0 = doporučeno
base_margin_mm = 0; // [0:0.5:15]
// hladkost kulaté základny / base outline resolution
base_fn = 128; // [48:16:256]

/* [Madlo / Handle] */
// šířka madla mm; 0 = doporučeno (jinak škéluje se stopou)
handle_w = 0; // [0:1:80]
// výška madla mm
handle_h = 0; // [0:1:30]

/* [Text] */
// vlastní český název (prázdné = výchozí) / custom CZ name
name_cz = "";
// vlastní anglický název / custom EN name
name_en = "";
// písmo / font (MakerWorld nabízí Google Fonts)
text_font = "Open Sans"; // font
// výška reliéfu textu mm; 0 = auto
text_h = 0; // [0:0.2:4]

/* [Skryté / Hidden] */
DATA = %s;

// --------------------------------------------------------------- helpers ---
function ptp(v) = max(v) - min(v);
function island_md(P) = min(ptp([for (q = P) q[0]]), ptp([for (q = P) q[1]]));

I = DATA[animal];
L_mm = I[3] * scale_pct / 100;
relief = relief_mm > 0 ? relief_mm : I[4];
bevel = bevel_r > 0 ? bevel_r : I[5];
margin = base_margin_mm > 0 ? base_margin_mm : I[6];
hw0 = handle_w > 0 ? handle_w : I[7][0];
hd0 = I[7][1];
hh = handle_h > 0 ? handle_h : I[7][2];
hr = I[7][3];
plate_h = base_h > 0 ? base_h : I[8];
name_cz_e = name_cz == "" ? I[0] : name_cz;
name_en_e = name_en == "" ? I[1] : name_en;
scale_s = scale_pct / 100;
// madlo škluje se stopou (minimálně ale 16 mm)
hw = max(16, hw0 * scale_s);
hd = max(12, hd0 * scale_s);
plate_w = ptp([for (p = I[9]) for (q = p) q[0]]) * scale_s;

polys = [ for (P = I[9]) [ for (q = P) [q[0] * scale_s, q[1] * scale_s] ] ];

module footprint() { for (P = polys) polygon(P); }

module base_shape() {
    offset(r = margin) hull() footprint();
}

// jeden polstarek/ostrova s kruhovym bevlem ke spicce
module island(P) {
    D = relief;
    R = min(bevel, max(0.7, 0.45 * island_md(P)));
    NL = bevel_steps;
    hull() {
        translate([0, 0, -0.5]) linear_extrude(plate_h + 1.0) polygon(P);
        for (j = [1 : NL]) {
            z = -D * j / NL;
            arg = z + D - R;
            ins = R - sqrt(max(0, R * R - arg * arg));
            translate([0, 0, z])
                linear_extrude(0.12)
                    offset(r = (ins < 0.01 ? 0.01 : -ins)) polygon(P);
        }
    }
}

module relief() { for (P = polys) island(P); }

module stamp_body() {
    mirror(side == "R" ? [1, 0, 0] : [0, 0, 0]) {
        relief();
        linear_extrude(plate_h) base_shape();
    }
    translate([0, 0, plate_h - 1])
        linear_extrude(hh + 1)
            offset(r = hr) offset(delta = -hr) square([hw, hd], center = true);
}

module top_text() {
    th = text_h > 0 ? text_h : 1.4;
    size_cz = min(6.4, 0.88 * hw / (0.75 * len(name_cz_e)), 0.27 * hd);
    size_en = min(5.0, 0.88 * hw / (0.75 * len(name_en_e)), 0.22 * hd);
    size_side = min(6.4, 0.27 * hd);
    translate([0, 0, plate_h + hh - 0.5])
    linear_extrude(th + 0.5)
    union() {
        translate([0, 0.11 * hd, 0])
            text(name_cz_e, size = size_cz, halign = "center", font = text_font);
        translate([0, -0.13 * hd, 0])
            text(name_en_e, size = size_en, halign = "center", font = text_font);
        translate([0, -0.30 * hd, 0])
            text(side, size = size_side, halign = "center", font = text_font);
    }
}

union() {
    stamp_body();
    top_text();
}
""" % (dropdown, data_js)

OUTD = os.path.join(ROOT, "MakerWorld-Generatory")
os.makedirs(OUTD, exist_ok=True)
out = os.path.join(OUTD, "Animal_Tracks_Stamp_Generator.scad")
with open(out, "w", encoding="utf-8") as f:
    f.write(scad)
print("written:", out, os.path.getsize(out) // 1024, "KB,", len(entries), "animals")