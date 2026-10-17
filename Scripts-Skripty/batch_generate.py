#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
batch_generate.py - seed params.json for every animal in the reference sheets
and optionally run generate_stamp.py for each.

Usage:
    python Scripts-Skripty/batch_generate.py [--generate]

Track sizes verified via web field guides (see per-animal "sources").
Tracks too small/large for a practical stamp are scaled (scale_note).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# sheet geometry: (file, row_height)
S1 = ("Tracks-Stopy/STOPY-1.png", 758)   # OPICE sheet
S2 = ("Tracks-Stopy/STOPY-2.png", 700)   # TETŘEV sheet
S3 = ("Tracks-Stopy/STOPY-3.png", 698)   # MEDVĚD sheet

# text cutoffs per sheet/row (label sits at the bottom of a cell; the bottom
# row also catches the label of the row above at its top)
CUT = {
    ("S1", 0): (0, 620), ("S1", 1): (60, 500),
    ("S2", 0): (0, 574), ("S2", 1): (20, 470),
    ("S3", 0): (0, 560), ("S3", 1): (20, 470),
}

# sizing tiers by target stamp length [mm]
def tier(length):
    if length < 50:
        return dict(relief=4.0, margin=4, handle=(30, 20, 12, 3))
    if length < 90:
        return dict(relief=5.0, margin=5, handle=(36, 22, 14, 3))
    if length < 120:
        return dict(relief=6.0, margin=6, handle=(44, 26, 16, 4))
    return dict(relief=6.5, margin=7, handle=(50, 30, 18, 5))

