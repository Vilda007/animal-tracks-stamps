# Animal Tracks Stamps / Razítka stop zvěře

## English

3D-printable **stamps of animal tracks** — press them into mud, clay or sand to
leave a realistic paw/hoof print. Each stamp carries the animal's name
(Czech + English) and **L/R** marking on top of the handle.

### Repository structure

```
Animals-Zvirata/            per-animal directories (all directories use EN-CZ naming)
  Fox-Liska/                stamp model (.scad), printable STL (L+R), source mask,
                            previews, animal-specific notes
Tracks-Stopy/               track outline reference sheets (source images)
Scripts-Skripty/            generators (extract paw outline from a sheet -> .scad)
```

### How a stamp is made

1. A paw outline is extracted from a reference sheet (PNG, black track on white)
   by `Scripts-Skripty/extract_liska.py`: threshold → contour tracing
   (matplotlib) → per-part clustering (k-means) → Douglas–Peucker
   simplification → scaling to the real track size.
2. The script generates an OpenSCAD file: base plate, **rounded** relief
   (~5 mm tall, domed like real paw pads), handle with the animal's name and
   L/R marker.
3. STL export: `openscad -o fox_stamp_L.stl -D 'side="L"' fox_stamp.scad`

Requirements: Python (numpy, Pillow, matplotlib) and OpenSCAD (CLI for STL export).

### 3D printing tips

- No supports needed; print text side up, 0.2 mm layers, PLA/PETG.
- Press evenly into soft mud/clay; the relief depth gives the imprint depth.

---

## Česky

Razítka **stop zvířat pro 3D tisk** — zatlačením do bláta, hlíny nebo písku
zanechají realistickou stopu tlapky/kopýtka. Každé razítko má na madlu název
zvířete (česky + anglicky) a označení **L/P** (v STL jako L/R).

### Struktura repozitáže

```
Animals-Zvirata/            adresáře jednotlivých zvířat (pojmenování adresářů EN-CZ)
  Fox-Liska/                model razítka (.scad), tisknutelné STL (L+R), maska stopy,
                            náhledy, upřesňující informace k tlapkám
Tracks-Stopy/               vzorové obrázky stop (zdroj)
Scripts-Skripty/            generátory (extrakce obrysu stopy ze vzoru -> .scad)
```

### Jak razítko vzniká

1. Obrys tlapky se extrahuje z referenčního obrázku skriptem
   `Scripts-Skripty/extract_liska.py`: prahování → trasování kontur
   (matplotlib) → seskupení částí (k-means) → zjednodušení
   (Douglas–Peucker) → přepočet na reálnou velikost stopy.
2. Skript vygeneruje OpenSCAD soubor: základní deska, **zaoblený** reliéf
   (~5 mm, klenutý jako skutečné polštářky tlapky), madlo s názvem a L/R.
3. Export STL: `openscad -o fox_stamp_L.stl -D 'side="L"' fox_stamp.scad`

Potřeba: Python (numpy, Pillow, matplotlib) a OpenSCAD (CLI pro export STL).

### Tipy pro tisk

- Bez podpěr; tisknout textem nahoru, vrstva 0.2 mm, PLA/PETG.
- Zatlačit rovnoměrně do měkkého bláta/hlíny — hloubka otisku odpovídá výšce reliéfu.

---

*Project generated in collaboration with Claude Code. No secrets, no credentials
in this repository – ever.*
