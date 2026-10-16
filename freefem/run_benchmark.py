#!/usr/bin/env python3
"""Full-benchmark driver: one FreeFEM process per solve, fixed wall-clock budget.

Evaluation rule (2026-09-28):
  * Every solve (case:param-set x preconditioner x Krylov method) is an
    independent FreeFem++-mpi process; its wall-clock budget (default 600 s)
    INCLUDES mesh loading, assembly and preconditioner setup.
  * Converging solves report iterations/time to rtol (1e-8, true residual).
    Non-converging solves are stopped at the budget and compared by the
    relative residual they reached ("timeout"), unless the Krylov method broke
    down first ("breakdown").
  * Iteration caps are effectively removed (1e6) so the budget, not max_it,
    is what stops a non-converging solve.

Each job runs in its own scratch directory (own runtime_case_config.idp), so
jobs can run concurrently; results are written per job (resumable: finished
jobs are skipped unless --force).

Solution error against a direct solve (off by default; solution_check.idp):
--save-solutions writes each job's solution vector to <out>/solutions/<job>.sol.gz
(with <job>.json: mesh SHA-256, NDOF, status). --ref-solutions DIR compares
each iterative solve with DIR/solutions/<case>_<set>__mumps_direct.sol.gz
(same mesh file required) and records the relative L2, Re(eps)-weighted L2,
curl, H(curl) and DOF-vector errors in the result JSON ("solution_check").
mumps/direct (sparse LU, not a benchmark combination) gives the references.

  python3 freefem/run_benchmark.py --list
  python3 freefem/run_benchmark.py --workers 5 --out results/benchmark
  python3 freefem/run_benchmark.py --only case2A:standard --combos cslp/gmres
  python3 freefem/run_benchmark.py --only case2A:standard --combos mumps/direct --save-solutions
  python3 freefem/run_benchmark.py --only case2A:standard --combos ssor/gmres \
      --ref-solutions results/benchmark
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import run_freefem_batch as rfb

ROOT = rfb.ROOT
FREEFEM_DIR = rfb.FREEFEM_DIR

# Preconditioner x Krylov combinations evaluated (problem_settings.md scope:
# GS, SSOR, AMG(GAMG), accelerated IC(0), CSLP, HX, CSLP+HX; GMRES and COCG
# wherever the preconditioner is a fixed COMPLEX-SYMMETRIC linear operator --
# forward GS is not symmetric, so gs/cocg is excluded (2026-09-28)).
DEFAULT_COMBOS = [
    "gs/gmres",
    "ssor/gmres", "ssor/cocg",
    "amg_gamg/gmres", "amg_gamg/cocg",
    "accel_ic/gmres", "accel_ic/cocg",
    "cslp/gmres", "hx/gmres", "cslp_hx/gmres",
]
NO_CAP = 1000000

# Sparse direct solve (MUMPS LU): reference solutions for the error check, not
# a benchmark combination (not in DEFAULT_COMBOS / rfb.PRESET_MAP).
DIRECT_COMBO = "mumps/direct"
DIRECT_OPTIONS = ("-ksp_type preonly -pc_type lu -pc_factor_mat_solver_type mumps "
                  "-ksp_monitor -ksp_converged_reason")

# Solution save / error check (solution_check.idp): files in the job directory,
# saved solutions in <out>/solutions/<job>.sol.gz with <job>.json beside.
SOL_SAVE_NAME = "solution_save.sol"
SOL_REF_NAME = "solution_ref.sol"
SOLUTIONS_DIR = "solutions"
SOL_ERROR_RE = re.compile(r"^SOLUTION_ERROR ndof (\d+) l2 (\S+) l2eps (\S+) curl (\S+) hcurl (\S+) "
                          r"vec (\S+) refL2 (\S+) refCurl (\S+)")
SOL_FAILED_RE = re.compile(r"^SOLUTION_CHECK_FAILED (.*)")

RES_RE = re.compile(r"^\s*(\d+) KSP Residual norm\s+(\S+)")
REASON_RE = re.compile(r"Linear solve (did not converge|converged) due to (\S+)")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def solution_file(out: Path, tag: str) -> Path:
    """Saved solution of job <tag> in the result directory out."""
    return out / SOLUTIONS_DIR / f"{tag}.sol.gz"


def find_reference(ref_dir: Path, tags: list, mesh: Path) -> tuple:
    """(path of the reference solution, None) for the first of tags (job names
    of the direct solve, in order of preference) saved in ref_dir, or (None,
    reason). The reference must come from a converged solve on the same mesh
    file (SHA-256)."""
    for t in tags:
        sol = solution_file(ref_dir, t)
        info_path = sol.with_name(f"{t}.json")
        if not sol.exists() or not info_path.exists():
            continue
        info = json.loads(info_path.read_text(encoding="utf-8"))
        if info.get("status") != "converged":
            return None, f"reference {t} did not converge ({info.get('status')})"
        if not mesh.exists() or info.get("mesh_sha256") != file_sha256(mesh):
            return None, f"reference {t} was computed on another mesh ({info.get('mesh')})"
        return sol, None
    return None, f"no reference solution in {ref_dir / SOLUTIONS_DIR} ({', '.join(tags)})"


def parse_solution_check(text: str, phases: dict) -> dict | None:
    """Errors printed by solution_check.idp (solver output without the log's
    time stamps; None if no error line). phases: PHASE times of the job."""
    rec = None
    for line in text.splitlines():
        m = SOL_ERROR_RE.match(line)
        if m:
            v = [float(x) for x in m.groups()[1:]]
            rec = dict(ndof=int(m.group(1)), rel_l2=v[0], rel_l2_eps=v[1], rel_curl=v[2],
                       rel_hcurl=v[3], rel_vec=v[4], ref_l2=v[5], ref_curl=v[6])
            continue
        m = SOL_FAILED_RE.match(line)
        if m:
            rec = dict(failed=m.group(1).strip())
    if rec is not None and "solution_check_start" in phases and "solution_check_end" in phases:
        rec["time"] = round(phases["solution_check_end"] - phases["solution_check_start"], 2)
    return rec


def solution_check_text(chk: dict | None) -> str:
    """Short console text of a result's solution_check ('' if none)."""
    if not chk:
        return ""
    if "failed" in chk:
        return f" no error check ({chk['failed']})"
    txt = (f" err L2={chk['rel_l2']:.2e} curl={chk['rel_curl']:.2e} Hcurl={chk['rel_hcurl']:.2e}"
           if "rel_l2" in chk else "")
    return txt + (" saved" if "saved" in chk else "")


