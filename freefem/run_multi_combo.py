#!/usr/bin/env python3
"""DEPRECATED (2026-09-28) -- use freefem/run_benchmark.py.
This driver shares one assembly across 11 combos and a single per-case time
budget; the benchmark rule is now one process per solve with a 600 s budget that
INCLUDES setup. It also runs maxwell_edge03d_multi_solve.edp, which does NOT
have the 2026-09-28 fixes (anisotropic UPML, LossyMaterial permittivity,
true-residual monitoring, vectorized drivers). Kept only to reproduce old results.

Run ALL 11 in-scope (preset, krylov) combinations for a single (case,
parameter set) through ONE FreeFEM process (maxwell_edge03d_multi_solve.edp),
instead of 11 separate processes -- amortizes mesh-load + matrix-assembly
(the dominant cost for large meshes, per the dry-run-all sweep) across every
combo instead of repeating it 11x.

Usage:
  python3 freefem/run_multi_combo.py --cases case2A:standard --run \
      --max-it 10 --timeout 300 --out results/multi_combo/results.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_freefem_batch as rfb  # noqa: E402

RESULT_ROOT = rfb.ROOT / "results" / "multi_combo"
MULTI_SOLVER_EDP = rfb.FREEFEM_DIR / "maxwell_edge03d_multi_solve.edp"

# Curated case:paramset subsets for quick, representative runs -- chosen to
# span DISTINCT difficulty mechanisms and to actually discriminate between
# preconditioners (not "everything fails" or "everything trivially works"),
# rather than being an arbitrary sample. See problem_settings.md's "最小
# プリセット" section for the full rationale behind each pick.
CASE_PRESETS = {
    "minimal": [
        "case2A:standard",      # near-resonance closed cavity (hardest case
                                 # found so far): only CSLP makes real
                                 # progress, everything else stalls, native
                                 # COCG breaks down in <=6 iterations.
        "case2A:off_resonance",  # IDENTICAL mesh to standard, off-resonance
                                 # k0 only -- isolates frequency (not
                                 # geometry/mesh) as the difficulty driver.
        "case3C:coarse_check",  # benign/well-conditioned: all 7
                                 # preconditioners actually CONVERGE (18-134
                                 # iterations) -- the only case so far that
                                 # discriminates by relative EFFICIENCY
                                 # rather than success/failure.
        "case3D:sparse_array",  # periodic rod array: HX is a striking
                                 # outlier here (1405 iterations / 214s vs.
                                 # low hundreds for everything else) --
                                 # exposes a preconditioner-specific weakness
                                 # tied to this geometry, not seen elsewhere.
        "case2F:plex7",         # TEAM-19 (real experimental benchmark,
                                 # Bossavit et al. 1992): dielectric loading
                                 # + loss make AMG(GAMG) and accel_ic+COCG
                                 # actually converge, unlike the empty-cavity
                                 # variant -- direct evidence that material
                                 # loss/loading changes solvability, in a
                                 # waveguide-fed/iris-coupled geometry
                                 # distinct from every closed-cavity case.
    ],
}

NATIVE_PRESETS = ["gs", "ssor", "amg_gamg"]
KRYLOVS = ["gmres", "cocg"]
MAX_IT_RE = re.compile(r"-ksp_max_it\s+\d+")

COMBO_RE = re.compile(r"^COMBO_START preset=(\S+) krylov=(\S+)\s*$")
COMBO_END_RE = re.compile(r"^COMBO_END\s*$")
# Two variants, chosen per-preset in parse_multi_log():
#  - Native presets (gs/ssor/amg_gamg) go through PETSc's own set()+A^-1*b, so
#    their GENUINE outer-loop residual line IS PETSc's own indented monitor
#    output ("  0 KSP Residual norm ...") -- there is no separate inner solve
#    to leak from, so the loose (leading-whitespace-tolerant) pattern is correct.
#  - Hand-rolled presets (accel_ic/cslp/hx/cslp_hx) print their OWN outer-loop
#    line with zero leading whitespace ("5 KSP Residual norm ..."). cslp/hx/
#    cslp_hx additionally build inner P/Mgrad/Mvec auxiliary GAMG solves via
#    PETSc; despite -ksp_monitor_cancel -ksp_converged_reason 0 on those inner
#    solves (build_multi_config's inner_petsc_options), PETSc's global options
#    database still leaked SOME inner-solve monitor output into the log at
#    production scale (confirmed: iteration numbers reset to 0 and repeat
#    throughout the history, corrupting convergence plots) -- the leaked
#    lines are always indented, so the strict (zero-indent) pattern excludes
#    them while keeping the genuine outer-loop history intact.
KSP_LINE_RE_LOOSE = re.compile(r"^\s*(\d+)\s+KSP Residual norm\s+([0-9.eE+\-]+)")
KSP_LINE_RE_STRICT = re.compile(r"^(\d+)\s+KSP Residual norm\s+([0-9.eE+\-]+)")
NATIVE_PRESET_SET = {"gs", "ssor", "amg_gamg"}
REASON_RE = re.compile(
    r"Linear solve (converged|did not converge) due to (\w+) iterations (\d+)"
)
SOLVE_TIME_RE = re.compile(r"SOLVE_TIME\s*=\s*([0-9.eE+\-]+)")
NDOF_RE = re.compile(r"NDOF\s*=\s*(\d+)")
ASSEMBLY_TIME_RE = re.compile(r"ASSEMBLY_TIME\s*=\s*([0-9.eE+\-]+)")


@dataclass
class ComboResult:
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
    error: Optional[str] = None


def native_opts(preset: str, krylov: str, max_it: int) -> str:
    cfg = rfb.PRESET_MAP[preset]
    opts = f"{rfb.KRYLOV_MAP[krylov]} {cfg['petsc_options']} -ksp_monitor -ksp_converged_reason"
    return MAX_IT_RE.sub(f"-ksp_max_it {max_it}", opts)


def build_multi_config(task: rfb.MeshTask, params: Dict, phys, max_its: Dict[str, int],
                        result_dir: Path, gmres_restart: int = rfb.DEFAULT_GMRES_RESTART) -> str:
    # Reuse build_runtime_config for every field it already knows how to
    # compute (labels, k0, PML sigma, source position, material params, ...),
    # then append the multi-solve-specific fields.
    # PETSc's options database is process-global, not scoped per Mat/KSP object:
    # once ANY set(..., sparams="... -ksp_monitor -ksp_converged_reason") call
    # happens (the native GS/SSOR/AMG combos, which run first), those flags
    # leak into every LATER set() call's KSP too -- including P/Mgrad/Mvec's
    # own inner GAMG solves inside CSLP/HX/CSLP_HX, even though their own
    # option string never asked for monitor/reason. Confirmed empirically:
    # without this, CSLP/HX/CSLP_HX's "Linear solve ... iterations N" log
    # line becomes ambiguous (regex grabs an inner solve's leaked reason line
    # instead of the real outer-loop result) and the KSP Residual norm
    # history gets interleaved with inner-solve noise. Explicitly cancel both
    # for every inner auxiliary solve to keep them silent regardless of what
    # ran earlier in the same process.
    inner_petsc_options = rfb.PRESET_MAP["cslp"]["petsc_options"] + " -ksp_monitor_cancel -ksp_converged_reason 0"
    base = rfb.build_runtime_config(
        task=task, params=params, phys=phys, abc_mode="auto", backend="petsc",
        petsc_options=inner_petsc_options,  # inner GAMG opts for P/Mgrad/Mvec
        save_vtk=False, result_dir=result_dir,
        outer_method="petsc", krylov_method="gmres",
        gmres_restart=gmres_restart,
    )
    extra = [
        "",
        f"string nativeOptsGsGmres = \"{native_opts('gs', 'gmres', max_its['gs_gmres'])}\";",
        f"string nativeOptsGsCocg = \"{native_opts('gs', 'cocg', max_its['gs_cocg'])}\";",
        f"string nativeOptsSsorGmres = \"{native_opts('ssor', 'gmres', max_its['ssor_gmres'])}\";",
        f"string nativeOptsSsorCocg = \"{native_opts('ssor', 'cocg', max_its['ssor_cocg'])}\";",
        f"string nativeOptsAmgGmres = \"{native_opts('amg_gamg', 'gmres', max_its['amg_gamg_gmres'])}\";",
        f"string nativeOptsAmgCocg = \"{native_opts('amg_gamg', 'cocg', max_its['amg_gamg_cocg'])}\";",
        f"int accelIcMaxItGmres = {max_its['accel_ic_gmres']};",
        f"int accelIcMaxItCocg = {max_its['accel_ic_cocg']};",
        f"int cslpMaxIt = {max_its['cslp_gmres']};",
        f"int hxMaxIt = {max_its['hx_gmres']};",
        f"int cslpHxMaxIt = {max_its['cslp_hx_gmres']};",
        "",
    ]
    return base + "\n".join(extra)


def parse_multi_log(log_path: Path, case_name: str, param_set: str, max_its: Dict[str, int]) -> List[ComboResult]:
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    results: List[ComboResult] = []
    cur_preset = None
    cur_krylov = None
    cur_lines: List[str] = []

    def flush():
        if cur_preset is None:
            return
        block = "\n".join(cur_lines)
        line_re = KSP_LINE_RE_LOOSE if cur_preset in NATIVE_PRESET_SET else KSP_LINE_RE_STRICT
        residuals = []
        for ln in cur_lines:
            m = line_re.match(ln)
            if m:
                residuals.append((int(m.group(1)), float(m.group(2))))
        reason_m = REASON_RE.search(block)
        converged = reason = iterations = None
        if reason_m:
            converged = reason_m.group(1) == "converged"
            reason = reason_m.group(2)
            iterations = int(reason_m.group(3))
        solve_m = SOLVE_TIME_RE.search(block)
        solve_time = float(solve_m.group(1)) if solve_m else None
        key = f"{cur_preset}_{cur_krylov}"
        max_it = max_its.get(key, max_its.get(f"{cur_preset}_gmres", 0))
        ok = reason_m is not None
        results.append(ComboResult(
            case_name, param_set, cur_preset, cur_krylov, ok=ok, max_it_used=max_it,
            residuals=residuals, reason=reason, iterations=iterations,
            converged=converged, solve_time=solve_time,
            error=None if ok else "no converged-reason line found in block",
        ))

    for ln in lines:
        m = COMBO_RE.match(ln)
        if m:
            flush()
            cur_preset, cur_krylov = m.group(1), m.group(2)
            cur_lines = []
            continue
        if COMBO_END_RE.match(ln):
            flush()
            cur_preset = None
            cur_krylov = None
            cur_lines = []
            continue
        if cur_preset is not None:
            cur_lines.append(ln)
    flush()

    petsc_error = "PETSC ERROR" in text
    if petsc_error:
        for r in results:
            if r.ok:
                continue
    return results


def run_one(case_name: str, param_set: str, mesh_path: Path, max_its: Dict[str, int],
            timeout: int, freefem_bin: str, result_dir: Path,
            gmres_restart: int = rfb.DEFAULT_GMRES_RESTART) -> Tuple[int, Path]:
    task = rfb.MeshTask(case_name=case_name, param_set=param_set, mesh_path=mesh_path)
    case_db = rfb.load_case_params()
    params = case_db[case_name]["parameter_sets"][param_set]
    phys = rfb.parse_physical_names(mesh_path)

    config_text = build_multi_config(task, params, phys, max_its, result_dir, gmres_restart=gmres_restart)
    rfb.CONFIG_FILE.write_text(config_text, encoding="utf-8")

    result_dir.mkdir(parents=True, exist_ok=True)
    log_path = result_dir / f"{case_name}_{param_set}.log"
    cmd = [freefem_bin, str(MULTI_SOLVER_EDP)]
    print(f"[RUN-MULTI] {case_name}:{param_set} -> {mesh_path.name}", flush=True)
    with log_path.open("w", encoding="utf-8") as logf:
        try:
            p = subprocess.run(cmd, cwd=rfb.FREEFEM_DIR, stdout=logf, stderr=subprocess.STDOUT,
                                timeout=timeout if timeout > 0 else None)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            logf.write(f"\n[TIMEOUT] exceeded {timeout}s\n")
            rc = 124
    return rc, log_path


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
    p.add_argument("--cases", type=str, default="", help="Comma-separated case:paramset pairs (omit with --all/--case-preset)")
    p.add_argument("--all", action="store_true", help="Process every discovered case:paramset pair")
    p.add_argument("--case-preset", type=str, default="", choices=[""] + sorted(CASE_PRESETS.keys()),
                   help="Use a curated case:paramset subset instead of --cases/--all (see CASE_PRESETS)")
    p.add_argument("--max-it", type=int, default=10, help="Uniform iteration cap for all 11 combos (unless --max-it-json given)")
    p.add_argument("--max-it-json", type=Path, default=None,
                   help="Optional JSON: {\"case:paramset\": {\"gs_gmres\": N, ...}} for per-combo caps")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--freefem-bin", type=str, default="FreeFem++-mpi")
    p.add_argument("--gmres-restart", type=int, default=rfb.DEFAULT_GMRES_RESTART,
                   help="Restart cycle length for every hand-rolled GMRES driver "
                        "(cslp/accel_ic/hx/cslp_hx); default 300 (see problem_settings.md "
                        "for why 30 was raised to 300)")
    p.add_argument("--out", type=Path, default=RESULT_ROOT / "results.json")
    args = p.parse_args()

    # NOTE: deliberately sequential, not parallel -- build_multi_config() writes
    # the ONE shared runtime_case_config.idp path that
    # maxwell_edge03d_multi_solve.edp reads at startup; concurrent workers
    # racing to overwrite that file while another's subprocess is still
    # starting up could make a subprocess read the WRONG config (silently
    # solving a different case/paramset than intended). This risk already
    # exists in dry_run_all.py's 6-worker sweep -- not fixed retroactively
    # there since this consolidated tool supersedes it, but not repeated here.
    if args.case_preset:
        case_pairs = [tuple(item.split(":", 1)) for item in CASE_PRESETS[args.case_preset]]
    elif args.all:
        tasks_all = rfb.discover_mesh_tasks(rfb.DEFAULT_MESH_DIR)
        case_pairs = [(t.case_name, t.param_set) for t in tasks_all]
    else:
        if not args.cases.strip():
            print("[ERROR] must pass --cases, --all, or --case-preset")
            return 1
        case_pairs = parse_case_list(args.cases)
    per_case_max_its = {}
    if args.max_it_json and args.max_it_json.exists():
        per_case_max_its = json.loads(args.max_it_json.read_text(encoding="utf-8"))

    combo_keys = ["gs_gmres", "gs_cocg", "ssor_gmres", "ssor_cocg", "amg_gamg_gmres", "amg_gamg_cocg",
                  "accel_ic_gmres", "accel_ic_cocg", "cslp_gmres", "hx_gmres", "cslp_hx_gmres"]

    all_results: List[ComboResult] = []
    tasks = rfb.discover_mesh_tasks(rfb.DEFAULT_MESH_DIR)
    task_map = {(t.case_name, t.param_set): t.mesh_path for t in tasks}

    for case_name, param_set in case_pairs:
        key = f"{case_name}:{param_set}"
        max_its = per_case_max_its.get(key, {k: args.max_it for k in combo_keys})
        mesh_path = task_map.get((case_name, param_set))
        if mesh_path is None:
            print(f"[WARN] mesh not found for {key}")
            continue
        result_dir = RESULT_ROOT / f"{case_name}_{param_set}"
        rc, log_path = run_one(case_name, param_set, mesh_path, max_its, args.timeout, args.freefem_bin, result_dir,
                                gmres_restart=args.gmres_restart)
        status = "OK" if rc == 0 else f"FAIL(rc={rc})"
        print(f"[{status}] {key} -> log={log_path}", flush=True)
        if log_path.exists():
            results = parse_multi_log(log_path, case_name, param_set, max_its)
            all_results.extend(results)
            for r in results:
                print(f"    {r.preset}/{r.krylov}: ok={r.ok} iters={r.iterations} "
                      f"converged={r.converged} solve_time={r.solve_time}", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in all_results], f, indent=2)
    print(f"\nWrote {args.out} ({len(all_results)} combo results)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
