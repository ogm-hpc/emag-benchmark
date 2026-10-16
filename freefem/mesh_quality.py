#!/usr/bin/env python3
"""Mesh size / resolution report for the benchmark meshes (MSH 2.2).

For every generated_meshes/mesh/case*.msh: tetrahedra, Edge03d DOF (= number of
edges), and per volume region the mean edge length h and the points per LOCAL
wavelength PPW = lambda0 / sqrt(eps_r) / h (the eps_r the solver assigns, from
case_parameters.json; PML regions excluded). Writes results/mesh_quality.json.

  python3 freefem/mesh_quality.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import run_freefem_batch as rfb

EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def mesh_stats(path: Path) -> dict:
    lines = path.read_text(errors="ignore").split("\n")
    i = lines.index("$PhysicalNames")
    names = {}
    for l in lines[i + 2:i + 2 + int(lines[i + 1])]:
        d, t, nm = l.split(maxsplit=2)
        names[(int(d), int(t))] = nm.strip('"')
    i = lines.index("$Nodes")
    nnode = int(lines[i + 1])
    rows = [l.split() for l in lines[i + 2:i + 2 + nnode]]
    ids = np.array([int(r[0]) for r in rows])
    xyz = np.array([r[1:4] for r in rows], dtype=float)
    idmap = np.zeros(ids.max() + 1, dtype=np.int64)
    idmap[ids] = np.arange(nnode)
    i = lines.index("$Elements")
    tets, tags = [], []
    for l in lines[i + 2:i + 2 + int(lines[i + 1])]:
        p = l.split()
        if p[1] == "4":
            nt = int(p[2])
            tags.append(int(p[3]))
            tets.append(p[3 + nt:3 + nt + 4])
    tets = idmap[np.array(tets, dtype=np.int64)]
    tags = np.array(tags)
    e = np.sort(np.concatenate([tets[:, list(ab)] for ab in EDGES]), axis=1)
    nedge = len(np.unique(e[:, 0] * (nnode + 1) + e[:, 1]))
    regions = {}
    for t in np.unique(tags):
        sel = tets[tags == t]
        ee = np.concatenate([sel[:, list(ab)] for ab in EDGES])
        h = np.linalg.norm(xyz[ee[:, 0]] - xyz[ee[:, 1]], axis=1)
        regions[names.get((3, int(t)), str(t))] = dict(tets=int(len(sel)), h_mean=float(h.mean()))
    return dict(nodes=nnode, tets=int(len(tets)), dof=int(nedge), regions=regions)


def eps_of(region: str, p: dict) -> float:
    """Real part of eps_r that maxwell_common.idp assigns to a region."""
    table = {
        "SphereDielectric": p.get("epsSphere", 10.0), "Layer2_CeramicOrHighK": p.get("kappa", 10.0),
        "PTFE": 2.1, "Alumina": 9.8, "Eps100": 100.0, "RodsHighEps": p.get("epsRods", 50.0),
        "HighK": p.get("kappa", 10.0), "Lossy": p.get("epsLossy", 10.0),
        "LossyMaterial": p.get("epsLossy", 10.0),
    }
    return float(table.get(region, 1.0))


def main() -> int:
    db = rfb.load_case_params()
    out = {}
    for t in rfb.discover_mesh_tasks(rfb.DEFAULT_MESH_DIR):
        p = db.get(t.case_name, {}).get("parameter_sets", {}).get(t.param_set)
        if p is None:
            continue
        s = mesh_stats(t.mesh_path)
        lam0 = 2 * math.pi / rfb.pick_k0(t.case_name, p)
        worst = None
        for reg, r in s["regions"].items():
            r["eps"] = eps_of(reg, p)
            if reg.startswith("PML_"):
                continue
            r["ppw"] = lam0 / math.sqrt(r["eps"]) / r["h_mean"]
            if worst is None or r["ppw"] < worst[1]:
                worst = (reg, r["ppw"])
        s.update(lambda0_eff=lam0, worst_region=worst[0], ppw_min=worst[1])
        out[f"{t.case_name}:{t.param_set}"] = s
        print(f"{t.case_name}:{t.param_set:28s} DOF={s['dof']:7d} PPWmin={worst[1]:5.1f} ({worst[0]})", flush=True)
    (rfb.ROOT / "results" / "mesh_quality.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
