#!/usr/bin/env python3
"""P05 resonance check (pcb_problem_benchmark_settings.md 5.9, 14 Phase 1 step 3).

Compares the peaks of the input impedance |Z11| of a P05 frequency sweep
(run_pcb_benchmark.py run --freq ..., usually --combos mumps/direct) with the
cavity modes of the plane pair with PMC edges,

    f_mn = c / (2 sqrt(eps_r)) * sqrt((m/a)^2 + (n/b)^2),

a = planeX, b = planeY. Z11 follows from S11 (reference R of the port,
S11 = (Z11 - R)/(Z11 + R)): Z11 = R (1 + S11)/(1 - S11).

Resonances of the sweep (time convention exp(+j omega t), as the solver):
  grid peak   local maximum of |Z11| on the sweep grid (+- half a step)
  refined     zero crossing of Im(Y11), Y11 = 1/Z11, from - to + (parallel
              resonance), linearly interpolated between the two grid points.
              Near an isolated mode Y11 is smooth (the pole of Z11 is a zero
              of Y11), so this is much finer than the grid even for Q ~ 1/tan(delta).
The coupling of mode (m, n) to the feed (x0, y0) is cos(m pi x0/a) cos(n pi y0/b)
(0: the feed is on a nodal line, the mode is not excited). Neighbouring sweep
points more than 1.5 x the smallest step apart are not interpolated (a sweep
made of separate windows).

Losses (--q): the quality factor of each resonance from the parallel-resonance
form of Y11, Q = (f_r/2) (d Im Y11/df) / Re Y11 at the zero crossing, against
the plane pair with dielectric loss tan(delta) and, for conductorModel "sibc"
or "volume" (planes as metal slabs much thicker than delta),
surface resistance R_s = omega mu0 delta/2 on both planes. With x = delta/d
(d = gap), the transmission-line model of the pair gives
    f_r = f_mn / sqrt(1 + x),    1/Q = x/(1 + x) + tan(delta),
i.e. Q_c ~ d/delta and a shift of about -f delta/(2d) (surface reactance).
The sweep step must be well below the bandwidth f_r/Q (1 MHz steps for Q ~ 140;
the 5 MHz sweep of the PEC case, Q = 1000, gives Q only to ~15 %).

  python3 freefem/pcb/run_pcb_benchmark.py run --sets P05-2 --combos mumps/direct \\
      --freq $(python3 -c "print(','.join(f'{0.70 + 0.005 * i:.3f}' for i in range(31)))")
  python3 freefem/pcb/check_p05_resonance.py                     # P05-2, results/pcb_benchmark
  python3 freefem/pcb/check_p05_resonance.py --set P05-2 --out results/pcb_benchmark --combo mumps_direct
  python3 freefem/pcb/check_p05_resonance.py --set P05-2_sibc --q     # SIBC: Q and shift
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C0_MM_GHZ = 299.792458
MU0 = 1.25663706212e-6
DEFAULT_SIGMA = 5.8e7
PARAMS_JSON = ROOT / "freefem" / "pcb" / "pcb_case_parameters.json"


def cavity_modes(a: float, b: float, eps_r: float, f_max: float) -> list:
    """[(f_mn [GHz], m, n)] of the PMC-edged cavity up to f_max, without (0, 0)."""
    out = []
    c = C0_MM_GHZ / (2.0 * math.sqrt(eps_r))
    for m in range(int(a * f_max / c) + 1):
        for n in range(int(b * f_max / c) + 1):
            if m == n == 0:
                continue
            f = c * math.hypot(m / a, n / b)
            if f <= f_max:
                out.append((f, m, n))
    return sorted(out)


def load_sweep(runs: Path, pset: str, combo: str) -> list:
    """[(f [GHz], S11 complex, file name)] of <set>@f<GHz> results (and the
    parameter set's own result, if any), sorted by frequency."""
    pat = re.compile(rf"^P05_{re.escape(pset)}(@f[0-9.eE+-]+)?__{re.escape(combo)}\.json$")
    pts = {}
    for fp in sorted(runs.glob(f"P05_{pset}*__{combo}.json")):
        if not pat.match(fp.name):
            continue   # other ports, E1, tagged variants
        r = json.loads(fp.read_text(encoding="utf-8"))
        s = ((r.get("pcb") or {}).get("ports") or {}).get("S", {}).get("S11")
        if s is None:
            print(f"  {fp.name}: no S11 (status {r.get('status')}), skipped")
            continue
        f = float(r["pcb"]["freq_GHz"])
        if f in pts:
            print(f"  {fp.name}: frequency {f} GHz already read from {pts[f][2]}, skipped")
            continue
        pts[f] = (f, complex(*s), fp.name)
    return [pts[f] for f in sorted(pts)]


def grid_peaks(freqs: list, zabs: list) -> list:
    """Indices of interior local maxima of |Z11|."""
    return [i for i in range(1, len(zabs) - 1) if zabs[i] > zabs[i - 1] and zabs[i] >= zabs[i + 1]]


def admittance_zeros(freqs: list, y: list) -> list:
    """[(f_r, Q)] where Im(Y11) crosses zero from - to + (linear interpolation
    between neighbouring points, not across gaps of the sweep). Q from the
    slope of Im Y11 and Re Y11 interpolated at f_r."""
    out = []
    steps = [freqs[i + 1] - freqs[i] for i in range(len(freqs) - 1)]
    dmin = min(steps)
    for i in range(len(y) - 1):
        if steps[i] > 1.5 * dmin:
            continue
        b0, b1 = y[i].imag, y[i + 1].imag
        if b0 < 0.0 <= b1:
            t = -b0 / (b1 - b0)
            fr = freqs[i] + t * steps[i]
            g = y[i].real + t * (y[i + 1].real - y[i].real)
            q = fr / 2 * (b1 - b0) / steps[i] / g if g > 0 else math.inf
            out.append((fr, q))
    return out


def skin_depth_mm(f_ghz: float, sigma: float) -> float:
    return 1e3 / math.sqrt(math.pi * f_ghz * 1e9 * MU0 * sigma)


def expected_resonance(f_mn: float, gap: float, tan_d: float, sigma: float | None) -> tuple:
    """(f_r, Q) of mode f_mn with dielectric loss and, if sigma, SIBC planes."""
    if not sigma:
        return f_mn, (1 / tan_d if tan_d > 0 else math.inf)
    fr = f_mn
    for _ in range(3):   # delta at f_r (weak dependence)
        x = skin_depth_mm(fr, sigma) / gap
        fr = f_mn / math.sqrt(1 + x)
    return fr, 1 / (x / (1 + x) + tan_d)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "pcb_benchmark")
    ap.add_argument("--set", default="P05-2", help="P05 parameter set of the sweep (default P05-2)")
    ap.add_argument("--combo", default="mumps_direct", help="preset_krylov part of the result names")
    ap.add_argument("--tol", type=float, default=0.01,
                    help="relative deviation from f_mn reported as a mismatch (default 0.01)")
    ap.add_argument("--q", action="store_true",
                    help="also compare Q and (SIBC) the frequency shift with the loss model")
    ap.add_argument("--q-tol", type=float, default=0.10,
                    help="relative deviation of Q reported as a mismatch (default 0.10)")
    ap.add_argument("--shift-tol", type=float, default=0.30,
                    help="SIBC: deviation of f_r from the model, relative to the predicted shift (default 0.30)")
    args = ap.parse_args()

    pdef = json.loads(PARAMS_JSON.read_text(encoding="utf-8"))["P05"]
    if args.set not in pdef["parameter_sets"]:
        print(f"unknown P05 parameter set {args.set}")
        return 2
    p = pdef["parameter_sets"][args.set]
    a, b, eps_r = float(p["planeX"]), float(p["planeY"]), float(p["epsSub"])
    x0, y0 = float(p["feedX"]), float(p["feedY"])
    R = float(pdef["ports"][0].get("R", 50.0))
    gap, tan_d = float(p["gap"]), float(p.get("tanDelta", 0.0))
    model = p.get("conductorModel", "pec")
    sigma = float(p.get("sigmaCond", DEFAULT_SIGMA)) if model in ("sibc", "volume") else None

    sweep = load_sweep(args.out / "runs", args.set, args.combo)
    if len(sweep) < 3:
        print(f"{len(sweep)} sweep points of {args.set} ({args.combo}) in {args.out / 'runs'}; need >= 3")
        return 1
    freqs = [f for f, _, _ in sweep]
    z = [R * (1 + s) / (1 - s) for _, s, _ in sweep]
    y = [1 / v for v in z]
    zabs = [abs(v) for v in z]
    steps = sorted({round(freqs[i + 1] - freqs[i], 9) for i in range(len(freqs) - 1)})

    print(f"== {args.set}: a = {a} mm, b = {b} mm, gap = {gap} mm, eps_r = {eps_r}, tan_delta = {tan_d}, "
          f"conductors {'%s sigma = %g S/m' % (model, sigma) if sigma else 'PEC'}, feed ({x0}, {y0}) mm, "
          f"R = {R} Ohm")
    print(f"   sweep {freqs[0]:.4f}-{freqs[-1]:.4f} GHz, {len(freqs)} points, "
          f"step {', '.join(f'{1e3 * s:g}' for s in steps)} MHz")
    print("   f [GHz]    |S11|     |Z11| [Ohm]  arg Z11 [deg]  Im Y11 [S]")
    for (f, s, _), v, w in zip(sweep, z, y):
        print(f"   {f:8.4f}  {abs(s):.5f}  {abs(v):12.4g}  {math.degrees(cmath.phase(v)):9.2f}  {w.imag:11.3e}")

    modes = cavity_modes(a, b, eps_r, freqs[-1] * 1.5)
    in_range = [(f, m, n) for f, m, n in modes if freqs[0] <= f <= freqs[-1]]
    print("   cavity modes in the sweep range (PMC edges):")
    for f, m, n in in_range:
        cpl = math.cos(m * math.pi * x0 / a) * math.cos(n * math.pi * y0 / b)
        print(f"     ({m},{n})  f_mn = {f:.4f} GHz  coupling to the feed {cpl:+.3f}")
    if not in_range:
        print("     none")

    peaks = [freqs[i] for i in grid_peaks(freqs, zabs)]
    zeros = admittance_zeros(freqs, y)
    print("   resonances of the sweep:")
    n_bad = 0
    for fr, q in zeros:
        near = min(modes, key=lambda t: abs(t[0] - fr))
        gp = min(peaks, key=lambda g: abs(g - fr)) if peaks else None
        dev = (fr - near[0]) / near[0]
        flag = "" if abs(dev) <= args.tol else "  MISMATCH"
        n_bad += abs(dev) > args.tol
        gp_txt = f"grid peak {gp:.4f} GHz" if gp is not None else "no grid peak"
        print(f"     refined {fr:.4f} GHz ({gp_txt}) -> ({near[1]},{near[2]}) {near[0]:.4f} GHz: "
              f"{1e3 * (fr - near[0]):+.1f} MHz ({100 * dev:+.2f} %){flag}")
        if args.q:
            f_pred, q_pred = expected_resonance(near[0], gap, tan_d, sigma)
            q_dev = (q - q_pred) / q_pred if math.isfinite(q_pred) else math.nan
            bad_q = not (abs(q_dev) <= args.q_tol)
            line = (f"       Q = {q:.1f}, model {q_pred:.1f} ({100 * q_dev:+.1f} %)"
                    f"{'  MISMATCH' if bad_q else ''}")
            n_bad += bad_q
            if sigma:
                shift = f_pred - near[0]
                bad_f = abs(fr - f_pred) > args.shift_tol * abs(shift)
                n_bad += bad_f
                line += (f"; f_r = {fr:.5f} GHz, model {f_pred:.5f} GHz (shift {1e3 * shift:+.2f} MHz, "
                         f"FEM {1e3 * (fr - near[0]):+.2f} MHz){'  MISMATCH' if bad_f else ''}")
            print(line)
    if not zeros:
        print("     none (no - to + zero crossing of Im Y11)")
    unmatched = [(f, m, n) for f, m, n in in_range
                 if not any(abs(fr - f) <= args.tol * f for fr, _ in zeros)
                 and abs(math.cos(m * math.pi * x0 / a) * math.cos(n * math.pi * y0 / b)) > 0.05]
    for f, m, n in unmatched:
        print(f"     ({m},{n}) {f:.4f} GHz: no resonance of the sweep within {100 * args.tol:g} %")
    n_bad += len(unmatched)
    print(f"   {'OK' if n_bad == 0 else f'{n_bad} mismatches'} (tolerance {100 * args.tol:g} %)")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