# (dir, slug, cz_full, en_full, latin, label_cz, label_en, sheet, row, col,
#  target_length_mm, true_width_mm_or_None, scale_note_or_None, paw_pick, sources)
ANIMALS = [
    # ----- STOPY-1 (OPICE sheet) -----
    ("Monkey-Opice", "monkey", "Opice", "Monkey", "Primates",
     "OPICE", "MONKEY", "S1", 0, 0, 90, 70,
     "modelled on baboon hand (~90-120 mm)", "larger",
     ["https://books.brightlearn.ai/Africas-Wild-Clues-The-Ultimate-African-Wildlife-Track-eea071131-en/page26.html"]),
    ("Boar-PraseDivoke", "boar", "Prase divoké", "Wild boar", "Sus scrofa",
     "PRASE DIV.", "BOAR", "S1", 0, 1, 75, 70, None, "larger",
     ["https://iboar.com/wild-boar-tracks-and-scat-identification/",
      "https://www.discoverwildlife.com/animal-facts/mammals/wild-boar-facts"]),
    ("Rhino-Nosorozec", "rhino", "Nosorožec", "White rhino", "Ceratotherium simum",
     "NOSOROŽEC", "RHINO", "S1", 0, 2, 110, 90,
     "scale ~1:2.2 (real front track ~220-300 mm wide)", "larger",
     ["https://krugerhelp.co.za/tracks"]),
    ("Mouse-Mys", "mouse", "Myš", "Wood mouse", "Apodemus sylvaticus",
     "MYŠ", "MOUSE", "S1", 0, 4, 35, 28,
     "scale ~3.5x up (real print ~10 mm)", "larger",
     ["https://www.naturevolunteers.uk/wp-content/uploads/2019/06/Naturehood-Spotters-guide-Hedgehog.pdf"]),
    ("Bull-Byk", "bull", "Býk", "Bull / cattle", "Bos taurus",
     "BÝK", "BULL", "S1", 0, 5, 120, 105, None, "larger",
     ["https://peecnature.org/learn/nature-guides/track-guide/"]),
    ("Horse-Kun", "horse", "Kůň", "Horse", "Equus caballus",
     "KŮŇ", "HORSE", "S1", 1, 0, 130, 120, None, "larger",
     ["https://peecnature.org/learn/nature-guides/track-guide/"]),
    ("Badger-Jezevec", "badger", "Jezevec", "European badger", "Meles meles",
     "JEZEVEC", "BADGER", "S1", 1, 2, 65, 50, None, "larger",
     ["https://www.naturevolunteers.uk/wp-content/uploads/2019/06/Naturehood-Spotters-guide-Hedgehog.pdf"]),
    ("Polecat-Tchor", "polecat", "Tchoř", "European polecat", "Mustela putorius",
     "TCHOŘ", "POLECAT", "S1", 1, 3, 40, 32, None, "larger",
     ["https://doi.org/10.21005/aapz2024.69.1.8"]),
    ("Frog-Zaba", "frog", "Žába", "Frog", "Anura",
     "ŽÁBA", "FROG", "S1", 1, 4, 45, 40,
     "scale ~2x up; real frog prints vary a lot by species", "larger",
     ["https://www.wildlifetrusts.org/how-identify/identify-tracks"]),
    ("Hare-Zajic", "hare", "Zajíc", "Brown hare", "Lepus europaeus",
     "ZAJÍC", "HARE", "S1", 1, 5, 150, 60,
     "hind foot (up to 150 mm per Cornwall Mammal Group)", "larger",
     ["https://www.cornwallmammalgroup.org/brown-hare"]),
    # ----- STOPY-2 (TETŘEV sheet) -----
    ("Grouse-Tetrev", "grouse", "Tetřev", "Capercaillie", "Tetrao urogallus",
     "TETŘEV", "CAPERCAILLIE", "S2", 0, 0, 90, 80,
     "turkey-sized grouse; ~90-120 mm estimated", "larger",
     ["https://avianenthusiast.com/bird-footprint/"]),
    ("Chicken-Kure", "chicken", "Kuře", "Chicken", "Gallus gallus domesticus",
     "KUŘE", "CHICKEN", "S2", 0, 1, 65, 55, None, "larger",
     ["https://avianenthusiast.com/bird-footprint/"]),
    ("Pigeon-Holub", "pigeon", "Holub", "Pigeon", "Columba livia",
     "HOLUB", "PIGEON", "S2", 0, 2, 45, 35, None, "larger",
     ["https://avianenthusiast.com/bird-footprint/",
      "https://betterplaneteducation.org.uk/factsheets/wildlife-id-footprints-birds"]),
    ("Duck-Kachna", "duck", "Kachna", "Mallard duck", "Anas platyrhynchos",
     "KACHNA", "DUCK", "S2", 0, 3, 70, 65, None, "larger",
     ["https://avianenthusiast.com/bird-footprint/"]),
    ("Dog-Pes", "dog", "Pes", "Dog (large)", "Canis lupus familiaris",
     "PES", "DOG", "S2", 0, 4, 90, 70, None, "larger",
     ["https://www.wildlifetrusts.org/how-identify/identify-tracks"]),
    ("Cat-Kocka", "cat", "Kočka", "Domestic cat", "Felis catus",
     "KOČKA", "CAT", "S2", 0, 5, 35, 32, None, "larger",
     ["https://peecnature.org/learn/nature-guides/track-guide/"]),
    ("Penguin-Tucnak", "penguin", "Tučňák", "Penguin (Gentoo)", "Pygoscelis papua",
     "TUČŇÁK", "PENGUIN", "S2", 1, 0, 120, 60,
     "gentoo-sized print 110-140 mm", "larger",
     ["https://www.apscience.blog/decode-penguin-footprints-secrets"]),
    ("Kangaroo-Klokan", "kangaroo", "Klokan", "Red kangaroo", "Osphranter rufus",
     "KLOKAN", "KANGAROO", "S2", 1, 1, 100, 40,
     "hind foot, scale ~1:3 (real macropod hind >250 mm)", "larger",
     ["https://www.sfzoodocents.org/notebook/Biofacts/AustralianWalkaboutTalkingPoints.pdf"]),
    ("Camel-Velbloud", "camel", "Velbloud", "Camel", "Camelus bactrianus",
     "VELBLOUD", "CAMEL", "S2", 1, 2, 120, 100,
     "slightly scaled (real ~150-200 mm)", "larger",
     ["https://studyx.ai/homework/112139089-footprint-animal-actual-length-of-the-footprint-in-centimetres-cm-cat-rabbit-cm-lion-rat"]),
    ("Mole-Krtek", "mole", "Krtek", "European mole", "Talpa europaea",
     "KRTEK", "MOLE", "S2", 1, 3, 50, 40,
     "scale ~2x up (front paw ~25 mm wide)", "larger",
     ["https://www.wildlifetrusts.org/how-identify/identify-tracks"]),
    ("Cow-Krava", "cow", "Kráva", "Domestic cattle", "Bos taurus",
     "KRÁVA", "COW", "S2", 1, 4, 110, 95, None, "larger",
     ["https://peecnature.org/learn/nature-guides/track-guide/"]),
    ("Squirrel-Veverka", "squirrel", "Veverka", "Red squirrel", "Sciurus vulgaris",
     "VEVERKA", "SQUIRREL", "S2", 1, 5, 70, 30,
     "hind foot scaled ~1.6x up (real 35-45 mm)", "larger",
     ["https://www.naturevolunteers.uk/wp-content/uploads/2019/06/Naturehood-Spotters-guide-Hedgehog.pdf"]),
    # ----- STOPY-3 (MEDVĚD sheet) -----
    ("Crocodile-Krokodyl", "crocodile", "Krokodýl", "Nile crocodile", "Crocodylus niloticus",
     "KROKODÝL", "CROCODILE", "S3", 0, 1, 120, 90,
     "front foot, slightly scaled; 5 splayed toes", "larger",
     ["https://krugerhelp.co.za/tracks"]),
    ("Coati-Nosal", "coati", "Nosál", "Ring-tailed coati", "Nasua nasua",
     "NOSÁL", "COATI", "S3", 0, 2, 80, 45, None, "larger",
     ["https://ipam.org.br/cartilhas-ipam/footprints-identifying-mammals/"]),
    ("Antelope-Antilopa", "antelope", "Antilopa", "Antelope (gazelle)", "Antilopinae",
     "ANTILOPA", "ANTELOPE", "S3", 0, 3, 60, 50, None, "larger",
     ["https://krugerhelp.co.za/tracks"]),
    ("Llama-Lama", "llama", "Lama", "Llama", "Lama glama",
     "LAMA", "LLAMA", "S3", 0, 4, 110, 85, None, "larger",
     ["https://petshun.com/article/what-do-llama-tracks-look-like"]),
    ("Lion-Lev", "lion", "Lev", "Lion", "Panthera leo",
     "LEV", "LION", "S3", 0, 5, 135, 120,
     "front paw 130-145 x 110-130 mm", "larger",
     ["https://www.lionlandscapes.org/paws-claws",
      "https://blog.londolozi.com/2012/05/09/how-to-track-a-lion/"]),
    ("Elephant-Slon", "elephant", "Slon", "African elephant", "Loxodonta africana",
     "SLON", "ELEPHANT", "S3", 1, 0, 110, 110,
     "scale ~1:3.5 (real print 390-470 mm)", "larger",
     ["https://en.upali.ch/foot-and-foot-care/"]),
    ("Hedgehog-Jezek", "hedgehog", "Ježek", "European hedgehog", "Erinaceus europaeus",
     "JEŽEK", "HEDGEHOG", "S3", 1, 1, 65, 60,
     "scale ~2.5x up (real print ~25 x 28 mm)", "larger",
     ["https://www.naturevolunteers.uk/wp-content/uploads/2019/06/Naturehood-Spotters-guide-Hedgehog.pdf"]),
    ("Pig-Prase", "pig", "Prase domácí", "Domestic pig", "Sus domesticus",
     "PRASE", "PIG", "S3", 1, 2, 80, 70, None, "larger",
     ["https://www.pubs.ext.vt.edu/content/dam/pubs_ext_vt_edu/CNRE/cnre-146/cnre-146.pdf"]),
    ("Sheep-Ovce", "sheep", "Ovce", "Sheep", "Ovis aries",
     "OVCE", "SHEEP", "S3", 1, 3, 65, 55, None, "larger",
     ["https://www.wildlifetrusts.org/how-identify/identify-tracks"]),
    ("Opossum-Vacice", "opossum", "Vačice", "Virginia opossum", "Didelphis virginiana",
     "VAČICE", "OPOSSUM", "S3", 1, 4, 55, 45, None, "larger",
     ["https://mdc.mo.gov/wildlife/wildlife-facts/mammal-facts/mammal-tracks"]),
    ("Reindeer-Sob", "reindeer", "Sob", "Reindeer / caribou", "Rangifer tarandus",
     "SOB", "REINDEER", "S3", 1, 5, 95, 90, None, "larger",
     ["https://worlddeer.org/deer-tracks/"]),
]

