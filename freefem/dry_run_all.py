#!/usr/bin/env python3
"""Dry-run-all: sanity-check + timing probe for every (case, parameter set) x
(preconditioner preset, Krylov method) combination in this project's
performance-evaluation scope, before committing to full-length runs.

Per the project's standing scope (problem_settings.md):
  - Krylov methods: GMRES and COCG only.
  - Preconditioner presets in scope: gs, ssor, amg_gamg, accel_ic, cslp, hx,
    cslp_hx (jacobi/ic0/ic0_shift/ilu are excluded; amg_gamg is kept despite
    known weakness).
  - cslp/hx/cslp_hx use a hand-rolled GMRES-only outer loop (--krylov is
    ignored for these), so only "gmres" is run for them -- running "cocg" too
    would just be a byte-identical duplicate.

Every combination is forced to a tiny iteration cap (--max-it, default 10)
so this sweeps the FULL case x parameter-set x preset x krylov space cheaply:
this is a smoke test (does it even run without a PETSC ERROR/crash) AND a
timing probe (wall-clock for a fixed small iteration count, used afterward to
estimate how long a real run would take and to size --outer-max-it/-ksp_max_it
for the follow-up full sweep so it finishes inside a wall-clock budget instead
of being killed mid-flight by --timeout).

Usage:
  python3 freefem/dry_run_all.py --run --workers 6 --max-it 10 --timeout 180 \
      --out results/dry_run_all/dry_run_results.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_freefem_batch as rfb  # noqa: E402

RESULT_ROOT = rfb.ROOT / "results" / "dry_run_all"

# Preconditioner evaluation scope (problem_settings.md, 2026-07-27): jacobi,
# ic0, ic0_shift, ilu are explicitly excluded; amg_gamg is explicitly kept.
PRESETS = ["gs", "ssor", "amg_gamg", "accel_ic", "cslp", "hx", "cslp_hx"]
GMRES_ONLY_PRESETS = {"cslp", "hx", "cslp_hx"}
KRYLOVS = ["gmres", "cocg"]

KSP_LINE_RE = re.compile(r"^\s*(\d+)\s+KSP Residual norm\s+([0-9.eE+\-]+)")
REASON_RE = re.compile(
    r"Linear solve (converged|did not converge) due to (\w+) iterations (\d+)"
)
SOLVE_TIME_RE = re.compile(r"SOLVE_TIME\s*=\s*([0-9.eE+\-]+)")
MAX_IT_RE = re.compile(r"-ksp_max_it\s+\d+")


@dataclass
class DryRunResult:
    case_name: str
    param_set: str
    preset: str
    krylov: str
    ok: bool
    max_it_used: int
    residuals: List[Tuple[int, float]] = field(default_factory=list)
    reason: Optional[str] = None
    iterations: Optional[int] = None
    converged: Optional[bool] = None
    solve_time: Optional[float] = None
    wall_time: Optional[float] = None
    error: Optional[str] = None
    log_path: Optional[str] = None


def parse_log(log_path: Path) -> Dict:
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    residuals = []
    for line in text.splitlines():
        m = KSP_LINE_RE.match(line)
        if m:
            residuals.append((int(m.group(1)), float(m.group(2))))
    reason_m = REASON_RE.search(text)
    converged = None
    reason = None
    iterations = None
    if reason_m:
        converged = reason_m.group(1) == "converged"
        reason = reason_m.group(2)
        iterations = int(reason_m.group(3))
    solve_m = SOLVE_TIME_RE.search(text)
    solve_time = float(solve_m.group(1)) if solve_m else None
    petsc_error = "PETSC ERROR" in text
    return {
        "residuals": residuals,
        "converged": converged,
        "reason": reason,
        "iterations": iterations,
        "solve_time": solve_time,
        "petsc_error": petsc_error,
    }


def run_one(case_name: str, param_set: str, mesh_path: Path, preset: str, krylov: str,
            max_it: int, timeout: int, freefem_bin: str) -> DryRunResult:
    result_dir = RESULT_ROOT / f"{case_name}_{param_set}" / f"{krylov}_{preset}"
    args = argparse.Namespace(
        mesh_dir=rfb.DEFAULT_MESH_DIR,
        cases=case_name,
        abc="auto",
        backend="petsc",
        preset=preset,
        krylov=krylov,
        freefem_bin=freefem_bin,
        run=True,
        save_vtk=False,
        result_dir=result_dir,
        petsc_options=rfb.DEFAULT_PETSC_OPTIONS,
        timeout=timeout,
        accel_ic_alpha=rfb.DEFAULT_ACCEL_IC_ALPHA,
        hx_smoother_omega=rfb.DEFAULT_HX_SMOOTHER_OMEGA,
        outer_max_it=max_it,
    )
    rfb.apply_preset(args)
    # Force every preset's iteration cap down to max_it for this probe, whether
    # it lives in the PETSc options string (native presets) or in
    # args.outer_max_it (hand-rolled presets: cslp/accel_ic/hx/cslp_hx -- already
    # set above, but re-set here too since apply_preset doesn't touch it).
    args.petsc_options = MAX_IT_RE.sub(f"-ksp_max_it {max_it}", args.petsc_options)
    args.outer_max_it = max_it

    case_db = rfb.load_case_params()
    task = rfb.MeshTask(case_name=case_name, param_set=param_set, mesh_path=mesh_path)

    t0 = time.time()
    rc = rfb.run_task(task, case_db, args)
    wall = time.time() - t0

    log_path = result_dir / f"{case_name}_{param_set}.log"
    res = DryRunResult(case_name, param_set, preset, krylov, ok=(rc == 0),
                        max_it_used=max_it, wall_time=wall, log_path=str(log_path))
    if log_path.exists():
        parsed = parse_log(log_path)
        res.residuals = parsed["residuals"]
        res.converged = parsed["converged"]
        res.reason = parsed["reason"]
        res.iterations = parsed["iterations"]
        res.solve_time = parsed["solve_time"]
        if parsed["petsc_error"] and res.ok:
            res.ok = False
            res.error = "PETSC ERROR in log"
    else:
        res.error = res.error or "log file not produced"
        res.ok = False
    return res


def enumerate_combos() -> List[Tuple[str, str, Path, str, str]]:
    tasks = rfb.discover_mesh_tasks(rfb.DEFAULT_MESH_DIR)
    combos = []
    for t in tasks:
        for preset in PRESETS:
            krylovs = ["gmres"] if preset in GMRES_ONLY_PRESETS else KRYLOVS
            for krylov in krylovs:
                combos.append((t.case_name, t.param_set, t.mesh_path, preset, krylov))
    return combos


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", action="store_true", help="Actually execute (otherwise just list combos)")
    p.add_argument("--workers", type=int, default=6, help="Concurrent FreeFEM processes")
    p.add_argument("--max-it", type=int, default=10, help="Iteration cap for this probe")
    p.add_argument("--timeout", type=int, default=180, help="Per-combo wall-clock timeout (s)")
    p.add_argument("--freefem-bin", type=str, default="FreeFem++-mpi")
    p.add_argument("--cases", type=str, default="", help="Optional comma-separated case filter")
    p.add_argument("--out", type=Path, default=RESULT_ROOT / "dry_run_results.json")
    args = p.parse_args()

    combos = enumerate_combos()
    if args.cases.strip():
        selected = {c.strip() for c in args.cases.split(",") if c.strip()}
        combos = [c for c in combos if c[0] in selected]

    print(f"[INFO] {len(combos)} combos to probe (max_it={args.max_it}, timeout={args.timeout}s, workers={args.workers})")

    if not args.run:
        for c in combos:
            print(f"  {c[0]}:{c[1]} preset={c[3]} krylov={c[4]}")
        return 0

    results: List[DryRunResult] = []
    done = 0
    total = len(combos)
    t_start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(run_one, cn, ps, mp, preset, krylov, args.max_it, args.timeout, args.freefem_bin): (cn, ps, preset, krylov)
            for (cn, ps, mp, preset, krylov) in combos
        }
        for fut in as_completed(futs):
            cn, ps, preset, krylov = futs[fut]
            try:
                res = fut.result()
            except Exception as e:  # noqa: BLE001
                res = DryRunResult(cn, ps, preset, krylov, ok=False, max_it_used=args.max_it, error=str(e))
            results.append(res)
            done += 1
            status = "OK" if res.ok else f"FAIL({res.error})"
            elapsed = time.time() - t_start
            wall_s = f"{res.wall_time:.1f}" if res.wall_time is not None else "None"
            print(f"[{done}/{total}] {cn}:{ps} {krylov}/{preset} -> {status} "
                  f"wall={wall_s}s solve={res.solve_time} iters={res.iterations} "
                  f"(elapsed {elapsed:.0f}s)", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nWrote {args.out} ({len(results)} results)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
