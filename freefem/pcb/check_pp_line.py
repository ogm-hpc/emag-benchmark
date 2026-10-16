#!/usr/bin/env python3
"""Parallel-plate line check of the conductor models (handoff task N).

P05 parameter sets with portFull = 1: an open-ended parallel-plate line of
width W = planeX, length L = planeY, gap d, port over the whole end face y = 0,
PMC sides (fields uniform in x). The transmission-line solution with the
surface impedance Z_s of both plates,

    Z' = j omega mu0 d / W + 2 Z_s / W,   Y' = j omega eps0 eps_r (1 - j tan delta) W / d,
    gamma = sqrt(Z' Y'),  Z0 = sqrt(Z' / Y'),  Z_in = Z0 / tanh(gamma L),

is compared with Z11 = R (1 + S11)/(1 - S11) of the results (time convention
exp(+j omega t)). Z_s: 0 (PEC); (1+j)/(sigma delta) (SIBC, half-space); for
conductorModel "volume" a slab of thickness tCond on PEC,
Z_s = eta_c tanh(gamma_c t), eta_c = sqrt(j omega mu0 / (sigma + j omega eps0)),
gamma_c = sqrt(j omega mu0 (sigma + j omega eps0)). The model is exact up to
(gamma/gamma_c)^2 and the fringing-free TEM assumption, which the PMC sides make exact.

  python3 freefem/pcb/check_pp_line.py                       # all portFull sets with results
  python3 freefem/pcb/check_pp_line.py --sets P05-pp_vol_h1,P05-pp_sibc_h1
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARAMS_JSON = ROOT / "freefem" / "pcb" / "pcb_case_parameters.json"
MU0 = 1.25663706212e-6
EPS0 = 8.8541878128e-12
DEFAULT_SIGMA = 5.8e7


def surface_impedance(p: dict, omega: float) -> complex:
    model = p.get("conductorModel", "pec")
    if model == "pec":
        return 0j
    sigma = float(p.get("sigmaCond", DEFAULT_SIGMA))
    if model == "sibc":
        return (1 + 1j) * math.sqrt(omega * MU0 / (2 * sigma))
    sc = sigma + 1j * omega * EPS0
    eta, gam = cmath.sqrt(1j * omega * MU0 / sc), cmath.sqrt(1j * omega * MU0 * sc)
    return eta * cmath.tanh(gam * float(p["tCond"]) * 1e-3)


def line_zin(p: dict, f_ghz: float) -> tuple:
    """(Z_in, Z_s) [Ohm] of the open-ended line of parameter set p at f_ghz."""
    omega = 2 * math.pi * f_ghz * 1e9
    w, length, d = (float(p[k]) * 1e-3 for k in ("planeX", "planeY", "gap"))
    zs = surface_impedance(p, omega)
    eps = float(p["epsSub"]) * (1 - 1j * float(p.get("tanDelta", 0.0)))
    zl = 1j * omega * MU0 * d / w + 2 * zs / w
    yl = 1j * omega * EPS0 * eps * w / d
    gam, z0 = cmath.sqrt(zl * yl), cmath.sqrt(zl / yl)
    return z0 / cmath.tanh(gam * length), zs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark")
    ap.add_argument("--sets", default="", help="comma-separated P05 sets (default: all with portFull = 1)")
    ap.add_argument("--combo", default="mumps_direct")
    args = ap.parse_args()

    pdef = json.loads(PARAMS_JSON.read_text(encoding="utf-8"))["P05"]
    R = float(pdef["ports"][0].get("R", 50.0))
    sets = [s for s in args.sets.split(",") if s] or \
        [k for k, v in pdef["parameter_sets"].items() if v.get("portFull")]
    print(f"{'set':<20} {'model':<6} {'f GHz':>5} {'Z11 FEM [Ohm]':>22} {'Z11 line model':>22} "
          f"{'|dZ|/|Z|':>9} {'|dS11|':>9}  Re Z11 FEM/model")
    for s in sets:
        p = pdef["parameter_sets"][s]
        fp = args.out / "runs" / f"P05_{s}__{args.combo}.json"
        if not fp.exists():
            print(f"{s:<20} no result {fp.name}")
            continue
        r = json.loads(fp.read_text(encoding="utf-8"))
        s11 = complex(*r["pcb"]["ports"]["S"]["S11"])
        f = float(r["pcb"]["freq_GHz"])
        z = R * (1 + s11) / (1 - s11)
        zm, _ = line_zin(p, f)
        sm = (zm - R) / (zm + R)
        print(f"{s:<20} {p.get('conductorModel', 'pec'):<6} {f:5.2f} {z.real:10.4f}{z.imag:+11.4f}j "
              f"{zm.real:10.4f}{zm.imag:+11.4f}j {abs(z - zm) / abs(zm):9.2e} {abs(s11 - sm):9.2e}  "
              f"{z.real / zm.real:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
