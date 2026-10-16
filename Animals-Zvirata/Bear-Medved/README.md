# Bear – Medvěd

## English

**Brown bear (*Ursus arctos*) — front paw stamp.**

- Track outline extracted from `Tracks-Stopy/STOPY-3.png` (top row, "MEDVĚD"),
  scaled to length **140 mm** — front print is 120–150 mm long, width over
  130 mm indicates an adult male
  ([Suurpedot.fi](https://www.largecarnivores.fi/species/brown-bear/signs-of-a-bear.html);
  [KORA](https://www.kora.ch/en/species/bear/signs-in-the-field);
  [ADFG track card](https://www.adfg.alaska.gov/static/education/educators/pdfs/track_pocket_card.pdf)).
- The track consists of 11 parts: sole pad, 5 toe pads, 5 claw marks.
- Note: the reference sheet artwork is proportionally narrower
  (140 × 110 mm after scaling) than typical field prints.
- Domed relief, paw rotated so the pad→toes axis is vertical.
- Files:
  - `params.json` — stamp configuration
  - `bear_stamp.scad` — parametric model (`side = "L"` / `"R"`)
  - `bear_stamp_L.stl`, `bear_stamp_R.stl` — ready to slice (124 × 147 × 33 mm, watertight)
  - `bear_mask.png`, `previews/`
- Regenerate: `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Bear-Medved --stl`
- The hind paw stamp (180–250 mm, human-foot-like) can be generated from the
  second outline with `paw_pick: "smaller"`.

## Česky

**Medvěd hnědý (*Ursus arctos*) — razítko přední tlapky.**

- Obrys extrahován z `Tracks-Stopy/STOPY-3.png` (horní řada, "MEDVĚD"),
  přepočten na délku **140 mm** — přední stopa je dlouhá 120–150 mm, šířka
  přes 130 mm znamená dospělého samce
  ([Suurpedot.fi](https://www.largecarnivores.fi/species/brown-bear/signs-of-a-bear.html);
  [KORA](https://www.kora.ch/en/species/bear/signs-in-the-field)).
- Stopa se skládá z 11 částí: spodek tlapy, 5 polštářků prstů, 5 drápků.
- Pozn.: kresba ve vzorníku je proporcionálně užší (140 × 110 mm po přepočtu)
  než typické stopy v terénu.
- Klenutý reliéf, stopa narotovaná osou nahoru.
- Soubory: `params.json`, `bear_stamp.scad`,
  `bear_stamp_L.stl` / `bear_stamp_R.stl` (124 × 147 × 33 mm), `bear_mask.png`, `previews/`
- Regenerace: `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Bear-Medved --stl`
- Razítko zadní tlapky (180–250 mm, podobné lidské noze) lze vyrobit z druhého
  obrysu pomocí `paw_pick: "smaller"`.
