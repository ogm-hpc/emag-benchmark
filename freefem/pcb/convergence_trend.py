#!/usr/bin/env python3
"""Convergence-trend indicators of a residual history (docs/paper_plan.md 4.2-4.4).

Supplementary information for runs stopped at the iteration cap: they are
never used as a stopping rule.

  envelope   r_hat_k = min_{j<=k} r_j (monotone; GMRES residuals already are)
  slope s    least-squares slope of log10 r_hat over the last window W
             (decades per iteration; rho = 10**s is the mean convergence factor)
  N_est      k + (log10(tol) - log10 r_hat_k) / s   (inf if s >= 0)
  rho_cyc    r_end / r_start of the last restart cycles (GMRES(m))
  last_update  last iteration at which r_hat decreased; drop_window = r_hat
             at the end / r_hat at the start of the window

The window of the v1.0 records (decided 2026-10-05, paper_plan 1): GMRES
w = 0.2, COCG w = 0.5 of the iterations (TREND_WINDOW); supplement() gives
the indicators of a result JSON as summarize_pcb_benchmark.py reports them.
N_est of cslp_hx is pessimistic (superlinear convergence, paper_plan 4.3-4.4).

Subcommands
  backtest   truncate converged histories at fractions of their length and
             compare N_est with the actual iteration count (per combination);
             also the indicators of the capped (timeout) runs and the time per
             iteration
  show       indicators of the given result JSON files

The input are result JSONs of run_benchmark.run_job (history = [[it, relres,
time], ...], subsampled to <= ~1500 points). Python standard library only.

  python3 freefem/pcb/convergence_trend.py backtest
  python3 freefem/pcb/convergence_trend.py show results/pcb_benchmark/runs/P03_P03-1__ssor_gmres.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOL = 1.0e-8
RESTART = 300
TREND_WINDOW = {"gmres": 0.2, "cocg": 0.5}   # window fraction w per Krylov method (paper_plan 1)
PESSIMISTIC_N_EST = ("cslp_hx/gmres",)       # backtest: N_est 2.7-4x the actual count (4.4)


def envelope(hist):
    out, m = [], math.inf
    for it, r, *_ in hist:
        m = min(m, r)
        out.append((it, m))
    return out


def slope(env, k_lo, k_hi):
    """Least-squares slope of log10 r_hat over iterations k_lo..k_hi."""
    pts = [(it, math.log10(r)) for it, r in env if k_lo <= it <= k_hi and r > 0]
    if len(pts) < 3 or pts[-1][0] == pts[0][0]:
        return None
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx if sxx > 0 else None


def window(k, krylov, frac, restart=RESTART):
    """Window length: a fraction of k; for GMRES whole restart cycles (>= 1)."""
    w = max(frac * k, 1.0)
    if krylov == "gmres":
        w = max(restart, restart * round(w / restart))
    return min(w, k)


def indicators(hist, krylov, k=None, frac=0.2, restart=RESTART, tol=TOL):
    """Indicators of the history truncated at iteration k (default: all)."""
    if k is not None:
        hist = [h for h in hist if h[0] <= k]
    if len(hist) < 3:
        return None
    env = envelope(hist)
    k = env[-1][0]
    r = env[-1][1]
    w = window(k, krylov, frac, restart)
    s = slope(env, k - w, k)
    if s is None:
        return None
    n_est = math.inf if s >= 0 else k + (math.log10(tol) - math.log10(r)) / s
    last = next((env[i][0] for i in range(len(env) - 1, 0, -1) if env[i][1] < env[i - 1][1]), env[0][0])
    out = dict(k=k, r_hat=r, window=w, s=s, rho=10 ** s, n_est=n_est,
               drop_window=r / next(e[1] for e in env if e[0] >= k - w), last_update=last)
    if krylov == "gmres":
        # reduction over the last (up to) three whole cycles, per cycle
        c_end = (k // restart) * restart
        c_start = max(0, c_end - 3 * restart)
        if c_end > c_start:
            r0 = next((e[1] for e in env if e[0] >= c_start), None)
            r1 = next((e[1] for e in reversed(env) if e[0] <= c_end), None)
            if r0 and r1:
                out["rho_cyc"] = (r1 / r0) ** (restart / (c_end - c_start))
    return out


def supplement(d: dict) -> dict | None:
    """Indicators of a result JSON (run_benchmark.run_job format) with the v1.0
    window of its Krylov method and its restart length; None if the history is
    too short. Adds the time per iteration and the estimated time to converge
    (set-up + N_est x time per iteration)."""
    kr = d["krylov"]
    restart = (d.get("pcb") or {}).get("gmres_restart") or RESTART
    ind = indicators(d.get("history") or [], kr, frac=TREND_WINDOW.get(kr, 0.2), restart=restart)
    if ind is None:
        return None
    tpi = time_per_it(d)
    ind["time_per_it"] = tpi
    ind["t_est"] = ((d.get("setup_time") or 0.0) + ind["n_est"] * tpi
                    if tpi and math.isfinite(ind["n_est"]) else math.inf)
    ind["pessimistic"] = f"{d['preset']}/{kr}" in PESSIMISTIC_N_EST
    return ind


def time_per_it(d):
    h = d.get("history") or []
    it = d.get("iterations") or 0
    if it <= 0 or not h:
        return None
    return (h[-1][2] - d.get("setup_time", 0.0)) / max(h[-1][0], 1)


def load_runs():
    """Standard results: PCB (pcb_summary.csv, no variant, not P02-b_h0.05) and existing."""
    runs = []
    pcb_dir = ROOT / "results/pcb_benchmark/runs"
    with open(ROOT / "docs/pcb_results/pcb_summary.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["variant"] or row["preset"] == "mumps" or row["paramSet"] == "P02-b_h0.05":
                continue
            p = pcb_dir / row["file"]
            if p.exists():
                runs.append(("pcb", p))
    for p in sorted((ROOT / "results/benchmark/runs").glob("*.json")):
        runs.append(("existing", p))
    return runs


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * (len(xs) - 1) + 0.5))]


def cmd_backtest(a):
    runs = load_runs()
    by = defaultdict(list)       # combo -> backtest ratios per (frac_trunc, frac_win)
    capped = defaultdict(list)
    tpi = defaultdict(list)
    n_conv = defaultdict(int)
    for src, p in runs:
        d = json.loads(p.read_text())
        kr, pre = d["krylov"], d["preset"]
        combo = f"{pre}/{kr}"
        restart = (d.get("pcb") or {}).get("gmres_restart") or RESTART
        hist = d.get("history") or []
        t = time_per_it(d)
        if t:
            tpi[combo].append((t, d.get("ndof", 0)))
        if d["status"] == "converged":
            n_conv[combo] += 1
            it = d["iterations"]
            if it < a.min_its:
                continue
            for ft in a.trunc:
                for fw in a.win:
                    ind = indicators(hist, kr, k=int(ft * it), frac=fw, restart=restart)
                    if ind and math.isfinite(ind["n_est"]):
                        by[(combo, ft, fw)].append(ind["n_est"] / it)
                    elif ind:
                        by[(combo, ft, fw)].append(math.inf)
        else:
            for fw in a.win:
                ind = indicators(hist, kr, frac=fw, restart=restart)
                if ind:
                    capped[(combo, fw)].append(ind)

    combos = sorted({k[0] for k in by} | {k[0] for k in capped})
    print("# Backtest of N_est on converged runs (ratio N_est / actual iterations)")
    print(f"# runs with >= {a.min_its} iterations; truncated at fraction t of the actual count; window fraction w")
    print("| combo | t | w | n | median | p10 | p90 | optimistic (<0.8) | inf |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in combos:
        for ft in a.trunc:
            for fw in a.win:
                xs = by.get((c, ft, fw))
                if not xs:
                    continue
                fin = [x for x in xs if math.isfinite(x)]
                if not fin:
                    print(f"| {c} | {ft} | {fw} | {len(xs)} | inf | | | | {len(xs)} |")
                    continue
                print(f"| {c} | {ft} | {fw} | {len(xs)} | {statistics.median(fin):.2f} | {q(fin, .1):.2f} | "
                      f"{q(fin, .9):.2f} | {sum(x < 0.8 for x in fin)} | {len(xs) - len(fin)} |")
    print()
    print("# Indicators of the capped (600 s timeout) runs")
    print("| combo | w | n | s~0 (drop<2 in window) | N_est median | N_est p10 | stagnant rho_cyc>0.9 |")
    print("|---|---|---|---|---|---|---|")
    for c in combos:
        for fw in a.win:
            xs = capped.get((c, fw))
            if not xs:
                continue
            flat = sum(1 for x in xs if x["drop_window"] > 0.5)
            ne = [x["n_est"] for x in xs]
            fin = [x for x in ne if math.isfinite(x)]
            med = statistics.median(ne) if ne else math.nan
            stag = sum(1 for x in xs if x.get("rho_cyc", 0) > 0.9)
            print(f"| {c} | {fw} | {len(xs)} | {flat} | {med:.3g} | {q(fin, .1) if fin else math.inf:.3g} | {stag} |")
    print()
    print("# Time per iteration (records, mostly 5-parallel), s")
    print("| combo | n | median | max | max at ndof |")
    print("|---|---|---|---|---|")
    for c in sorted(tpi):
        xs = tpi[c]
        mx = max(xs)
        print(f"| {c} | {len(xs)} | {statistics.median(x[0] for x in xs):.3g} | {mx[0]:.3g} | {mx[1]} |")
    return 0


def cmd_show(a):
    for f in a.files:
        d = json.loads(Path(f).read_text())
        restart = (d.get("pcb") or {}).get("gmres_restart") or RESTART
        ind = indicators(d.get("history") or [], d["krylov"], frac=a.win[0], restart=restart)
        tpi = time_per_it(d)
        print(Path(f).name, d["status"], d.get("iterations"), f"s_per_it={tpi:.4g}" if tpi else "",
              f"setup={d.get('setup_time')}", json.dumps(ind))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--trunc", type=float, nargs="+", default=[0.25, 0.5, 0.75])
    b.add_argument("--win", type=float, nargs="+", default=[0.1, 0.2, 0.5])
    b.add_argument("--min-its", type=int, default=200)
    b.set_defaults(func=cmd_backtest)
    s = sub.add_parser("show")
    s.add_argument("files", nargs="+")
    s.add_argument("--win", type=float, nargs="+", default=[0.2])
    s.set_defaults(func=cmd_show)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
