# Wolf – Vlk

## English

**Gray wolf (*Canis lupus*) — front paw stamp.**

- Track outline extracted from `Tracks-Stopy/STOPY-1.png` (bottom row, "VLK"),
  scaled to real size: **110 × 85 mm** (L × W) — front paw
  ([KORA](https://www.kora.ch/en/species/wolf/signs-in-the-field);
  [NPS carnivore tracking guide](https://www.nps.gov/mora/planyourvisit/upload/Carnivore-Tracks-12-20-21_508.pdf)
  gives 89–125 × 75–124 mm; front larger than hind).
- The track consists of 9 parts: palm pad, 4 toe pads, 4 claw marks.
- Domed relief (no sharp edges), paw rotated so the pad→toes axis is vertical.
- Files:
  - `params.json` — stamp configuration
  - `wolf_stamp.scad` — parametric model (`side = "L"` / `"R"`)
  - `wolf_stamp_L.stl`, `wolf_stamp_R.stl` — ready to slice (96 × 122 × 29 mm, watertight)
  - `wolf_mask.png`, `previews/`
- Regenerate: `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Wolf-Vlk --stl`

## Česky

**Vlk obecný (*Canis lupus*) — razítko přední tlapky.**

- Obrys extrahován z `Tracks-Stopy/STOPY-1.png` (dolní řada, "VLK"),
  přepočten na reálnou velikost: **110 × 85 mm** (D × Š) — přední tlapa
  ([KORA](https://www.kora.ch/en/species/wolf/signs-in-the-field);
  [NPS carnivore tracking guide](https://www.nps.gov/mora/planyourvisit/upload/Carnivore-Tracks-12-20-21_508.pdf)
  uvádí 89–125 × 75–124 mm; přední větší než zadní).
- Stopa se skládá z 9 částí: polštář chodidla, 4 polštářky prstů, 4 drápky.
- Klenutý reliéf (bez ostrých hran), stopa narotovaná osou nahoru.
- Soubory: `params.json`, `wolf_stamp.scad`,
  `wolf_stamp_L.stl` / `wolf_stamp_R.stl` (96 × 122 × 29 mm), `wolf_mask.png`, `previews/`
- Regenerace: `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Wolf-Vlk --stl`
