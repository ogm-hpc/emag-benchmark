#!/usr/bin/env python3
"""Mesh convergence of existing benchmark sets (docs/paper_plan.md B6).

The existing sets are meshed with lc = lambda/8 (mean edge about lambda/6,
PPW >= 6). Per set, the mesh sizes (all parameters lc*) are scaled by the
factors SCALES; each mesh is solved by run_pcb_benchmark.py run (the solver
v1.0 and the runner's standard, the solution saved; mumps/direct, below scale
0.6 npatch_asm/cocg), and every solution is
compared with the one on the finest mesh by pcb_mesh_convergence.edp
(relative L2, curl and H(curl) differences on the finest mesh, also over the
physical region without the UPML layers). With the observed order p from the
differences, the error of the benchmark mesh (scale 1) against the h -> 0
limit is estimated as d(1) / (1 - s_min^p) (Richardson).

  python3 freefem/pcb/mesh_convergence.py mesh       # meshes (gmsh, as generate_all_meshes.py)
  python3 freefem/pcb/mesh_convergence.py run        # solves (alone, solutions saved)
  python3 freefem/pcb/mesh_convergence.py compare    # differences to the finest -> JSON
  python3 freefem/pcb/mesh_convergence.py summary --out docs/results_v1/mac_m3pro
  ... --sets case2A:standard --scales 1,0.8          # some only

Scale 1 is the benchmark (B1) mesh itself: the regenerated mesh must have its
MD5 (else stop). Meshes: generated_meshes/convergence/h<scale>/<case>_<set>.msh;
results: results/pcb_meshconv/ (runs, logs, solutions, compare.json).
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
sys.path.insert(0, str(PCB_DIR))
sys.path.insert(0, str(ROOT / "gmsh_templates"))
import run_pcb_benchmark as rpb  # noqa: E402
import inject_params  # noqa: E402

# the existing sets of the Core suite (docs/paper_plan.md B6: "representative")
SETS = ("case1A:standard", "case2A:standard", "case2A:off_resonance", "case3A:high_contrast")
SCALES = (1.0, 0.8, 0.63, 0.5)
COMBO = "mumps/direct"
# below this scale MUMPS needs more than the 18 GB of the M3 Pro (h0.63: 9.3 GB,
# case2A): the node-patch COCG (rtol 1e-8; converged in all 112 sets of v1.0,
# H(curl) difference to MUMPS <= 3e-9 on these sets)
ITER_COMBO, ITER_BELOW = "npatch_asm/cocg", 0.6


def combo_of(s: float) -> str:
    return ITER_COMBO if s < ITER_BELOW else COMBO
MESH_DIR = ROOT / "generated_meshes" / "convergence"
OUT = ROOT / "results" / "pcb_meshconv"
B1_MD5 = ROOT / "docs" / "results_v1" / "mac_m3pro" / "mesh_md5.txt"
ERR_RE = re.compile(r"MESHCONV_ERR ndof (\d+) l2 (\S+) curl (\S+) hcurl (\S+) "
                    r"l2core (\S+) curlcore (\S+) hcurlcore (\S+)")


def label(s: float) -> str:
    return f"h{s:.2f}"


def mesh_path(cs: str, s: float) -> Path:
    case, pset = cs.split(":")
    return MESH_DIR / label(s) / f"{case}_{pset}.msh"


def sol_path(cs: str, s: float) -> Path:
    case, pset = cs.split(":")
    return OUT / "solutions" / f"{case}_{pset}@{label(s)}__{combo_of(s).replace('/', '_')}.sol.gz"


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def cmd_mesh(a) -> int:
    db = rpb.load_existing_cases()
    b1 = {Path(line.split()[1]).name: line.split()[0] for line in B1_MD5.read_text().splitlines()}
    for cs in a.sets:
        case, pset = cs.split(":")
        for s in a.scales:
            msh = mesh_path(cs, s)
            if msh.exists():
                print(f"{cs} {label(s)}: exists ({msh.relative_to(ROOT)})")
                continue
            d = copy.deepcopy(db)
            ps = d[case]["parameter_sets"][pset]
            for k in [k for k in ps if k.startswith("lc")]:
                ps[k] = ps[k] * s
            geo = msh.parent / "geo" / f"{case}_{pset}.geo"
            geo.parent.mkdir(parents=True, exist_ok=True)
            if not inject_params.inject_params(case, pset, geo, d):
                return 1
            p = subprocess.run([a.gmsh, str(geo), "-3", "-format", "msh2", "-o", str(msh)],
                               capture_output=True, text=True)
            if p.returncode != 0:
                print(p.stdout[-2000:], p.stderr[-2000:])
                return 1
            print(f"{cs} {label(s)}: {msh.relative_to(ROOT)} ({msh.stat().st_size / 2**20:.0f} MB)")
            if s == 1.0 and b1.get(msh.name) != md5(msh):
                print(f"ERROR: {msh.name} at scale 1 differs from the B1 mesh (MD5 {md5(msh)} vs {b1.get(msh.name)})")
                return 1
    return 0


def cmd_run(a) -> int:
    rc = 0
    for s in a.scales:
        sets = [cs for cs in a.sets if mesh_path(cs, s).exists()]
        if not sets:
            continue
        cmd = [sys.executable, str(PCB_DIR / "run_pcb_benchmark.py"), "run", "--sets", ",".join(sets),
               "--combos", combo_of(s), "--existing-mesh-dir", str(MESH_DIR / label(s)), "--tag", label(s),
               "--save-solutions", "--out", str(OUT), "--workers", "1", "--mem-budget", "0"]
        print("$ " + " ".join(cmd), flush=True)
        rc |= subprocess.run(cmd).returncode
    return rc


def core_labels(msh: Path) -> str:
    phys = rpb.rfb.parse_physical_names(msh)
    vols = [(t, n) for (dim, n), t in phys.items() if dim == 3]
    return ",".join(str(t) for t, n in sorted(vols) if not n.upper().startswith("PML"))


def unzip(src: Path, dst: Path) -> Path:
    with gzip.open(src, "rb") as fi, open(dst, "wb") as fo:
        shutil.copyfileobj(fi, fo)
    return dst


def run_json(cs: str, s: float) -> dict:
    case, pset = cs.split(":")
    return json.loads((OUT / "runs" / f"{case}_{pset}@{label(s)}__{combo_of(s).replace('/', '_')}.json").read_text())


def cmd_compare(a) -> int:
    res_file = OUT / "compare.json"
    res = json.loads(res_file.read_text()) if res_file.exists() else {}
    scratch = Path(a.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    rc = 0
    for cs in a.sets:
        done = [s for s in a.scales if sol_path(cs, s).exists()]
        if len(done) < 2:
            print(f"{cs}: fewer than 2 solutions ({[label(s) for s in done]})")
            continue
        sf = min(done)
        fine = unzip(sol_path(cs, sf), scratch / "fine.sol")
        k0 = (run_json(cs, sf).get("pcb") or {}).get("k0")
        core = core_labels(mesh_path(cs, sf))
        rows = []
        for s in sorted(done, reverse=True):
            r = run_json(cs, s)
            row = dict(scale=s, combo=combo_of(s), ndof=r.get("dof") or r.get("ndof"), status=r.get("status"),
                       iterations=r.get("iterations"),
                       mesh_md5=md5(mesh_path(cs, s)))
            if s != sf:
                coarse = unzip(sol_path(cs, s), scratch / "coarse.sol")
                p = subprocess.run(["FreeFem++-mpi", "-nw", "-v", "0", "pcb_mesh_convergence.edp",
                                    "-fm", str(mesh_path(cs, sf)), "-fs", str(fine),
                                    "-cm", str(mesh_path(cs, s)), "-cs", str(coarse),
                                    "-k0", repr(k0), "-core", core],
                                   cwd=PCB_DIR, capture_output=True, text=True)
                m = ERR_RE.search(p.stdout)
                if not m:
                    print(f"{cs} {label(s)}: FAILED\n{p.stdout[-2000:]}")
                    rc = 1
                    continue
                row.update(dict(zip(("ndof_check", "l2", "curl", "hcurl", "l2core", "curlcore", "hcurlcore"),
                                    [int(m.group(1))] + [float(x) for x in m.groups()[1:]])))
            rows.append(row)
            print(f"{cs} {label(s)}: {row}", flush=True)
        res[cs] = dict(finest=sf, k0=k0, core_labels=core, rows=rows)
    res_file.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"-> {res_file}")
    return rc


def estimate(rows: list, key: str, sf: float) -> dict:
    """Order p and error of scale 1, C, from the differences d(s) to the finest
    solution (s > sf). On non-nested meshes the two discretization errors are
    nearly uncorrelated, so d(s)^2 = C^2 (s^2p + sf^2p) (checked with the
    Nedelec interpolants of a smooth field on the case2A meshes h1.00 / h0.50:
    0.0615 and 0.0307 against the exact field, 0.0686 between them,
    sqrt(0.0615^2 + 0.0307^2) = 0.0687), not C (s^p - sf^p) as for nested
    meshes. Least squares in log d over p in 0.1..4; fit: rms log misfit."""
    pts = [(r["scale"], r[key]) for r in rows if key in r and r["scale"] != sf]
    if len(pts) < 2:
        return dict(p=None, err1=None, fit=None)
    best = None
    for i in range(391):
        p = 0.1 + i * 0.01
        g = [math.log(math.sqrt(s ** (2 * p) + sf ** (2 * p))) for s, _ in pts]
        lc = sum(math.log(d) - gi for gi, (_, d) in zip(g, pts)) / len(pts)
        r = math.sqrt(sum((lc + gi - math.log(d)) ** 2 for gi, (_, d) in zip(g, pts)) / len(pts))
        if best is None or r < best[0]:
            best = (r, p, math.exp(lc))
    return dict(p=best[1], err1=best[2], fit=best[0])


def cmd_summary(a) -> int:
    res = json.loads((OUT / "compare.json").read_text())
    md = ["# 既存ケースのメッシュ収束（B6）", "",
          "`freefem/pcb/mesh_convergence.py summary` が出力。lc（パラメータ `lc*`）に倍率 s を掛けたメッシュで "
          f"`{COMBO}`（s < {ITER_BELOW} は MUMPS のメモリが足りないので `{ITER_COMBO}`、rtol 1e-8。ソルバー v1.0）で解き、最も細かいメッシュの解との相対差（最も細かいメッシュの上で積分、"
          "core は UPML を除いた領域）。s = 1 はベンチマークのメッシュ（B1）そのもの。"
          "メッシュが入れ子でないので2つの離散化誤差はほぼ無相関で、差は \\(d(s)^2 = C^2(s^{2p} + s_{\\min}^{2p})\\) "
          "に従う（滑らかな場の補間で確認、`estimate` の注）。p はこの当てはめによる見かけの次数、"
          "err(1) = C は s = 1（ベンチマークのメッシュ）の誤差の推定（h → 0 の極限に対する）、"
          "fit は log d の当てはめの残差（rms）。", ""]
    cols = ["set", "s", "ndof", "l2", "curl", "hcurl", "l2core", "curlcore", "hcurlcore"]
    md += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    est_rows = []
    for cs, d in res.items():
        for r in d["rows"]:
            md.append("| " + " | ".join([cs, f"{r['scale']:.2f}", str(r["ndof"])]
                                         + [f"{r[k]:.2e}" if k in r else "(ref)" for k in cols[3:]]) + " |")
        e = {k: estimate(d["rows"], k, d["finest"]) for k in ("hcurl", "hcurlcore", "l2core")}
        est_rows.append((cs, e))
    md += ["", "| set | p (hcurl) | err(1) hcurl | fit | p (hcurlcore) | err(1) hcurlcore | fit "
           "| p (l2core) | err(1) l2core | fit |", "|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x, s: "" if x is None else s.format(x)
    for cs, e in est_rows:
        md.append(f"| {cs} | " + " | ".join(f"{f(e[k]['p'], '{:.2f}')} | {f(e[k]['err1'], '{:.2e}')} "
                                             f"| {f(e[k]['fit'], '{:.3f}')}"
                                             for k in ("hcurl", "hcurlcore", "l2core")) + " |")
    text = "\n".join(md) + "\n"
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "mesh_convergence.md").write_text(text, encoding="utf-8")
        (a.out / "mesh_convergence.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"-> {a.out / 'mesh_convergence.md'}")
    else:
        print(text)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["mesh", "run", "compare", "summary"])
    ap.add_argument("--sets", default=",".join(SETS))
    ap.add_argument("--scales", default=",".join(str(s) for s in SCALES))
    ap.add_argument("--gmsh", default="gmsh")
    ap.add_argument("--scratch", default="/tmp/emag_pcb_meshconv")
    ap.add_argument("--out", type=Path, default=None, help="summary: directory for mesh_convergence.md / .json")
    a = ap.parse_args()
    a.sets = [s for s in a.sets.split(",") if s]
    a.scales = [float(s) for s in a.scales.split(",") if s]
    return dict(mesh=cmd_mesh, run=cmd_run, compare=cmd_compare, summary=cmd_summary)[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
