# Fox – Liška

## English

**Red fox (*Vulpes vulpes*) — front paw stamp.**

- Track outline extracted from `Tracks-Stopy/STOPY-1.png` (top row, "LIŠKA"),
  scaled to real size: **51–57 × 44 mm** (L × W) — front track
  ([ND Game & Fish](https://gf.nd.gov/wildlife/id/carnivores/red-fox);
  [Maryland DNR track key](https://dnr.maryland.gov/wildlife/Documents/Key-Common-Mammal-Tracks.pdf)
  gives 44–64 × 38–51 mm).
- The track consists of 9 parts: palm pad, 4 toe pads, 4 claw marks.
- Relief is **domed** (no sharp edges) — pads in the wild leave soft,
  rounded imprints.
- **All parameters are configurable in `params.json`** (size, relief depth,
  rounding, handle…) — regenerate with
  `python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Fox-Liska --stl`.
- The track consists of 9 parts: palm pad, 4 toe pads, 4 claw marks.
- Relief is **domed** (no sharp edges) — pads in the wild leave soft,
  rounded imprints.
- Files:
  - `params.json` — stamp configuration (track size, relief depth, rounding,
    handle, position in the reference sheet)
  - `fox_stamp.scad` — parametric model (`side = "L"` / `"R"`, sizes in mm at the top)
  - `fox_stamp_L.stl`, `fox_stamp_R.stl` — ready to slice (54.6 × 67.0 × 26.3 mm, watertight)
  - `fox_mask.png` — the source mask crop
  - `previews/` — outline check + rendered previews
- Front/hind note: this model traces the **front** (larger) paw from the sheet.
  A hind-paw stamp can be generated from the second, smaller outline.

## Česky

**Liška obecná (*Vulpes vulpes*) — razítko přední tlapky.**

- Obrys stopy extrahován z `Tracks-Stopy/STOPY-1.png` (horní řada, "LIŠKA"),
  přepočten na reálnou velikost: **51–57 × 44 mm** (D × Š) — přední stopa
  ([ND Game & Fish](https://gf.nd.gov/wildlife/id/carnivores/red-fox);
  [Maryland DNR atlas stop](https://dnr.maryland.gov/wildlife/Documents/Key-Common-Mammal-Tracks.pdf)
  uvádí 44–64 × 38–51 mm).
- Stopa se skládá z 9 částí: polštář chodidla, 4 polštářky prstů, 4 drápky.
- Reliéf je **klenutý** (bez ostrých hran) — polštářky zanechávají v přírodě
  měkké, zaoblené otisky.
- Soubory:
  - `params.json` — konfigurace razítka (velikost stopy, hloubka reliéfu,
    zaoblení, madlo, pozice ve vzoru)
  - `fox_stamp.scad` — parametrický model (`side = "L"` / `"R"`)
  - `fox_stamp_L.stl`, `fox_stamp_R.stl` — připraveno ke slicování (54,6 × 67,0 × 26,3 mm)
  - `fox_mask.png` — ořez původní masky
  - `previews/` — kontrolní obrázek obrysu + rendry
- Pozn.: model je přední (větší) tlapa; zadní lze vygenerovat z druhého,
  menšího obrysu ve vzoru.