SHEETS = {"S1": S1, "S2": S2, "S3": S3}


def seed(a):
    (d, slug, cz, en, latin, lcz, len_en, sh, row, col, L, Wmm, note, pick,
     sources) = a
    sheet_file, _ = SHEETS[sh]
    top, bottom = CUT[(sh, row)]
    tr = tier(L)
    hw, hd, hh, hr = tr["handle"]
    cfg = {
        "animal": {"cz": cz, "en": en, "latin": latin, "slug": slug},
        "stamp": {
            "name_cz": lcz, "name_en": len_en, "paw": "front/hind (larger print in sheet)",
            "source": {
                "sheet": sheet_file, "row": row, "col": col,
                "n_rows": 2, "n_cols": 6,
                "text_cutoff_px": bottom, "text_top_cutoff_px": top,
                "paw_pick": pick,
            },
            "track": {
                "length_mm": float(L),
                "relief_depth_mm": tr["relief"],
                "claws": True,
                "bevel_mm": 10.0, "bevel_steps": 12,
                "base_shape": "hull",
                "base_margin_mm": float(tr["margin"]),
                "base_thickness_mm": 4.0,
                "handle": {"width_mm": float(hw), "height_mm": float(hd),
                           "thickness_mm": float(hh), "corner_r_mm": float(hr)},
                "text_height_mm": 1.4,
            },
        },
        "sources": sources,
        "notes": note or "",
    }
    if Wmm:
        cfg["stamp"]["track"]["width_mm"] = float(Wmm)
    od = os.path.join(ROOT, "Animals-Zvirata", d)
    os.makedirs(od, exist_ok=True)
    p = os.path.join(od, "params.json")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    return d


