#!/usr/bin/env python3
"""Resonance-proximity check for every case/param-set (runs resonance_check.edp).

For each mesh, finds the discrete modes of the benchmark operator nearest to the
operating k0 and writes results/resonance/resonance.json + a printed table:
relative distance |k_mode - k0|/k0 of the nearest mode (small = near-resonant).

  python3 freefem/resonance_check.py --workers 5
  python3 freefem/resonance_check.py --only case2A:standard,case3A:high_contrast
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import run_freefem_batch as rfb

MODE_RE = re.compile(r"MODE (\d+) k_re (\S+) k_im (\S+) reldist (\S+)")


def check(task: rfb.MeshTask, case_db: dict, scratch: Path, timeout: int, nev: int = 6,
          k0scale: float = 1.0) -> dict:
    tag = f"{task.case_name}_{task.param_set}_{k0scale}"
    work = scratch / tag
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for f in ("resonance_check.edp", "maxwell_common.idp"):
        shutil.copy(rfb.FREEFEM_DIR / f, work / f)
    params = case_db[task.case_name]["parameter_sets"][task.param_set]
    cfg = rfb.build_runtime_config(task=task, params=params, phys=rfb.parse_physical_names(task.mesh_path),
                                   abc_mode="auto", backend="petsc", petsc_options="", save_vtk=False,
                                   result_dir=work)
    (work / "runtime_case_config.idp").write_text(cfg, encoding="utf-8")
    try:
        p = subprocess.run(["FreeFem++", "-nw", "-v", "0", "resonance_check.edp", "-nev", str(nev),
                            "-k0scale", str(k0scale), "-maxit", "3000", "-ncv", str(max(4 * nev, 30))],
                           cwd=work,
                           capture_output=True, text=True, timeout=timeout)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        out += "\nTIMEOUT"
    (work / "resonance.log").write_text(out)
    modes = [dict(k_re=float(m.group(2)), k_im=float(m.group(3)), reldist=float(m.group(4)))
             for m in MODE_RE.finditer(out)]
    k0 = rfb.pick_k0(task.case_name, params) * k0scale
    rec = dict(case=task.case_name, param_set=task.param_set, k0=k0, k0scale=k0scale, modes=modes,
               nearest=min(modes, key=lambda d: d["reldist"]) if modes else None,
               ok="TIMEOUT" not in out and bool(modes))
    if rec["ok"]:
        shutil.rmtree(work, ignore_errors=True)   # keep the work dir (log) of failed checks
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--nev", type=int, default=6, help="number of modes nearest to k0 to compute")
    ap.add_argument("--k0scales", default="1.0",
                    help="comma list of k0 multipliers to probe (e.g. 0.99,0.995,1.005,1.01)")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--out", type=Path, default=rfb.ROOT / "results" / "resonance")
    ap.add_argument("--scratch", type=Path, default=Path("/tmp/emag_reson"))
    args = ap.parse_args()
    case_db = rfb.load_case_params()
    tasks = [t for t in rfb.discover_mesh_tasks(rfb.DEFAULT_MESH_DIR)
             if t.case_name in case_db and t.param_set in case_db[t.case_name]["parameter_sets"]]
    if args.only:
        want = set(args.only.split(","))
        tasks = [t for t in tasks if f"{t.case_name}:{t.param_set}" in want]
    args.out.mkdir(parents=True, exist_ok=True)
    res_file = args.out / "resonance.json"
    results = json.loads(res_file.read_text()) if res_file.exists() else {}
    with ThreadPoolExecutor(args.workers) as ex:
        scales = [float(s) for s in args.k0scales.split(",")]
        futs = {ex.submit(check, t, case_db, args.scratch, args.timeout, args.nev, s): t
                for t in tasks for s in scales}
        for f in as_completed(futs):
            r = f.result()
            key = f"{r['case']}:{r['param_set']}" + ("" if r["k0scale"] == 1.0 else f"@{r['k0scale']}")
            results[key] = r
            n = r["nearest"]
            print(f"{key:36s} k0={r['k0']:.4f} "
                  + (f"nearest k={n['k_re']:.4f}{n['k_im']:+.4f}i rel.dist={n['reldist']:.4f}" if n else "FAILED"),
                  flush=True)
            res_file.write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
