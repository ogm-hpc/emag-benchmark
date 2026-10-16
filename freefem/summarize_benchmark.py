#!/usr/bin/env python3
"""Aggregate a run_benchmark.py campaign into results/benchmark/summary.{json,csv}.

Joins, per case/param-set: the problem definition (case_parameters.json), mesh
metrics (results/mesh_quality.json), the resonance-proximity check
(results/resonance/resonance.json) and the 11 solver runs (runs/*.json:
status, iterations, relative true residual reached, wall time incl. setup,
setup time, peak memory, and a thinned residual history).

  python3 freefem/summarize_benchmark.py [--dir results/benchmark]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import run_freefem_batch as rfb
from run_benchmark import DEFAULT_COMBOS


def thin(history: list, n: int = 80) -> list:
    """Keep ~n points, log-spaced in iteration index, always first and last."""
    if len(history) <= n:
        return history
    idx = sorted({0, len(history) - 1} | {int(round(math.expm1(i / (n - 1) * math.log1p(len(history) - 1))))
                                            for i in range(n)})
    return [history[i] for i in idx if i < len(history)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=rfb.ROOT / "results" / "benchmark")
    args = ap.parse_args()
    db = rfb.load_case_params()
    mq = json.loads((rfb.ROOT / "results" / "mesh_quality.json").read_text())
    rp = rfb.ROOT / "results" / "resonance" / "resonance.json"
    res = json.loads(rp.read_text()) if rp.exists() else {}

    runs = {}
    for p in sorted((args.dir / "runs").glob("*.json")):
        r = json.loads(p.read_text())
        runs[(f"{r['case']}:{r['param_set']}", f"{r['preset']}/{r['krylov']}")] = r

    sets = []
    for case, cdef in db.items():
        for ps, pdef in cdef["parameter_sets"].items():
            key = f"{case}:{ps}"
            m = mq.get(key, {})
            near = (res.get(key) or {}).get("nearest")
            entry = dict(key=key, case=case, param_set=ps, case_description=cdef["description"],
                         description=pdef.get("description", ""),
                         params={k: v for k, v in pdef.items() if k != "description"},
                         k0=rfb.pick_k0(case, pdef), dof=m.get("dof"), ppw_min=m.get("ppw_min"),
                         worst_region=m.get("worst_region"),
                         nearest_mode=near, runs={})
            for combo in DEFAULT_COMBOS:
                r = runs.get((key, combo))
                if not r:
                    continue
                entry["runs"][combo] = dict(
                    status=r["status"], reason=r["reason"], iterations=r["iterations"],
                    final_relres=r["final_relres"], min_relres=r["min_relres"], wall=r["wall"],
                    setup_time=r["setup_time"], peak_rss_gb=r["peak_rss_gb"],
                    history=thin([(i, v, t) for i, v, t in r["history"]]))
            sets.append(entry)

    out = dict(budget=600, rtol=1e-8, combos=DEFAULT_COMBOS, sets=sets)
    (args.dir / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    with (args.dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "param_set", "dof", "ppw_min", "nearest_mode_reldist", "combo", "status",
                    "iterations", "final_relres", "wall_s", "setup_s", "peak_rss_gb"])
        for s in sets:
            nd = s["nearest_mode"]["reldist"] if s["nearest_mode"] else ""
            for combo, r in s["runs"].items():
                w.writerow([s["case"], s["param_set"], s["dof"], f"{s['ppw_min']:.2f}" if s["ppw_min"] else "",
                            nd, combo, r["status"], r["iterations"], r["final_relres"], r["wall"],
                            r["setup_time"], r["peak_rss_gb"]])
    n = sum(len(s["runs"]) for s in sets)
    print(f"{len(sets)} sets, {n} runs -> {args.dir/'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