README_TMPL = """# {en} – {cz}

**{en} (*{latin}*) — {label_en} stamp. / Razítko: {label_cz}.**

- Track length on the stamp: **{L} mm**. {note}
- Sources: {srcs}
- Regenerate: `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/{d} --stl`

Soubory / files: `params.json`, `{slug}_stamp.scad`, `{slug}_stamp_L.stl`,
`{slug}_stamp_R.stl`, `{slug}_mask.png`, `previews/`.
"""


def write_readme(a, cfg):
    (d, slug, cz, en, latin, lcz, len_en, sh, row, col, L, Wmm, note, pick,
     sources) = a
    p = os.path.join(ROOT, "Animals-Zvirata", d, "README.md")
    if os.path.exists(p):
        return
    with open(p, "w", encoding="utf-8") as f:
        f.write(README_TMPL.format(
            d=d, slug=slug, cz=cz, en=en, latin=latin,
            label_cz=lcz, label_en=len_en, L=L,
            note=(note + ".") if note else "Real size.",
            srcs=", ".join(sources)))


def main():
    do_gen = "--generate" in sys.argv
    gen = os.path.join(ROOT, "Scripts-Skripty", "generate_stamp.py")
    for a in ANIMALS:
        d = seed(a)
        print(d)
    if do_gen:
        for a in ANIMALS:
            d = a[0]
            cfg = json.load(open(os.path.join(ROOT, "Animals-Zvirata", d,
                                              "params.json"), encoding="utf-8"))
            write_readme(a, cfg)
            r = subprocess.run(
                [sys.executable, "-I", gen,
                 os.path.join(ROOT, "Animals-Zvirata", d)],
                capture_output=True, text=True)
            out = (r.stdout or "") + (r.stderr or "")
            print("== %s: %s" % (d, " | ".join(out.strip().splitlines()[:2])))


if __name__ == "__main__":
    main()
