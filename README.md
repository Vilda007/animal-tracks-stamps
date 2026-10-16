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

1. Each animal directory has a **`params.json`** config: real track size
   (length × width, verified against online field guides - source links
   included), relief depth, claws, edge rounding, base margin, handle size,
   and the position of the track outline in the reference sheet
   (row/column, text cutoff).
2. `Scripts-Skripty/generate_stamp.py <animal-dir>` extracts the outline
   (threshold → contours → clustering → Douglas–Peucker → scale to real
   size) and generates an OpenSCAD model: base plate, **rounded** relief
   (domed like real paw pads), handle with the animal's name and L/R marker.
3. With `--stl` the script exports both STL variants directly
   (uses OpenSCAD CLI).

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

1. Každý adresář zvířete obsahuje konfiguraci **`params.json`**: reálná velikost
   stopy (délka × šířka, ověřená v online atlasech stop – odkazy uvedeny),
   hloubka reliéfu, drápy, zaoblení hran, okraj základny, rozměry madla
   a pozice stopy ve vzorovém obrázku (řádek/sloupec, oříznutí textu).
2. `Scripts-Skripty/generate_stamp.py <adresar-zvirete>` extrahuje obrys
   (prahování → kontury → shlukování → Douglas–Peucker → přepočet na reálnou
   velikost) a vygeneruje OpenSCAD model: základní deska, **zaoblený** reliéf
   (klenutý jako skutečné polštářky), madlo s názvem a označením L/R.
3. S přepínačem `--stl` skript rovnou exportuje obě STL varianty
   (volá OpenSCAD CLI).

Potřeba: Python (numpy, Pillow, matplotlib) a OpenSCAD (CLI pro export STL).

### Tipy pro tisk

- Bez podpěr; tisknout textem nahoru, vrstva 0.2 mm, PLA/PETG.
- Zatlačit rovnoměrně do měkkého bláta/hlíny — hloubka otisku odpovídá výšce reliéfu.

---

*Project generated in collaboration with Claude Code. No secrets, no credentials
in this repository – ever.*
