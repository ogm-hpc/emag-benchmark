#!/usr/bin/env python3
"""Run GMRES/COCG x preconditioner-preset combinations for selected cases,
parse the KSP convergence history out of each log, and dump the results as
one JSON file for later report rendering.

This is a thin orchestration layer over run_freefem_batch.py: it reuses that
module's apply_preset()/discover_mesh_tasks()/run_task() directly so every
combination goes through the exact same run path as a normal batch run (same
runtime_case_config.idp generation, same PETSC-ERROR-in-log failure check).

Usage:
  python3 freefem/generate_convergence_report.py \
      --cases case2A:standard,case2B:medium_iris,case2C:medium_slit \
      --presets jacobi,ssor,ic0_shift,ilu,amg_gamg \
      --krylovs gmres,cocg \
      --timeout 240 \
      --out results/convergence_report/report_data.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_freefem_batch as rfb  # noqa: E402

REPORT_RESULT_DIR = rfb.ROOT / "results" / "convergence_report"

DEFAULT_PRESETS = ["jacobi", "ssor", "ic0_shift", "ilu", "amg_gamg"]
DEFAULT_KRYLOVS = ["gmres", "cocg"]

KSP_LINE_RE = re.compile(r"^\s*(\d+)\s+KSP Residual norm\s+([0-9.eE+\-]+)")
REASON_RE = re.compile(
    r"Linear solve (converged|did not converge) due to (\w+) iterations (\d+)"
)
SOLVE_TIME_RE = re.compile(r"SOLVE_TIME\s*=\s*([0-9.eE+\-]+)")


@dataclass
class RunResult:
    case_name: str
    param_set: str
    krylov: str
    preset: str
    ok: bool
    residuals: List[Tuple[int, float]] = field(default_factory=list)
    reason: Optional[str] = None
    iterations: Optional[int] = None
    converged: Optional[bool] = None
    solve_time: Optional[float] = None
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


def run_one(case_name: str, param_set: str, krylov: str, preset: str, timeout: int) -> RunResult:
    result_dir = REPORT_RESULT_DIR / f"{case_name}_{param_set}" / f"{krylov}_{preset}"
    args = argparse.Namespace(
        mesh_dir=rfb.DEFAULT_MESH_DIR,
        cases=case_name,
        abc="auto",
        backend="petsc",
        preset=preset,
        krylov=krylov,
        freefem_bin="FreeFem++-mpi",
        run=True,
        save_vtk=False,
        result_dir=result_dir,
        petsc_options=rfb.DEFAULT_PETSC_OPTIONS,
        timeout=timeout,
    )
    rfb.apply_preset(args)

    case_db = rfb.load_case_params()
    tasks = rfb.discover_mesh_tasks(args.mesh_dir)
    tasks = [t for t in tasks if t.case_name == case_name and t.param_set == param_set]
    if not tasks:
        return RunResult(case_name, param_set, krylov, preset, ok=False, error="mesh not found")

    task = tasks[0]
    print(f"[REPORT-RUN] {case_name}:{param_set} krylov={krylov} preset={preset}", flush=True)
    rc = rfb.run_task(task, case_db, args)

    log_path = result_dir / f"{case_name}_{param_set}.log"
    res = RunResult(case_name, param_set, krylov, preset, ok=(rc == 0), log_path=str(log_path))
    if log_path.exists():
        parsed = parse_log(log_path)
        res.residuals = parsed["residuals"]
        res.converged = parsed["converged"]
        res.reason = parsed["reason"]
        res.iterations = parsed["iterations"]
        res.solve_time = parsed["solve_time"]
        if parsed["petsc_error"] and not res.error:
            res.error = "PETSC ERROR in log"
    else:
        res.error = res.error or "log file not produced"
    return res


def parse_case_list(spec: str) -> List[Tuple[str, str]]:
    pairs = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        case_name, _, param_set = item.partition(":")
        if not param_set:
            raise ValueError(f"expected case:paramset, got {item!r}")
        pairs.append((case_name, param_set))
    return pairs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cases", type=str, required=True, help="Comma-separated case:paramset pairs")
    p.add_argument("--presets", type=str, default=",".join(DEFAULT_PRESETS))
    p.add_argument("--krylovs", type=str, default=",".join(DEFAULT_KRYLOVS))
    p.add_argument("--timeout", type=int, default=300, help="Per-run timeout in seconds")
    p.add_argument("--out", type=Path, default=REPORT_RESULT_DIR / "report_data.json")
    args = p.parse_args()

    case_pairs = parse_case_list(args.cases)
    presets = [s.strip() for s in args.presets.split(",") if s.strip()]
    krylovs = [s.strip() for s in args.krylovs.split(",") if s.strip()]

    all_results: List[RunResult] = []
    total = len(case_pairs) * len(presets) * len(krylovs)
    done = 0
    for case_name, param_set in case_pairs:
        for krylov in krylovs:
            for preset in presets:
                res = run_one(case_name, param_set, krylov, preset, args.timeout)
                all_results.append(res)
                done += 1
                status = "OK" if res.ok else f"FAIL({res.error})"
                print(f"[{done}/{total}] {case_name}:{param_set} {krylov}/{preset} -> {status}", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in all_results], f, indent=2)
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
