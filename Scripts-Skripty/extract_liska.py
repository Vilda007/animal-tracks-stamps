#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract fox (liska) paw-print outline from the reference sheet and generate
an OpenSCAD stamp model with rounded (domed) relief - paw pads do not have
sharp edges, so every island tapers smoothly toward the tip.

Input : Tracks-Stopy/STOPY-1.png  (LIŠKA = top row, 4th of 6 columns)
Output: Animals-Zvirata/Fox-Liska/fox_stamp.scad + mask/preview images
"""
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Tracks-Stopy", "STOPY-1.png")
OUT = os.path.join(ROOT, "Animals-Zvirata", "Fox-Liska")
os.makedirs(OUT, exist_ok=True)
prev = os.path.join(OUT, "previews")
os.makedirs(prev, exist_ok=True)

img = Image.open(SRC).convert("L")
a = np.array(img)
H, W = a.shape

# LIŠKA: top row, 4th column of 6
col_w = W // 6
crop = a[: H // 2, 3 * col_w : 4 * col_w]
bw = (crop < 128).astype(float)

# --- outline loops of all black blobs ----------------------------------------
fig, ax = plt.subplots()
cs = ax.contour(bw, levels=[0.5])
plt.close(fig)

loops = []
for p in cs.allsegs[0]:
    if len(p) < 10:
        continue
    x, y = p[:, 0], p[:, 1]
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    loops.append(dict(path=p, area=area,
                      xmin=x.min(), xmax=x.max(), ymin=y.min(), ymax=y.max(),
                      cx=x.mean(), cy=y.mean()))

# "LIŠKA" label is at the bottom of the crop -> cut off
Y_TEXT = 620
parts = [l for l in loops if l["ymax"] < Y_TEXT and l["area"] > 30]

# --- two paws = k-means (k=2) over part centroids -----------------------------
C = np.array([[l["cx"], l["cy"]] for l in parts])
A = np.array([l["area"] for l in parts])
t = C[:, 0] + C[:, 1]  # paws lie on the diagonal
mu = np.array([C[np.argmin(t)], C[np.argmax(t)]], dtype=float)
for _ in range(50):
    d = ((C[:, None, :] - mu[None, :, :]) ** 2).sum(axis=2)
    asg = d.argmin(axis=1)
    new_mu = np.array([
        (C[asg == k] * A[asg == k, None]).sum(axis=0) / A[asg == k].sum()
        if (asg == k).any() else mu[k]
        for k in range(2)
    ])
    if np.allclose(new_mu, mu):
        break
    mu = new_mu
groups = [[i for i in range(len(parts)) if asg[i] == k] for k in range(2)]
groups.sort(key=lambda g: -sum(parts[i]["area"] for i in g))  # front = bigger

front = [parts[i] for i in groups[0]]
x0 = min(p["xmin"] for p in front); x1 = max(p["xmax"] for p in front)
y0 = min(p["ymin"] for p in front); y1 = max(p["ymax"] for p in front)

# --- Douglas-Peucker for closed loops -----------------------------------------
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

# --- to millimetres: real front fox track height ~ 57 mm ----------------------
REAL_HEIGHT_MM = 57.0
SCALE = REAL_HEIGHT_MM / (y1 - y0)
polys = []
for p in front:
    S = dp_closed(p["path"], 0.9)
    if len(S) < 3:
        continue
    S = S.astype(float)
    S[:, 0] = (S[:, 0] - (x0 + x1) / 2) * SCALE
    S[:, 1] = -((S[:, 1] - (y0 + y1) / 2) * SCALE)  # y up
    aa = 0.5 * abs(np.dot(S[:, 0], np.roll(S[:, 1], 1))
                   - np.dot(S[:, 1], np.roll(S[:, 0], 1)))
    if aa < 4:  # drop dust
        continue
    mindim = min(S[:, 0].max() - S[:, 0].min(), S[:, 1].max() - S[:, 1].min())
    polys.append((S, mindim, aa))
print("islands:", len(polys), "sizes:", [round(p[1], 1) for p in polys])

# --- save paw mask (source crop) ------------------------------------------------
Image.fromarray(((1 - bw) * 255).astype("uint8")).save(
    os.path.join(OUT, "fox_mask.png"))

# --- check image -----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 5))
for S, _, _ in polys:
    ax.fill(np.r_[S[:, 0], S[0, 0]], np.r_[S[:, 1], S[0, 1]], color="black")
ax.set_aspect("equal"); ax.invert_yaxis()
ax.set_title("fox front track [mm]")
fig.savefig(os.path.join(prev, "fox_outline_check.png"), dpi=120)

# --- OpenSCAD generation ----------------------------------------------------------
def poly_str(S):
    return "[" + ", ".join("[%.2f, %.2f]" % (q[0], q[1]) for q in S) + "]"

# relief with rounded tip: hull() over polygon layers inset towards the tip,
# inset scaled per island so tiny claw marks keep some body
relief_blocks = []
for S, mindim, area in polys:
    k = min(2.6, max(0.7, 0.16 * mindim))  # max inset at the tip [mm]
    k1, k2 = 0.45 * k, 0.8 * k
    P = poly_str(S)
    relief_blocks.append("""\
    hull() {
        translate([0, 0, -0.3])  linear_extrude(0.3) polygon(%s);
        translate([0, 0, -2.0])  linear_extrude(0.1) offset(r = -%.2f) polygon(%s);
        translate([0, 0, -3.6])  linear_extrude(0.1) offset(r = -%.2f) polygon(%s);
        translate([0, 0, -pattern_h]) linear_extrude(0.15) offset(r = -%.2f) polygon(%s);
    }""" % (P, k1, P, k2, P, k, P))
relief_scad = "\n".join(relief_blocks)

footprint_lines = "\n".join("    polygon(%s);" % poly_str(S) for S, _, _ in polys)

scad = """// Fox paw stamp (POC) - front paw, L/R variant
// Generated from Tracks-Stopy/STOPY-1.png by Scripts-Skripty/extract_liska.py
// Bottom relief is rounded (domed) - real paw pads have no sharp edges.

// --- stamp parameters --------------------------------------------------------
base_margin = 5;    // base outline margin around the track [mm]
base_h      = 4;    // base plate thickness [mm]
pattern_h   = 5;    // relief height = imprint depth in mud [mm]
handle_h    = 16;   // handle height [mm]
text_h      = 1.4;  // raised text height [mm]
name_cz     = "LIŠKA";
name_en     = "FOX";
side        = "L";  // "L" or "R"

module footprint() {  // full outline (for the base plate)
%s
}

module relief() {  // rounded imprint pattern (points down, into the mud)
%s
}

module base_shape() { offset(r = base_margin) footprint(); }

module stamp_body() {
    mirror(side == "R" ? [1, 0, 0] : [0, 0, 0])
    union() {
        relief();
        linear_extrude(base_h) base_shape();
    }
    // handle block with rounded corners (not mirrored, text stays readable)
    translate([0, 0, base_h - 0.2])
    linear_extrude(handle_h + 0.2)
        offset(r = 4) offset(delta = -4)
            square([38, 24], center = true);
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
""" % (footprint_lines, relief_scad)

with open(os.path.join(OUT, "fox_stamp.scad"), "w", encoding="utf-8") as f:
    f.write(scad)
print("SCAD written ->", os.path.join(OUT, "fox_stamp.scad"))
