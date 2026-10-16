#!/usr/bin/env python3
"""P06 slot check (pcb_problem_benchmark_settings.md 5.10; handoff task J-3).

Reads the frequency sweeps of the P06 parameter sets (run_pcb_benchmark.py run
--freq ..., results P06_<set>@f<GHz>__mumps_direct.json, plus the sets' own
results) and compares the dip of |S21| with the half-wave resonance of the slot,

    f_slot ~ c / (2 L_eff sqrt(eps_slot)),   eps_slot = (eps_r + 1) / 2,

where L_eff is the slot length, or with ideal stitching at x = -d, +d the
length 2 d - stitchW of the aperture piece under the trace (the outer pieces
are not crossed by the trace).

Per set: the sweep table (|S11|, |S21| in dB, the insertion loss against the
set without slot at the same frequency, and the power not leaving through the
ports, 1 - |S11|^2 - |S21|^2: radiation and dielectric loss), then the deepest
dip of the |S21| ratio to the no-slot set (local minimum on the grid, refined
by a parabola through the three points) against f_slot.

A set passes when its estimate lies inside the sweep and a dip of at least
--min-dip dB is found within --tol (relative) of it; sets whose estimate is
above the sweep are reported only. When the ratio is still falling at the
upper end of the sweep (the resonance is at or above it), the end frequency
is a lower bound and must not exceed the estimate by more than --tol.
Exit status 1 if a set fails.

  python3 freefem/pcb/check_p06_slot.py                       # results/pcb_benchmark
  python3 freefem/pcb/check_p06_slot.py --table               # also the sweep tables
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C0_MM_GHZ = 299.792458
PROBLEM = "P06"
REFERENCE = "P06-L0"   # the set without slot


def db(x: float) -> float:
    return 20 * math.log10(max(x, 1e-300))


def load_sweep(runs: Path, pset: str, combo: str) -> dict:
    """{f [GHz]: (S11, S21)} of a set: its own result and its @f results."""
    out = {}
    files = [runs / f"{PROBLEM}_{pset}__{combo}.json"] + sorted(runs.glob(f"{PROBLEM}_{pset}@f*__{combo}.json"))
    for fp in files:
        if not fp.exists():
            continue
        r = json.loads(fp.read_text(encoding="utf-8"))
        if r.get("param_set", "").split("@")[0] != pset:
            continue
        s = ((r.get("pcb") or {}).get("ports") or {}).get("S") or {}
        if "S21" not in s or "S11" not in s:
            continue
        out.setdefault(round(float(r["pcb"]["freq_GHz"]), 6), (complex(*s["S11"]), complex(*s["S21"])))
    return dict(sorted(out.items()))


def slot_estimate(p: dict) -> tuple:
    """(effective slot length [mm], f_slot [GHz]) or (0, None) without slot."""
    if p["slotL"] <= 0:
        return 0.0, None
    leff = p["slotL"] if p["stitchD"] <= 0 else 2 * p["stitchD"] - p["stitchW"]
    eps_slot = (p["epsSub"] + 1) / 2
    return leff, C0_MM_GHZ / (2 * leff * math.sqrt(eps_slot))


def deepest_dip(freqs: list, vals: list) -> tuple | None:
    """(f, value) of the lowest interior local minimum, refined by a parabola."""
    best = None
    for k in range(1, len(freqs) - 1):
        if vals[k] < vals[k - 1] and vals[k] <= vals[k + 1]:
            f0, f1, f2 = freqs[k - 1:k + 2]
            y0, y1, y2 = vals[k - 1:k + 2]
            den = (f0 - f1) * (f0 - f2) * (f1 - f2)
            a = (f2 * (y1 - y0) + f1 * (y0 - y2) + f0 * (y2 - y1)) / den
            b = (f2 * f2 * (y0 - y1) + f1 * f1 * (y2 - y0) + f0 * f0 * (y1 - y2)) / den
            fm, ym = f1, y1
            if a > 0:
                fm = -b / (2 * a)
                ym = y1 - a * (f1 - fm) ** 2 if f0 < fm < f2 else y1
                fm = fm if f0 < fm < f2 else f1
            if best is None or ym < best[1]:
                best = (fm, ym)
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark")
    ap.add_argument("--combo", default="mumps_direct", help="preset_krylov part of the result names")
    ap.add_argument("--tol", type=float, default=0.25, help="relative tolerance of the dip frequency")
    ap.add_argument("--min-dip", type=float, default=1.0, help="least depth [dB] of the dip against the no-slot set")
    ap.add_argument("--table", action="store_true", help="print the sweep table of every set")
    args = ap.parse_args()
    sets = json.loads((ROOT / "freefem" / "pcb" / "pcb_case_parameters.json").read_text(encoding="utf-8"))[
        PROBLEM]["parameter_sets"]
    runs = args.out / "runs"
    sweeps = {name: load_sweep(runs, name, args.combo) for name in sets}
    ref = sweeps.get(REFERENCE) or {}
    if not any(sweeps.values()):
        print(f"no {PROBLEM} results for {args.combo} in {runs}")
        return 1
    ok = True
    for name, p in sets.items():
        sw = sweeps[name]
        if not sw:
            print(f"== {name}: no results")
            continue
        leff, f_est = slot_estimate(p)
        freqs = list(sw)
        print(f"== {name}  slotL={p['slotL']:g} stitchD={p['stitchD']:g}  {len(freqs)} frequencies "
              f"{freqs[0]:g}-{freqs[-1]:g} GHz"
              + (f"  L_eff={leff:g} mm, f_slot ~ {f_est:.2f} GHz" if f_est else "  (no slot)"))
        if args.table:
            print("      f [GHz]  |S11| [dB]  |S21| [dB]  vs no slot [dB]  1-|S11|^2-|S21|^2")
            for f in freqs:
                s11, s21 = sw[f]
                rel = f"{db(abs(s21)) - db(abs(ref[f][1])):+8.2f}" if f in ref else "       -"
                print(f"   {f:10.4g}  {db(abs(s11)):10.2f}  {db(abs(s21)):10.2f}  {rel:>15s}  "
                      f"{1 - abs(s11) ** 2 - abs(s21) ** 2:17.3f}")
        if name == REFERENCE or f_est is None:
            worst = min(freqs, key=lambda f: abs(sw[f][1]))
            print(f"   min |S21| {db(abs(sw[worst][1])):.2f} dB at {worst:g} GHz")
            continue
        common = [f for f in freqs if f in ref]
        if len(common) < 3:
            print(f"   fewer than 3 frequencies in common with {REFERENCE}: no dip search")
            continue
        ratio = [db(abs(sw[f][1])) - db(abs(ref[f][1])) for f in common]
        dip = deepest_dip(common, ratio)
        in_sweep = common[0] < f_est < common[-1]
        k = min(range(len(common)), key=lambda i: ratio[i])
        if k == len(common) - 1 and ratio[k] <= -args.min_dip and (dip is None or dip[1] > ratio[k]):
            # still falling at the upper end of the sweep: the resonance is at or above it
            dev = common[k] / f_est - 1
            good = dev <= args.tol
            ok &= good or not in_sweep
            print(f"   |S21| ratio still falling at the end of the sweep ({ratio[k]:+.2f} dB at {common[k]:g} GHz): "
                  f"resonance >= {common[k]:g} GHz (f_slot ~ {f_est:.2f} GHz, >= {100 * dev:+.1f} %)  "
                  + (f"{'OK' if good else 'FAIL'} (tol {100 * args.tol:.0f} %)" if in_sweep
                     else "(f_slot outside the sweep: not checked)"))
            continue
        if dip is None or dip[1] > -args.min_dip:
            msg = f"   no dip of {args.min_dip:g} dB (lowest {ratio[k]:+.2f} dB at {common[k]:g} GHz)"
            if in_sweep:
                ok = False
                msg += "  FAIL"
            else:
                msg += f"  (f_slot outside the sweep: not checked)"
            print(msg)
            continue
        dev = dip[0] / f_est - 1
        line = f"   dip {dip[1]:+.2f} dB at {dip[0]:.2f} GHz (f_slot ~ {f_est:.2f} GHz, {100 * dev:+.1f} %)"
        if in_sweep:
            good = abs(dev) <= args.tol
            ok &= good
            line += f"  {'OK' if good else 'FAIL'} (tol {100 * args.tol:.0f} %)"
        else:
            line += "  (f_slot outside the sweep: not checked)"
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
