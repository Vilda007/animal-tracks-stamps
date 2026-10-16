#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_stamp.py - config-driven stamp generator for one animal directory.

Usage:
    python Scripts-Skripty/generate_stamp.py Animals-Zvirata/Fox-Liska [--stl]

Reads <animal-dir>/params.json, extracts the paw outline from the reference
sheet, scales it to the real track size, and writes:
    <animal-dir>/<slug>_stamp.scad      parametric OpenSCAD model (side="L"/"R")
    <animal-dir>/<slug>_mask.png        source mask crop
    <animal-dir>/previews/<slug>_outline_check.png
With --stl and OpenSCAD available it also exports fox_stamp_L/R.stl.

Params documented in Animals-Zvirata/*/params.json.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- extraction
def extract_paw_polys(cfg):
    """Return list of (polygon Nx2 mm, min_dim mm, area mm2) for the paw."""
    src = cfg["source"]
    t = cfg["track"]
    img = Image.open(os.path.join(ROOT, src["sheet"])).convert("L")
    a = np.array(img)
    H, W = a.shape
    rh, cw = H // src["n_rows"], W // src["n_cols"]
    crop = a[src["row"] * rh : (src["row"] + 1) * rh,
             src["col"] * cw : (src["col"] + 1) * cw]
    bw = (crop < 128).astype(float)

    fig, ax = plt.subplots()
    cs = ax.contour(bw, levels=[0.5])
    plt.close(fig)

    loops = []
    for p in cs.allsegs[0]:
        if len(p) < 10:
            continue
        x, y = p[:, 0], p[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        loops.append(dict(path=p, area=area, cx=x.mean(), cy=x.mean()))
        loops[-1].update(xmin=x.min(), xmax=x.max(),
                         ymin=y.min(), ymax=y.max())

    parts = [l for l in loops
             if l["ymax"] < src.get("text_cutoff_px", crop.shape[0])
             and l["ymin"] >= src.get("text_top_cutoff_px", 0)
             and l["area"] > 30]

    # two paws in a cell -> k-means (k=2) over part centroids
    C = np.array([[l["cx"], l["cy"]] for l in parts])
    A = np.array([l["area"] for l in parts])
    dsum = C[:, 0] + C[:, 1]
    mu = np.array([C[np.argmin(dsum)], C[np.argmax(dsum)]], dtype=float)
    for _ in range(50):
        d = ((C[:, None, :] - mu[None, :, :]) ** 2).sum(axis=2)
        asg = d.argmin(axis=1)
        new_mu = np.array([
            (C[asg == k] * A[asg == k, None]).sum(axis=0) / A[asg == k].sum()
            if (asg == k).any() else mu[k]
            for k in range(2)])
        if np.allclose(new_mu, mu):
            break
        mu = new_mu
    groups = [[i for i in range(len(parts)) if asg[i] == k] for k in range(2)]
    groups.sort(key=lambda g: -sum(parts[i]["area"] for i in g))
    pick = groups[0] if src.get("paw_pick", "larger") == "larger" else groups[1]
    front = [parts[i] for i in pick]
    x0 = min(p["xmin"] for p in front); x1 = max(p["xmax"] for p in front)
    y0 = min(p["ymin"] for p in front); y1 = max(p["ymax"] for p in front)

    scale = t["length_mm"] / (y1 - y0)
    polys = []
    for p in front:
        S = dp_closed(p["path"], 0.9)
        if len(S) < 3:
            continue
        S = S.astype(float)
        S[:, 0] = (S[:, 0] - (x0 + x1) / 2) * scale
        S[:, 1] = -((S[:, 1] - (y0 + y1) / 2) * scale)  # y up
        area = 0.5 * abs(np.dot(S[:, 0], np.roll(S[:, 1], 1))
                         - np.dot(S[:, 1], np.roll(S[:, 0], 1)))
        if area < 4:
            continue
        mindim = min(np.ptp(S[:, 0]), np.ptp(S[:, 1]))
        polys.append((S, mindim, area))

    # --- rotation: pad->toes axis vertical (pointing up) ----------------------
    # anatomy-based, robust for near-round canine tracks: direction from the
    # largest part (palm pad) to the centroid of the small parts (toes/claws)
    i_big = max(range(len(polys)), key=lambda i: polys[i][2])
    pad_c = polys[i_big][0].mean(axis=0)
    small = [polys[i] for i in range(len(polys))
             if i != i_big and polys[i][2] < 0.35 * polys[i_big][2]]
    if small:
        toes_c = np.mean([s[0].mean(axis=0) for s in small], axis=0)
        d = toes_c - pad_c
        rot = np.pi / 2 - np.arctan2(d[1], d[0])
        R = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
        polys = [(S @ R.T, m, ar) for S, m, ar in polys]
        if abs(np.degrees(rot)) > 3:
            print("rotated paw by %.1f deg" % np.degrees(rot))

    got_w = max(S[:, 0].max() for S, _, _ in polys) - \
            min(S[:, 0].min() for S, _, _ in polys)
    want_w = t.get("width_mm")
    if want_w and abs(got_w - want_w) / want_w > 0.15:
        print("WARNING: resulting width %.1f mm vs configured %.1f mm"
              % (got_w, want_w))
    return polys, bw


def dp(P, eps):
    if len(P) < 3:
        return P
    a, b = P[0], P[-1]
    ab = b - a
    denom = np.hypot(ab[0], ab[1]) or 1e-9
    d = np.abs(ab[0] * (P[:, 1] - a[1]) - ab[1] * (P[:, 0] - a[0])) / denom
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([dp(P[: i + 1], eps)[:-1], dp(P[i:], eps)])
    return np.array([a, b])


def dp_closed(P, eps):
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    nn = len(P)
    c = P.mean(axis=0)
    i0 = int(np.argmax(((P - c) ** 2).sum(axis=1)))
    i1 = (i0 + nn // 2) % nn
    aa, bb = min(i0, i1), max(i0, i1)
    return np.vstack([dp(P[aa : bb + 1], eps)[:-1],
                      dp(np.vstack([P[bb:], P[: aa + 1]]), eps)[:-1]])


# ---------------------------------------------------------------- generation
def poly_str(S):
    return "[" + ", ".join("[%.2f, %.2f]" % (q[0], q[1]) for q in S) + "]"


def gen_scad(cfg):
    t = cfg["track"]
    polys, _ = extract_paw_polys(cfg)
    bevel = t.get("bevel_mm", 10.0)
    NL = int(t.get("bevel_steps", 12))
    D = t.get("relief_depth_mm", 5.0)
    relief_blocks = []
    for S, mindim, area in polys:
        # fillet radius: as requested, but capped so small islands (claws)
        # keep a flat core
        Rv = min(bevel, max(0.7, 0.45 * mindim))
        P = poly_str(S)
        layers = ["        translate([0, 0, -0.3])  linear_extrude(0.32) polygon(%s);" % P]
        for j in range(1, NL + 1):
            zj = -D * j / NL
            arg = zj + D - Rv
            ins = Rv - (max(0.0, Rv * Rv - arg * arg) ** 0.5)
            if ins < 0.01:
                shape = "polygon(%s)" % P
            else:
                shape = "offset(r = -%.2f) polygon(%s)" % (ins, P)
            layers.append("        translate([0, 0, %.2f])  linear_extrude(0.12) %s;"
                          % (zj, shape))
        relief_blocks.append("    hull() {\n%s\n    }" % "\n".join(layers))
    footprint_lines = "\n".join("    polygon(%s);" % poly_str(S)
                                for S, _, _ in polys)
    # convex base: circumscribed ellipse (or circle) around the whole track
    margin = t.get("base_margin_mm", 5.0)
    allx = np.concatenate([S[:, 0] for S, _, _ in polys])
    ally = np.concatenate([S[:, 1] for S, _, _ in polys])
    hx = np.ptp(allx) / 2 + margin
    hy = np.ptp(ally) / 2 + margin
    h = t["handle"]
    return SCAD_TEMPLATE % dict(
        footprint=footprint_lines,
        relief="\n".join(relief_blocks),
        base_margin=margin,
        base_shape=t.get("base_shape", "ellipse"),
        base_rx=hx, base_ry=hy,
        base_h=t.get("base_thickness_mm", 4.0),
        pattern_h=t.get("relief_depth_mm", 5.0),
        handle_h=h.get("thickness_mm", 16.0),
        handle_w=h.get("width_mm", 38.0),
        handle_d=h.get("height_mm", 24.0),
        handle_r=h.get("corner_r_mm", 4.0),
        text_h=t.get("text_height_mm", 1.4),
        name_cz=cfg["name_cz"], name_en=cfg["name_en"],
    ), polys


SCAD_TEMPLATE = """// Paw/hoof stamp - generated by Scripts-Skripty/generate_stamp.py
// Params: params.json in the same directory as this file.

base_margin = %(base_margin).2f;
base_shape  = "%(base_shape)s";  // "ellipse" or "circle"
base_rx     = %(base_rx).2f;  // ellipse half-axes incl. margin
base_ry     = %(base_ry).2f;
base_h      = %(base_h).2f;
pattern_h   = %(pattern_h).2f;
handle_h    = %(handle_h).2f;
handle_w    = %(handle_w).2f;
handle_d    = %(handle_d).2f;
handle_r    = %(handle_r).2f;
text_h      = %(text_h).2f;
name_cz     = "%(name_cz)s";
name_en     = "%(name_en)s";
side        = "L";  // "L" or "R"

module footprint() {  // full outline (base plate)
%(footprint)s
}

module relief() {  // rounded imprint pattern (points down, into the mud)
%(relief)s
}

module base_shape() {
    // convex circumscribed shape (ellipse or circle) - never copies the track
    if (base_shape == "circle")
        circle(r = max(base_rx, base_ry), $fn = 128);
    else
        scale([base_rx, base_ry]) circle(r = 1, $fn = 128);
}

module stamp_body() {
    mirror(side == "R" ? [1, 0, 0] : [0, 0, 0])
    union() {
        relief();
        linear_extrude(base_h) base_shape();
    }
    translate([0, 0, base_h - 0.2])
    linear_extrude(handle_h + 0.2)
        offset(r = handle_r) offset(delta = -handle_r)
            square([handle_w, handle_d], center = true);
}

module top_text() {
    translate([0, 0, base_h + handle_h - 0.1])
    linear_extrude(text_h)
    union() {
        translate([0, 4.5, 0])
            text(name_cz, size = 6.4, halign = "center",
                 font = "Liberation Sans:style=Bold");
        translate([0, -3.5, 0])
            text(name_en, size = 4.6, halign = "center",
                 font = "Liberation Sans:style=Bold");
        translate([0, -11, 0])
            text(side, size = 6.4, halign = "center",
                 font = "Liberation Sans:style=Bold");
    }
}

union() {
    stamp_body();
    top_text();
}
"""


def find_openscad():
    for c in (r"C:\Program Files\OpenSCAD\openscad.exe", "openscad"):
        try:
            subprocess.run([c, "--version"], capture_output=True, check=True)
            return c
        except (OSError, subprocess.CalledProcessError):
            continue
    return None


def main():
    animal_dir = sys.argv[1]
    do_stl = "--stl" in sys.argv
    with open(os.path.join(animal_dir, "params.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    scad_cfg = dict(cfg["stamp"])
    slug = cfg["animal"]["en"].lower().split()[-1]  # "Red fox" -> "fox"

    scad, polys = gen_scad(scad_cfg)
    scad_path = os.path.join(animal_dir, "%s_stamp.scad" % slug)
    with open(scad_path, "w", encoding="utf-8") as f:
        f.write(scad)
    print("islands:", len(polys), "->", scad_path)

    # mask + check image
    src = scad_cfg["source"]
    img = Image.open(os.path.join(ROOT, src["sheet"])).convert("L")
    a = np.array(img)
    H, W = a.shape
    rh, cw = H // src["n_rows"], W // src["n_cols"]
    crop = a[src["row"] * rh : (src["row"] + 1) * rh,
             src["col"] * cw : (src["col"] + 1) * cw]
    bw = (crop < 128).astype(float)
    Image.fromarray(((1 - bw) * 255).astype("uint8")).save(
        os.path.join(animal_dir, "%s_mask.png" % slug))
    prev = os.path.join(animal_dir, "previews")
    os.makedirs(prev, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    for S, _, _ in polys:
        ax.fill(np.r_[S[:, 0], S[0, 0]], np.r_[S[:, 1], S[0, 1]], color="black")
    ax.set_aspect("equal"); ax.invert_yaxis()
    ax.set_title("%s %s track [mm]" % (cfg["animal"]["en"], scad_cfg["paw"]))
    fig.savefig(os.path.join(prev, "%s_outline_check.png" % slug), dpi=120)

    if do_stl:
        osc = find_openscad()
        if not osc:
            print("OpenSCAD not found - skipping STL export")
        else:
            for side in ("L", "R"):
                out = os.path.join(animal_dir, "%s_stamp_%s.stl" % (slug, side))
                r = subprocess.run(
                    [osc, "-o", out, "--export-format", "binstl",
                     "-D", 'side="%s"' % side, scad_path],
                    capture_output=True, text=True)
                print(side, "STL:", "OK" if os.path.exists(out) else r.stderr)


if __name__ == "__main__":
    main()
