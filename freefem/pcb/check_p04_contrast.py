#!/usr/bin/env python3
"""P04 contrast-series check (pcb_problem_benchmark_settings.md 5.8; handoff task J-2).

Reads the P04 result JSONs (run_pcb_benchmark.py run, E2 excitation, usually
--combos mumps/direct) and prints, per parameter set, S11, S21 and the
effective permittivity from the S21 phase: the eps_eff for which the lossless
line model between the two 50 Ohm ports (air impedance Z01 of the strip from
Hammerstad-Jensen, Z0 = Z01/sqrt(eps_eff)) has the phase of the FEM S21.

The phase fixes eps_eff only up to steps of 2 pi in beta L, so the root is
chosen by continuity along the contrast series: for eps2 = eps1 = 1 the root
nearest to 1, then, in the order of growing eps2, the smallest root above the
eps_eff of the previous set (the electrical length grows with eps2, by less
than a wavelength per step).

The board is a stack of four layers eps1, eps2, eps1, eps2 of equal thickness
(eps1 = 1). There is no closed form for the strip on it; two quasi-static
values are printed for orientation:

  series   Hammerstad-Jensen with the homogeneous substrate that has the same
           parallel-plate capacitance as the stack,
           eps_eq = 4 / (2/eps1 + 2/eps2)   (-> 2 eps1 for eps2 -> infinity);
           it ignores the fringing field, which runs along the high-eps top layer
  upper    Hammerstad-Jensen with eps2 in all four layers

Checks (exit status 1 if one fails), per mesh series (the sets' own meshes;
the sets on the eps2 = 100 mesh, names *_m100 together with P04-4):
  1. eps2 = eps1 = 1 (no dielectric): eps_eff = 1 within --tol-air (the lumped
     ports lengthen the line electrically: P01 shows +10 % on its medium mesh)
  2. every set has a root by continuity, and it is <= the upper value (with
     the same tolerance)
The difference of S between a set and its *_m100 twin (same physics, finer
in-plane mesh) is printed as a mesh-sensitivity figure.

  python3 freefem/pcb/check_p04_contrast.py                     # results/pcb_benchmark
  python3 freefem/pcb/check_p04_contrast.py --combo cslp_hx_gmres
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

from check_p01_sparams import C0_MM_GHZ, fmt, hammerstad_jensen

ROOT = Path(__file__).resolve().parents[2]
PROBLEM = "P04"


def series_eps(eps1: float, eps2: float) -> float:
    """Homogeneous permittivity with the parallel-plate capacitance of the
    stack eps1, eps2, eps1, eps2 (equal thicknesses)."""
    return 4.0 / (2.0 / eps1 + 2.0 / eps2)


def eps_eff_roots(s21: complex, f_ghz: float, L: float, w: float, h: float, lo: float, hi: float,
                  R: float = 50.0) -> list:
    """All eps_eff in [lo, hi] whose lossless line-model S21 (air impedance of the
    strip, Z0 = Z01/sqrt(eps_eff), between two R ports) has the phase of s21.
    The roots are about 2 pi apart in beta L."""
    z01, _ = hammerstad_jensen(w, h, 1.0)
    k0 = 2 * math.pi * f_ghz / C0_MM_GHZ

    def dphase(ee: float) -> float:
        bl = k0 * math.sqrt(ee) * L
        z0 = z01 / math.sqrt(ee)
        a = math.cos(bl)
        b, c = 1j * z0 * math.sin(bl), 1j * math.sin(bl) / z0
        return cmath.phase((2 / (a + b / R + c * R + a)) / s21)

    n = max(4000, int(400 * (hi - lo)))
    grid = [lo + (hi - lo) * k / n for k in range(n + 1)]
    vals = [dphase(e) for e in grid]
    roots = []
    for k in range(n):
        v0, v1 = vals[k], vals[k + 1]
        if v0 == 0:
            roots.append(grid[k])
        elif v0 * v1 < 0 and abs(v0 - v1) < math.pi:   # a sign change, not a 2 pi wrap
            a, b = grid[k], grid[k + 1]
            for _ in range(60):
                mid = 0.5 * (a + b)
                if dphase(a) * dphase(mid) <= 0:
                    b = mid
                else:
                    a = mid
            roots.append(0.5 * (a + b))
    return roots


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark")
    ap.add_argument("--combo", default="mumps_direct", help="preset_krylov part of the result names")
    ap.add_argument("--tol-air", type=float, default=0.15,
                    help="relative tolerance of eps_eff = 1 without dielectric, and of the upper bound")
    args = ap.parse_args()
    params_db = json.loads((ROOT / "freefem" / "pcb" / "pcb_case_parameters.json").read_text(encoding="utf-8"))
    sets = params_db[PROBLEM]["parameter_sets"]
    tol = args.tol_air
    rows = {}
    for name, p in sets.items():
        fp = args.out / "runs" / f"{PROBLEM}_{name}__{args.combo}.json"
        if not fp.exists():
            print(f"{name}: no result {fp.name}")
            continue
        r = json.loads(fp.read_text(encoding="utf-8"))
        s = ((r.get("pcb") or {}).get("ports") or {}).get("S") or {}
        if "S21" not in s:
            print(f"{name}: no S-parameters (status {r.get('status')})")
            continue
        h = 4 * p["tLayer"]
        e1, e2 = p["epsSub"], p["epsSub2"]
        z0_s, ee_s = hammerstad_jensen(p["w"], h, series_eps(e1, e2))
        z0_u, ee_u = hammerstad_jensen(p["w"], h, max(e1, e2))
        rows[name] = dict(p=p, r=r, h=h, s11=complex(*s["S11"]), s21=complex(*s["S21"]), e2=e2, ee=None,
                          f=r["pcb"].get("freq_GHz", p["freqGHz"]), ee_s=ee_s, z0_s=z0_s, ee_u=ee_u, z0_u=z0_u)
    if not rows:
        print(f"no {PROBLEM} results for {args.combo} in {args.out / 'runs'}")
        return 1

    # eps_eff by continuity along each mesh series
    series = {"own mesh": [n for n in rows if "_m100" not in n],
              "eps2 = 100 mesh": [n for n in rows if "_m100" in n or sets[n]["epsSub2"] == 100.0]}
    for names in series.values():
        prev = None
        for n in sorted(names, key=lambda n: rows[n]["e2"]):
            d = rows[n]
            if d["ee"] is not None:       # P04-4 belongs to both series
                prev = d["ee"]
                continue
            roots = eps_eff_roots(d["s21"], d["f"], d["p"]["L"], d["p"]["w"], d["h"], 0.8,
                                  max(2.0, 1.5 * d["ee_u"]))
            if prev is None:
                d["ee"] = min(roots, key=lambda e: abs(e - 1.0)) if roots and d["e2"] == 1.0 else \
                    (min(roots) if roots else None)
            else:
                above = [e for e in roots if e > prev]
                d["ee"] = min(above) if above else None
            prev = d["ee"] if d["ee"] is not None else prev

    for name, d in rows.items():
        p, r, ee = d["p"], d["r"], d["ee"]
        print(f"== {name}  eps2={d['e2']:g}  f={d['f']} GHz  NDOF={r['ndof']}  status={r['status']}  "
              f"rss={r.get('peak_rss_gb')} GB")
        print(f"   S11  {fmt(d['s11'])}")
        print(f"   S21  {fmt(d['s21'])}")
        print("   eps_eff from the S21 phase: " + (f"{ee:.3f}" if ee is not None else "no root")
              + f" | series: eps_eff {d['ee_s']:.3f}, Z0 {d['z0_s']:.1f} Ohm"
              f" | upper (eps2 everywhere): eps_eff {d['ee_u']:.3f}, Z0 {d['z0_u']:.1f} Ohm"
              + (f" | L/lambda_g={p['L'] * d['f'] * math.sqrt(ee) / C0_MM_GHZ:.3f}" if ee is not None else ""))

    ok = True
    print("== checks")
    for name, d in rows.items():
        if d["ee"] is None:
            print(f"   {name}: no eps_eff  FAIL")
            ok = False
            continue
        if d["e2"] == d["p"]["epsSub"] == 1.0:
            good = abs(d["ee"] - 1.0) <= tol
            ok &= good
            print(f"   {name}: no dielectric, eps_eff {d['ee']:.3f} vs 1 ({100 * (d['ee'] - 1):+.1f} %, "
                  f"tol {100 * tol:.0f} %)  {'OK' if good else 'FAIL'}")
        good = d["ee"] <= d["ee_u"] * (1 + tol)
        ok &= good
        if not good:
            print(f"   {name}: eps_eff {d['ee']:.3f} above the upper value {d['ee_u']:.3f}  FAIL")
    for label, names in series.items():
        names = sorted(names, key=lambda n: rows[n]["e2"])
        if len(names) < 2 or any(rows[n]["ee"] is None for n in names):
            continue
        print(f"   {label}: eps_eff " + " < ".join(f"{rows[n]['ee']:.3f} ({n})" for n in names)
              + "  (by continuity; all below the upper values: "
              + ("OK" if all(rows[n]["ee"] <= rows[n]["ee_u"] * (1 + tol) for n in names) else "FAIL") + ")")
    for name, d in rows.items():
        twin = rows.get(name + "_m100")
        if twin:
            print(f"   {name} vs {name}_m100 (mesh): |dS11| {abs(d['s11'] - twin['s11']):.4f}, "
                  f"|dS21| {abs(d['s21'] - twin['s21']):.4f}, "
                  f"S21 phase {math.degrees(cmath.phase(d['s21'] / twin['s21'])):+.2f} deg")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
