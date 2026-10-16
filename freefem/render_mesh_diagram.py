#!/usr/bin/env python3
"""Render a 3D boundary-surface mesh diagram (PNG) from an MSH2 file,
color-coded by physical surface group. No GUI/OpenGL needed (gmsh's own
image export requires a display, unavailable headless in WSL) -- this parses
the raw .msh text and draws the boundary triangles with matplotlib.

Usage:
  python3 freefem/render_mesh_diagram.py --mesh <path.msh> --out <path.png> \
      [--title "..."] [--elev 20] [--azim -60]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Categorical palette (dataviz skill reference, slots 1-7), reused for
# physical-group identity here (not a data chart, but keeping one consistent
# palette across this project's visual output).
GROUP_COLORS = {
    "PEC": "#7c8592", "PECWall": "#7c8592",
    "PortOut": "#2a78d6", "PortIn": "#2a78d6",
    "LossyMaterial": "#e87ba4", "Eps100": "#eb6834", "Eps1": "#cde2fb",
    "RodsHighEps": "#eb6834", "HighK": "#eb6834", "Lossy": "#e87ba4",
    "Air": "#cde2fb", "BackgroundAir": "#cde2fb",
}
DEFAULT_COLOR = "#9085e9"


def parse_msh2(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    def section(name):
        i0 = lines.index(f"${name}")
        i1 = lines.index(f"$End{name}")
        return lines[i0 + 1:i1]

    phys_lines = section("PhysicalNames")
    n_phys = int(phys_lines[0])
    phys = {}
    for ln in phys_lines[1:1 + n_phys]:
        m = re.match(r"^(\d+)\s+(\d+)\s+\"(.+)\"$", ln.strip())
        if m:
            phys[int(m.group(2))] = (int(m.group(1)), m.group(3))

    node_lines = section("Nodes")
    n_nodes = int(node_lines[0])
    coords = {}
    for ln in node_lines[1:1 + n_nodes]:
        parts = ln.split()
        nid = int(parts[0])
        coords[nid] = (float(parts[1]), float(parts[2]), float(parts[3]))

    elem_lines = section("Elements")
    n_elem = int(elem_lines[0])
    tris_by_group = {}
    tets_by_group = {}
    for ln in elem_lines[1:1 + n_elem]:
        parts = list(map(int, ln.split()))
        etype = parts[1]
        ntags = parts[2]
        phys_id = parts[3]
        if etype == 2:  # 3-node triangle (boundary face)
            node_ids = parts[3 + ntags: 3 + ntags + 3]
            tris_by_group.setdefault(phys_id, []).append(node_ids)
        elif etype == 4:  # 4-node tetrahedron (volume region)
            node_ids = parts[3 + ntags: 3 + ntags + 4]
            tets_by_group.setdefault(phys_id, []).append(node_ids)

    return phys, coords, tris_by_group, tets_by_group


def _tet_plane_polygon(pts, axis_idx, offset):
    """Intersect a tetrahedron (4 xyz points) with the plane coord[axis_idx]=offset.
    Returns a list of 2D points (in the OTHER two coords, in order) forming the
    cross-section polygon (empty if the plane misses the tet)."""
    d = [p[axis_idx] - offset for p in pts]
    other = [i for i in range(3) if i != axis_idx]
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    poly = []
    for i, j in edges:
        di, dj = d[i], d[j]
        if di == 0:
            poly.append((pts[i][other[0]], pts[i][other[1]]))
        if dj == 0:
            poly.append((pts[j][other[0]], pts[j][other[1]]))
        if di * dj < 0:
            t = di / (di - dj)
            x = pts[i][other[0]] + t * (pts[j][other[0]] - pts[i][other[0]])
            y = pts[i][other[1]] + t * (pts[j][other[1]] - pts[i][other[1]])
            poly.append((x, y))
    if len(poly) < 3:
        return []
    # Order points around their centroid (angle sort) to get a proper polygon
    # (a tet-plane intersection is always convex: a triangle or quadrilateral).
    pts_arr = np.array(poly)
    pts_arr = np.unique(np.round(pts_arr, 12), axis=0)
    if len(pts_arr) < 3:
        return []
    c = pts_arr.mean(axis=0)
    ang = np.arctan2(pts_arr[:, 1] - c[1], pts_arr[:, 0] - c[0])
    order = np.argsort(ang)
    return pts_arr[order].tolist()


def render_slice(phys, coords, tets_by_group, out, title, axis, offset, slab, figsize):
    """Fill the actual tet/cutting-plane intersection polygons, colored by
    volume region -- shows internal material structure (checkerboards, rod
    arrays, embedded rods) that isn't exposed as its own tagged boundary
    surface in this project's meshes (only the outer PEC/port envelope is a
    tagged Physical Surface; internal material boundaries are plain untagged
    tet faces). `slab` is unused for the geometric cut (exact plane
    intersection needs none) but kept for CLI compatibility."""
    axis_idx = {"x": 0, "y": 1, "z": 2}[axis]
    fig, ax = plt.subplots(figsize=(figsize, figsize))

    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection

    for phys_id, tets in sorted(tets_by_group.items()):
        dim, name = phys.get(phys_id, (3, f"id{phys_id}"))
        if dim != 3:
            continue
        color = GROUP_COLORS.get(name, DEFAULT_COLOR)
        patches = []
        for tet in tets:
            pts = [coords[n] for n in tet]
            poly = _tet_plane_polygon(pts, axis_idx, offset)
            if len(poly) >= 3:
                patches.append(Polygon(poly, closed=True))
        if not patches:
            continue
        coll = PatchCollection(patches, facecolor=color, edgecolor="#00000015", linewidths=0.3, label=name)
        ax.add_collection(coll)

    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_axis_off()
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS.get(phys.get(pid, (3, ""))[1], DEFAULT_COLOR))
               for pid in tets_by_group if phys.get(pid, (3, ""))[0] == 3]
    labels = [phys.get(pid, (3, f"id{pid}"))[1] for pid in tets_by_group if phys.get(pid, (3, ""))[0] == 3]
    ax.legend(handles, labels, loc="upper left", frameon=False, fontsize=11, bbox_to_anchor=(0.0, 1.0))
    if title:
        ax.set_title(title, fontsize=13)
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    fig.savefig(out, dpi=160, facecolor="white")
    print(f"Wrote {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--title", type=str, default="")
    p.add_argument("--elev", type=float, default=22)
    p.add_argument("--azim", type=float, default=-55)
    p.add_argument("--figsize", type=float, default=7.5)
    p.add_argument("--slice", type=str, default="", choices=["", "x", "y", "z"],
                   help="Render a 2D cross-section slice (tet centroids near the cutting plane, "
                        "colored by volume region) instead of the 3D boundary-surface mesh -- use "
                        "for cases whose interesting structure is an internal material region "
                        "(checkerboard, rod array, embedded rod) not exposed as its own tagged "
                        "boundary surface.")
    p.add_argument("--slice-offset", type=float, default=0.0)
    p.add_argument("--slice-slab", type=float, default=None,
                   help="Half-thickness of the slab selected around the cutting plane (default: "
                        "~1 mesh element's worth, auto-estimated)")
    args = p.parse_args()

    phys, coords, tris_by_group, tets_by_group = parse_msh2(args.mesh)

    if args.slice:
        if args.slice_slab is None:
            all_pts = np.array(list(coords.values()))
            span = (all_pts.max(axis=0) - all_pts.min(axis=0)).max()
            args.slice_slab = span / 40.0
        render_slice(phys, coords, tets_by_group, args.out, args.title,
                     args.slice, args.slice_offset, args.slice_slab, args.figsize)
        return 0

    fig = plt.figure(figsize=(args.figsize, args.figsize))
    ax = fig.add_subplot(111, projection="3d")

    all_pts = np.array(list(coords.values()))
    center = all_pts.mean(axis=0)
    span = (all_pts.max(axis=0) - all_pts.min(axis=0)).max() / 2.0

    legend_handles = []
    for phys_id, tris in sorted(tris_by_group.items()):
        dim, name = phys.get(phys_id, (2, f"id{phys_id}"))
        if dim != 2:
            continue
        color = GROUP_COLORS.get(name, DEFAULT_COLOR)
        polys = [[coords[n] for n in tri] for tri in tris]
        alpha = 0.25 if name in ("PEC", "PECWall") else 0.85
        edge = "#00000022" if name in ("PEC", "PECWall") else "#1c1f2455"
        coll = Poly3DCollection(polys, facecolor=color, edgecolor=edge, linewidths=0.15, alpha=alpha)
        ax.add_collection3d(coll)
        legend_handles.append((name, color))

    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_axis_off()

    seen = set()
    handles = []
    for name, color in legend_handles:
        if name in seen:
            continue
        seen.add(name)
        handles.append(plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=color,
                                   markeredgecolor="none", markersize=12, label=name))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 0.98), frameon=False, fontsize=10)

    if args.title:
        ax.set_title(args.title, fontsize=13, pad=0)

    fig.patch.set_facecolor("white")
    plt.tight_layout()
    fig.savefig(args.out, dpi=160, facecolor="white")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