def build_job_dir(work: Path, task: rfb.MeshTask, case_db: dict, preset: str, krylov: str,
                  rtol: float, sol_save_file: str = "", sol_ref_file: str = "") -> None:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for f in FREEFEM_DIR.iterdir():
        if f.suffix in (".edp", ".idp") and f.name != "runtime_case_config.idp":
            shutil.copy(f, work / f.name)

    class A:  # minimal argparse-like namespace for rfb.apply_preset
        pass
    a = A()
    a.preset, a.krylov, a.backend = preset, krylov, "petsc"
    a.petsc_options = rfb.DEFAULT_PETSC_OPTIONS
    a.max_it = NO_CAP
    a.gmres_restart = rfb.DEFAULT_GMRES_RESTART
    if f"{preset}/{krylov}" == DIRECT_COMBO:
        a.outer_method, a.petsc_options = "petsc", DIRECT_OPTIONS
    else:
        rfb.apply_preset(a)
    if rtol != 1e-8:
        a.petsc_options = re.sub(r"-ksp_rtol \S+", f"-ksp_rtol {rtol}", a.petsc_options, count=1) \
            if a.outer_method == "petsc" else a.petsc_options
    params = case_db[task.case_name]["parameter_sets"][task.param_set]
    cfg = rfb.build_runtime_config(
        task=task, params=params, phys=rfb.parse_physical_names(task.mesh_path),
        abc_mode="auto", backend=a.backend, petsc_options=a.petsc_options,
        save_vtk=False, result_dir=work, outer_method=a.outer_method,
        outer_rtol=rtol, outer_max_it=NO_CAP, krylov_method=krylov,
        gmres_restart=rfb.DEFAULT_GMRES_RESTART,
        sol_save_file=sol_save_file, sol_ref_file=sol_ref_file)
    (work / "runtime_case_config.idp").write_text(cfg, encoding="utf-8")


def _peak_footprint_gb_macos(pid: int) -> float | None:
    # macOS has no /proc: proc_pid_rusage(RUSAGE_INFO_V4) gives the lifetime
    # peak physical footprint (bytes), the closest counterpart of VmHWM.
    import ctypes
    try:
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    except OSError:
        return None
    buf = (ctypes.c_uint64 * 64)()   # rusage_info_v4: 16-byte uuid + uint64 fields
    if libc.proc_pid_rusage(ctypes.c_int(pid), ctypes.c_int(4), ctypes.byref(buf)) != 0:
        return None
    return buf[2 + 28] / 1024 ** 3   # ri_lifetime_max_phys_footprint (field 28 after the uuid)


def peak_rss_gb(pid: int) -> float | None:
    if sys.platform == "darwin":
        return _peak_footprint_gb_macos(pid)
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) / 1024 / 1024
    except OSError:
        return None
    return None


def run_job(task: rfb.MeshTask, case_db: dict, combo: str, out: Path, scratch: Path,
            budget: float, rtol: float, freefem_bin: str, save_solution: bool = False,
            ref_solution: Path | None = None) -> dict:
    """One solve. save_solution: write the solution to <out>/solutions/<job>.sol.gz
    (solution_check.idp). ref_solution: a saved solution (.sol.gz, see
    find_reference) to compute the errors against. Both off by default."""
    preset, krylov = combo.split("/")
    tag = f"{task.case_name}_{task.param_set}__{preset}_{krylov}"
    work = scratch / tag
    build_job_dir(work, task, case_db, preset, krylov, rtol,
                  sol_save_file=SOL_SAVE_NAME if save_solution else "",
                  sol_ref_file=SOL_REF_NAME if ref_solution else "")
    if ref_solution:
        with gzip.open(ref_solution, "rb") as fi, (work / SOL_REF_NAME).open("wb") as fo:
            shutil.copyfileobj(fi, fo)
    log_path = out / "logs" / f"{tag}.log"
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1")

    t0 = time.time()
    # stdbuf: FreeFEM's stdout is block-buffered on a pipe; line buffering keeps
    # the per-iteration timestamps honest and loses nothing when a job is killed.
    proc = subprocess.Popen(["stdbuf", "-oL", "-eL", freefem_bin, "-nw", "-v", "0",
                             "maxwell_edge03d_solver.edp"], cwd=work,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            bufsize=1, env=env, start_new_session=True)
    state = {"rss": 0.0}
    stop = threading.Event()

    def watch_rss():
        while not stop.is_set():
            r = peak_rss_gb(proc.pid)
            if r:
                state["rss"] = max(state["rss"], r)
            stop.wait(1.0)
    threading.Thread(target=watch_rss, daemon=True).start()

    def killer():
        # Budget measured on the REAL-TIME clock (time.time): under WSL2 the
        # monotonic clock that Event.wait() uses was measured to run ~4.5% fast
        # against the Windows clock (a 600 s wait ended after ~575 real seconds).
        last = time.time()
        while not stop.is_set():
            now = time.time()
            if now - last > 20:
                # the host slept (WSL suspended): the wall clock jumped, so this
                # run's timing is invalid -> kill it and do not record a result
                state["suspended"] = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                return
            last = now
            if now - t0 >= budget:
                state["killed"] = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                return
            stop.wait(0.5)
    threading.Thread(target=killer, daemon=True).start()

    res, reason, ndof, petsc_error, breakdown, phases = [], None, None, False, False, {}
    t_first = None
    sol_lines = []
    with log_path.open("w", encoding="utf-8") as logf:
        for line in proc.stdout:
            now = time.time() - t0
            logf.write(f"{now:9.2f} {line}")
            if not line.endswith("\n"):   # partial last line of a killed process
                continue
            if line.startswith("SOLUTION_"):
                sol_lines.append(line.rstrip("\n"))
                continue
            m = RES_RE.match(line)
            if m and " : " not in line:
                if t_first is None:
                    t_first = now
                res.append((int(m.group(1)), float(m.group(2)), round(now, 2)))
                continue
            m = REASON_RE.search(line)
            if m:
                reason = m.group(2)
            if line.startswith("NDOF = "):
                ndof = int(line.split("=")[1])
            if line.startswith("PHASE "):
                p = line.split()
                phases[p[1]] = round(now, 2)
            if "PETSC ERROR" in line:
                petsc_error = True
            if "COCG breakdown" in line:
                breakdown = True
    proc.wait()
    stop.set()
    wall = time.time() - t0

    if state.get("suspended"):
        shutil.rmtree(work, ignore_errors=True)
        raise RuntimeError("host suspended during the run; not recorded (re-run to retry)")
    killed = state.get("killed", False)
    if reason and reason.startswith("CONVERGED"):
        status = "converged"
    elif killed:
        status = "timeout" if res else "setup_timeout"
    elif breakdown or (reason and ("INDEFINITE" in reason or "BREAKDOWN" in reason)):
        status = "breakdown"
    elif petsc_error or proc.returncode != 0:
        status = "error"
    else:
        status = "stopped"    # e.g. DIVERGED_ITS (should not happen with NO_CAP) / DTOL
    r0 = res[0][1] if res else None
    rel = [(i, v / r0, t) for i, v, t in res] if r0 else []
    # keep the history compact: <= 1500 points, always including the last one
    step = max(1, len(rel) // 1500)
    hist = rel[::step] + ([rel[-1]] if rel and (len(rel) - 1) % step else [])
    rec = dict(
        case=task.case_name, param_set=task.param_set, preset=preset, krylov=krylov,
        status=status, reason=reason, ndof=ndof, wall=round(wall, 2), budget=budget,
        setup_time=round(t_first, 2) if t_first is not None else None,
        phases=phases, iterations=res[-1][0] if res else 0,
        final_relres=rel[-1][1] if rel else None,
        min_relres=min(v for _, v, _ in rel) if rel else None,
        peak_rss_gb=round(state["rss"], 3), returncode=proc.returncode, history=hist,
    )
    if save_solution or ref_solution:
        # solution_check.idp runs after "PHASE total": its time (and the solution
        # write) is part of wall, and kept apart in solution_check.time
        chk = parse_solution_check("\n".join(sol_lines), phases) or {}
        saved = work / SOL_SAVE_NAME
        if save_solution and any(l.startswith("SOLUTION_SAVED") for l in sol_lines) and saved.exists():
            dest = solution_file(out, tag)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with saved.open("rb") as fi, gzip.open(dest, "wb", compresslevel=6) as fo:
                shutil.copyfileobj(fi, fo)
            mesh = task.mesh_path
            info = dict(case=task.case_name, param_set=task.param_set, combo=combo, status=status,
                        final_relres=rec["final_relres"], ndof=ndof,
                        mesh=mesh.relative_to(ROOT).as_posix() if mesh.is_relative_to(ROOT) else str(mesh),
                        mesh_sha256=file_sha256(mesh),
                        saved=time.strftime("%Y-%m-%d %H:%M:%S"))
            dest.with_name(f"{tag}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
            chk["saved"] = dest.relative_to(ROOT).as_posix() if dest.is_relative_to(ROOT) else str(dest)
        if ref_solution:
            if "rel_l2" not in chk and "failed" not in chk:
                # e.g. stopped at the budget: solution_check.idp runs after the solve
                chk["failed"] = f"not evaluated, status {status}"
            chk["reference"] = (ref_solution.relative_to(ROOT).as_posix()
                                if ref_solution.is_relative_to(ROOT) else str(ref_solution))
        rec["solution_check"] = chk
    (out / "runs" / f"{tag}.json").write_text(json.dumps(rec), encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh-dir", type=Path, default=rfb.DEFAULT_MESH_DIR)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "benchmark")
    ap.add_argument("--scratch", type=Path, default=Path("/tmp/emag_bench"))
    ap.add_argument("--cases", default="", help="case filter, e.g. case2A,case3C")
    ap.add_argument("--only", default="", help="explicit case:param_set list, comma separated")
    ap.add_argument("--combos", default=",".join(DEFAULT_COMBOS))
    ap.add_argument("--budget", type=float, default=600.0, help="wall-clock seconds per solve, incl. setup")
    ap.add_argument("--rtol", type=float, default=1e-8)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--freefem-bin", default="FreeFem++-mpi")
    ap.add_argument("--force", action="store_true", help="re-run jobs that already have results")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--save-solutions", action="store_true",
                    help="write each solution to <out>/solutions/<job>.sol.gz (off by default)")
    ap.add_argument("--ref-solutions", type=Path, default=None, metavar="DIR",
                    help="result directory with saved mumps/direct solutions (DIR/solutions): "
                         "record the solution errors against them (off by default)")
    args = ap.parse_args()

    case_db = rfb.load_case_params()
    tasks = rfb.filter_tasks(rfb.discover_mesh_tasks(args.mesh_dir), args.cases)
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        tasks = [t for t in tasks if f"{t.case_name}:{t.param_set}" in want]
    tasks = [t for t in tasks
             if t.case_name in case_db and t.param_set in case_db[t.case_name]["parameter_sets"]]
    combos = [c.strip() for c in args.combos.split(",") if c.strip()]
    jobs = [(t, c) for c in combos for t in tasks]   # combo-major: spreads heavy jobs out
    (args.out / "runs").mkdir(parents=True, exist_ok=True)
    (args.out / "logs").mkdir(parents=True, exist_ok=True)

    def done(t, c):
        p, k = c.split("/")
        return (args.out / "runs" / f"{t.case_name}_{t.param_set}__{p}_{k}.json").exists()
    todo = [(t, c) for t, c in jobs if args.force or not done(t, c)]
    bad = [c for c in combos if c != DIRECT_COMBO and c.split("/")[0] not in rfb.PRESET_MAP]
    if bad:
        print(f"ERROR: unknown combination(s) {', '.join(bad)}")
        return 2
    print(f"{len(tasks)} case/param-sets x {len(combos)} combos = {len(jobs)} jobs; "
          f"{len(todo)} to run, budget {args.budget:.0f} s, {args.workers} workers"
          + (", saving solutions" if args.save_solutions else "")
          + (f", errors against {args.ref_solutions}" if args.ref_solutions else ""), flush=True)
    # reference solution per job (not for the direct solve itself)
    refs = {}
    if args.ref_solutions:
        for t, c in todo:
            if c == DIRECT_COMBO:
                continue
            ref, why = find_reference(args.ref_solutions, [f"{t.case_name}_{t.param_set}__mumps_direct"],
                                      t.mesh_path)
            refs[(t.case_name, t.param_set, c)] = ref
            if why:
                print(f"  WARNING {t.case_name}:{t.param_set} {c}: {why}; no error check")
    if args.list:
        for t, c in todo:
            print(f"  {t.case_name}:{t.param_set} {c}")
        return 0

    meta = dict(budget=args.budget, rtol=args.rtol, workers=args.workers, combos=combos,
                save_solutions=args.save_solutions or None,
                ref_solutions=str(args.ref_solutions) if args.ref_solutions else None,
                started=time.strftime("%Y-%m-%d %H:%M:%S"))
    (args.out / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    n = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_job, t, case_db, c, args.out, args.scratch, args.budget, args.rtol,
                          args.freefem_bin, args.save_solutions,
                          refs.get((t.case_name, t.param_set, c))): (t, c) for t, c in todo}
        for f in as_completed(futs):
            t, c = futs[f]
            n += 1
            try:
                r = f.result()
                fr = f"{r['final_relres']:.2e}" if r["final_relres"] is not None else "-"
                print(f"[{n}/{len(todo)}] {t.case_name}:{t.param_set} {c}: {r['status']} "
                      f"it={r['iterations']} rel={fr} wall={r['wall']:.0f}s "
                      f"setup={r['setup_time']} rss={r['peak_rss_gb']}GB"
                      f"{solution_check_text(r.get('solution_check'))}", flush=True)
            except Exception as e:  # keep the campaign going
                print(f"[{n}/{len(todo)}] {t.case_name}:{t.param_set} {c}: EXCEPTION {e!r}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
