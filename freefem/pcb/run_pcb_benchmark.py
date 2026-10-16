#!/usr/bin/env python3
"""PCB-benchmark runner (pcb_problem_benchmark_settings.md 7.4-7.5).

Runs freefem/pcb/maxwell_pcb_solver.edp in isolated job directories. Shared,
unmodified pieces of the high-frequency benchmark are imported or copied:
run_freefem_batch (presets, runtime config), run_benchmark (log parsing,
RSS probe), and the .idp drivers in freefem/ (pcb/ files override same names).

  regress   Regression check of the fork (7.5): solve existing benchmark cases
            with maxwell_edge03d_solver.edp and maxwell_pcb_solver.edp under
            identical settings (capped iterations) and require identical
            residual histories and solutions.

  run       PCB benchmark (15.2): case/parameter sets of pcb_case_parameters.json
            x preconditioner/Krylov combinations, one FreeFEM process per solve
            under run_benchmark.py's rules (true residual, resumable), stopped
            by the v1.0 rule (docs/paper_plan.md 4.1): convergence, the
            iteration cap K_max of the combination (K_MAX_STANDARD; status
            max_it), breakdown, or a safety time limit of 12 h incl. setup
            (timeout). --k-max none restores the pre-v1.0 rule (600 s budget,
            no cap). The whole residual history is kept (re-read from the log;
            "history_full"), and "stop_rule" records the rule. Meshes from gmsh_templates/pcb/
            generate_pcb_meshes.py. Result JSON: run_benchmark.py's format plus
            a "pcb" field (excitation, frequency, port voltages, S-parameters).
            Excitation E2 (lumped ports, settings 3.3) by default; the extra
            combination mumps/direct gives MUMPS reference solutions.
            PETSc's GMRES uses modified Gram-Schmidt (PCB_GMRES_OPTIONS).
            HX and CSLP+HX mask the gradient correction on the PEC (on()
            penalty) rows (PCB_HX_DIRICHLET_MASK; --no-hx-mask for the
            unmasked fork of the existing benchmark).
            Up to 16 lumped ports; --port all (or a list) runs one job per
            excited port; --mrhs solves all ports in one job (multiple
            right-hand sides: shared set-up, block FGMRES, recycled FGMRES). Up to 4 dielectric volumes (Substrate, Substrate2..4
            with epsSub/tanDelta, epsSub2/tanDelta2, ...).
            Conductors are PEC, or surface-impedance boundaries (settings 3.4)
            for parameter sets with "conductorModel": "sibc" (faces from the
            problem's conductor_surfaces or the set's conductorSurfaces, Z_s
            from sigmaCond and the frequency), or volume conductors (settings
            5.5 stage 4) for "conductorModel": "volume" (mesh volume
            Conductor, eps_r = 1 - j sigmaCond/(omega eps0)).

  Machines (pcb_host.py, docs/pcb_handoff.md 3.1): on the reference WSL
  machine nothing changes. On a Mac the default --workers is the number of
  performance cores, and run excludes jobs whose memory estimate (WSL peak RSS
  x 1.2) exceeds 75 % of the physical memory and keeps the running jobs within
  it (--mem-budget, 0 = off). Results carry "host"; Mac summaries go to
  docs/pcb_results/<host>/, never over the WSL records.

  python3 freefem/pcb/run_pcb_benchmark.py regress
  python3 freefem/pcb/run_pcb_benchmark.py regress --max-it 30 --workers 4
  python3 freefem/pcb/run_pcb_benchmark.py regress --only case2A:standard:hx/gmres

  python3 freefem/pcb/run_pcb_benchmark.py ritz --suite core --workers 4
                           # Ritz probe (docs/matrix_features.md 8): 300 Arnoldi steps on A M^-1
                           # per set and preconditioner, no solve (pcb_ritz_probe.idp); PCB and
                           # existing sets (case2A:standard) as run selects them; features
                           # by ritz_features.py -> results/pcb_ritz/<host>/

  python3 freefem/pcb/run_pcb_benchmark.py run --list          # jobs, no FreeFEM
  python3 freefem/pcb/run_pcb_benchmark.py run --show-config P01-1:hx/gmres
  python3 freefem/pcb/run_pcb_benchmark.py run --workers 1 --out results/pcb_v1
                           # minimal set, 99 jobs, K_max rule (v1.0: every job alone)
  python3 freefem/pcb/run_pcb_benchmark.py run --workers 5 --k-max none
                           # the pre-v1.0 rule (600 s, no cap) into results/pcb_benchmark
  python3 freefem/pcb/run_pcb_benchmark.py run --suite extended --workers 5 --list
                           # suite tiers (settings 15, "suite" in pcb_case_parameters.json):
                           # core (= minimal set), extended, challenge; multi_rhs selects the
                           # sets with multiRhsBudgetPerPort (use with --mrhs / --port all)
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-1 --combos ssor/gmres
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-1 --port Port2 --combos mumps/direct
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P05-1 --combos ssor/gmres \
      --petsc-extra=-ksp_gmres_classicalgramschmidt --tag cgs
                           # diagnostic variant: extra PETSc options, result <set>@cgs
                           # (here: PETSc's default CGS instead of the PCB-standard MGS)
                           # (write --petsc-extra=... : a value starting with '-')
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-2,P05-2 --combos ssor/gmres,hx/gmres \
      --gmres-restart 30 --tag m30
                           # sensitivity (14 Phase 2): GMRES restart length (default 300),
                           # result <set>@m30; --accel-ic-alpha A (default 1.5) likewise
                           # for accel_ic/*. Non-default values need --tag.
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-1 --combos hx/gmres,cslp_hx/gmres \
      --no-hx-mask --tag nomask
                           # HX without the PEC-row mask (the existing benchmark's HX; before
                           # task I-9 the PCB standard), result <set>@nomask
  python3 freefem/pcb/run_pcb_benchmark.py run --roles sibc --combos mumps/direct
                           # SIBC parameter sets (conductor loss; handoff task I)
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P05-2 --combos mumps/direct \
      --freq 0.70,0.705,0.71
                           # frequency sweep on the parameter set's mesh: freqGHz replaced,
                           # results <set>@f0.7, <set>@f0.705, ... (check_p05_resonance.py)
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P07-1 --port all --combos mumps/direct
                           # one job per excited port (results <set>, <set>@Port2, ...);
                           # full S matrix: freefem/pcb/assemble_s_matrix.py
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P08-N4_s1 --combos cslp_hx/gmres \
      --mrhs gcro --budget 4800
                           # multiple right-hand sides (settings 12.2): every port in ONE
                           # process (result <set>@mrhs-gcro with the full S matrix);
                           # shared / block / gcro (pcb_mrhs.idp)
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-1 --combos mumps/direct --save-solutions
  python3 freefem/pcb/run_pcb_benchmark.py run --sets P01-1 --combos hx/gmres \
      --ref-solutions results/pcb_benchmark
                           # solution error (off by default; ../solution_check.idp): save the
                           # MUMPS solution (<out>/solutions/<job>.sol.gz), then record the
                           # relative L2 / curl / H(curl) errors and |dS| of iterative solves
                           # against it ("solution_check" of the result JSON; same mesh file
                           # required, single right-hand side only)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
FREEFEM_DIR = PCB_DIR.parent
sys.path.insert(0, str(FREEFEM_DIR))

import run_freefem_batch as rfb  # noqa: E402
import run_benchmark as rb  # noqa: E402
import pcb_host  # noqa: E402

ROOT = rfb.ROOT
HOST = pcb_host.detect()
PCB_SOLVER = "maxwell_pcb_solver.edp"
REF_SOLVER = "maxwell_edge03d_solver.edp"
DEFAULT_OUT = ROOT / "results" / "pcb_benchmark"
PCB_PARAMS_JSON = PCB_DIR / "pcb_case_parameters.json"
# suite tiers (settings 15): "suite" of a parameter set; multi_rhs = the sets
# with "multiRhsBudgetPerPort" (wall-clock budget per right-hand side, 12.2)
SUITES = ("core", "extended", "challenge", "multi_rhs")
PCB_MESH_DIR = ROOT / "generated_meshes" / "pcb" / "mesh"
C0_MM_GHZ = 299.792458   # speed of light [mm GHz]; PCB lengths are in mm

# Surface labels imposed as PEC (strongly, on()), and as Silver-Mueller ABC.
# PMC_Edge gets no term (natural boundary condition); port faces get the
# lumped-port term with E2 excitation (pcb_case_config.idp, port_list).
PCB_PEC_NAMES = ["PEC_Ground", "PEC_Trace", "PEC_Power", "PEC_Via", "PEC_ReturnVia"]
PCB_SM_NAMES = ["OuterBoundary"]

# One combination per outerMethod branch of the solver (petsc, pc_cocg,
# accel_ic, cslp, hx, cslp_hx), plus the UPML case for the PETSc and CSLP paths.
REGRESSION_CASES = [
    ("case2A", "standard", "ssor/gmres"),
    ("case2A", "standard", "ssor/cocg"),
    ("case2A", "standard", "accel_ic/cocg"),
    ("case2A", "standard", "cslp/gmres"),
    ("case2A", "standard", "hx/gmres"),
    ("case2A", "standard", "cslp_hx/gmres"),
    ("case1A", "standard", "amg_gamg/gmres"),
    ("case1A", "standard", "cslp/gmres"),
]
REGRESSION_TOL = 1.0e-12
# PCB-only combinations (no counterpart in the old solver): the PCB solver against
# a stored reference (residual history and solution norm, taken with
# regress --update-reference). One reference per host (key suffix @<host>):
# each machine generates its own meshes (Gmsh output differs between OSs), so
# a reference is only comparable on the machine that took it. The mesh MD5 is
# stored to tell a regenerated mesh from a solver change.
REFERENCE_CASES = [
    ("case2A", "standard", "npatch_asm/cocg"),
    ("case1A", "standard", "npatch_asm/cocg"),
]
REFERENCE_JSON = Path(__file__).resolve().parent / "regress_reference.json"
REFERENCE_TOL = 1.0e-8
REFERENCE_LOCK = threading.Lock()
# regress --all-cases: every parameter set of the existing benchmark with this combination
ALL_CASES_COMBO = "ssor/cocg"

# Wrapper run in the job directory: full-precision output of the residual
# history (hand-rolled drivers print through cout) and a dump of the solution.
WRAPPER = """cout.precision(16);
include "{solver}"
{{
  ofstream fo("solution.txt");
  fo.precision(17);
  for (int i = 0; i < Esolx[].n; i++) fo << real(Esolx[][i]) << " " << imag(Esolx[][i]) << "\\n";
}}
"""


MAX_PORTS = 16  # port slots portLabel1..16 of pcb_common.idp / pcb_port.idp
MAX_SIBC = 4    # SIBC slots sibcLabel1..4 of pcb_common.idp
MAX_SUBSTRATES = 4   # dielectric slots labSubstrate, labSubstrate2..4 of pcb_common.idp
# Dielectric slot i (0-based): mesh volume name, and the parameter names of its
# relative permittivity and loss tangent (pcb_case_parameters.json).
SUBSTRATE_SLOTS = [("Substrate", "epsSub", "tanDelta")] + \
    [(f"Substrate{i}", f"epsSub{i}", f"tanDelta{i}") for i in range(2, MAX_SUBSTRATES + 1)]
MU0 = 1.25663706212e-6   # vacuum permeability [H/m]
EPS0 = 8.8541878128e-12  # vacuum permittivity [F/m]
DEFAULT_SIGMA = 5.8e7    # copper [S/m]
RITZ_FILE = "ritz_hessenberg.txt"   # written by pcb_ritz_probe.idp in the job directory
CONDUCTOR_VOLUME = "Conductor"   # mesh volume of conductorModel "volume" (labConductor)


def pcb_case_config(excitation: str = "E1", src_dir=(1.0, 0.0, 0.0), substrates: list | None = None,
                    ports: list | None = None, excited_port: int = 0, port_current: float = 1.0,
                    pcb_diag: int = 0, sibc: list | None = None, sibc_zs: complex = 1.0,
                    hx_dirichlet_mask: int = 0, mrhs_method: str = "", mrhs_recycle: int = 20,
                    mrhs_recycle_max: int = 60, cond_label: int = -1, cond_sigma: float = 0.0,
                    cond_rel: float = 0.0, ritz_steps: int = 0, ritz_start: str = "rhs",
                    ritz_seed: int = 1, hx_vec_term: int = 0, hx_smoother: int = 0,
                    hx_vec_options: str = "", npatch_type: int = 0) -> str:
    """PCB-only settings read by maxwell_pcb_solver.edp (pcb_case_config.idp).
    substrates: MAX_SUBSTRATES dielectric slots [{label_tag, eps, tan_delta}]
    (label_tag -1 = unused; substrate_list). ports: [{label_tag, width, height,
    R, direction}] (lumped ports, settings 3.3); excited_port is 1-based (E2).
    sibc: [{label_tag, factor}] (surface impedance faces, settings 3.4) with
    the surface impedance sibc_zs [Ohm]. cond_label: volume conductor region
    (settings 5.5 stage 4, -1 = none) with sigma [S/m] and
    cond_rel = sigma/(omega eps0). ritz_steps > 0: Ritz probe instead of the
    solve (pcb_ritz_probe.idp, cmd_ritz). The defaults leave the existing
    benchmark cases unchanged (regression)."""
    ports = ports or []
    sibc = sibc or []
    substrates = list(substrates or [])
    if len(substrates) > MAX_SUBSTRATES:
        raise ValueError(f"{len(substrates)} dielectric regions, at most {MAX_SUBSTRATES} supported")
    substrates += [dict(label_tag=-1, eps=1.0, tan_delta=0.0)] * (MAX_SUBSTRATES - len(substrates))
    if len(ports) > MAX_PORTS:
        raise ValueError(f"{len(ports)} ports, at most {MAX_PORTS} supported")
    if len(sibc) > MAX_SIBC:
        raise ValueError(f"{len(sibc)} SIBC faces, at most {MAX_SIBC} supported")
    lines = [
        "// Auto-generated by run_pcb_benchmark.py",
        f"string excitation = \"{excitation}\";",
        f"real srcDirX = {src_dir[0]};",
        f"real srcDirY = {src_dir[1]};",
        f"real srcDirZ = {src_dir[2]};",
        "",
        f"int labSubstrate = {substrates[0]['label_tag']};",
        f"real epsSubstrate = {substrates[0]['eps']};",
        f"real tanDeltaSubstrate = {substrates[0]['tan_delta']};",
        "// Further dielectric regions (label -1 = unused)",
    ]
    for i in range(1, MAX_SUBSTRATES):
        d = substrates[i]
        lines.append(f"int labSubstrate{i + 1} = {d['label_tag']}; real epsSubstrate{i + 1} = {d['eps']}; "
                     f"real tanDeltaSubstrate{i + 1} = {d['tan_delta']};")
    lines += [
        "",
        "// Lumped ports: face label, sheet impedance Zs = R*w/h [Ohm], width w,",
        "// resistance R, unit height vector (ground -> trace). Label -1 = unused.",
        f"int nPorts = {len(ports)};",
        f"int excitedPort = {excited_port};",
        f"real portI = {port_current!r};",
    ]
    for i in range(MAX_PORTS):
        if i < len(ports):
            p = ports[i]
            d = p["direction"]
            lines.append(f"int portLabel{i + 1} = {p['label_tag']}; "
                         f"real portZs{i + 1} = {p['R'] * p['width'] / p['height']!r}; "
                         f"real portW{i + 1} = {p['width']!r}; real portR{i + 1} = {p['R']!r}; "
                         f"real portEx{i + 1} = {d[0]!r}; real portEy{i + 1} = {d[1]!r}; "
                         f"real portEz{i + 1} = {d[2]!r};")
        else:
            lines.append(f"int portLabel{i + 1} = -1; real portZs{i + 1} = 1.0; real portW{i + 1} = 1.0; "
                         f"real portR{i + 1} = 1.0; real portEx{i + 1} = 0.0; real portEy{i + 1} = 0.0; "
                         f"real portEz{i + 1} = 0.0;")
    lines += ["", "// Surface impedance boundary (SIBC): face label, number of conductor",
              "// surfaces the face stands for (1 outer, 2 zero-thickness sheet), Z_s [Ohm].",
              "// Label -1 = unused."]
    for i in range(MAX_SIBC):
        if i < len(sibc):
            lines.append(f"int sibcLabel{i + 1} = {sibc[i]['label_tag']}; "
                         f"real sibcFactor{i + 1} = {float(sibc[i]['factor'])!r};")
        else:
            lines.append(f"int sibcLabel{i + 1} = -1; real sibcFactor{i + 1} = 0.0;")
    zs = complex(sibc_zs)
    lines += [f"real sibcZsRe = {zs.real!r};", f"real sibcZsIm = {zs.imag!r};"]
    lines += ["", "// Volume conductor: region label (-1 = none), sigma [S/m], sigma/(omega eps0)",
              f"int labConductor = {int(cond_label)};",
              f"real condSigma = {float(cond_sigma)!r};",
              f"real condRel = {float(cond_rel)!r};"]
    lines += ["", "// HX / CSLP+HX: mask the gradient correction on the on() penalty rows",
              "// (1 = PCB standard of run for hx/cslp_hx; 0 = unmasked, as ../hx_precon.idp)",
              f"int hxDirichletMask = {int(hx_dirichlet_mask)};",
              "// HX vector (Pi) term (pcb_hx_vec.idp): 0 off, 1 Pi^T A Pi, 2 Pi^T (A + 2k0^2 Meps) Pi,",
              "// 3 Pi^T P Pi (cslp_hx); inner options ('' = petscOptions); HX smoother 0 Jacobi, 1 SGS",
              f"int hxVecTerm = {int(hx_vec_term)};",
              f"string hxVecOptions = \"{hx_vec_options}\";",
              f"int hxSmoother = {int(hx_smoother)};",
              "// Node patch (outerMethod npatch, pcb_npatch_precon.idp): 0 asm, 1 ras, 2 sms",
              f"int npatchType = {int(npatch_type)};"]
    lines += ["", "// Multiple right-hand sides (pcb_mrhs.idp): '' off, shared, block, gcro;",
              "// recycle: harmonic Ritz vectors added per right-hand side, max: recycle-space size (gcro)",
              f"string mrhsMethod = \"{mrhs_method}\";",
              f"int mrhsRecycle = {int(mrhs_recycle)};",
              f"int mrhsRecycleMax = {int(mrhs_recycle_max)};"]
    lines += ["", "// Ritz probe (pcb_ritz_probe.idp): Arnoldi steps (0 = solve as usual),",
              "// start vector rhs | random (seed), Hessenberg matrix file",
              f"int ritzSteps = {int(ritz_steps)};",
              f"string ritzStart = \"{ritz_start}\";",
              f"int ritzSeed = {int(ritz_seed)};",
              f"string ritzFile = \"{RITZ_FILE}\";"]
    lines += ["", f"int pcbDiag = {pcb_diag};", ""]
    return "\n".join(lines)


# PCB-only combination: sparse direct solve (reference solutions, port
# verification). Not a benchmark preconditioner, so not in rfb.PRESET_MAP.
DIRECT_COMBO = "mumps/direct"
DIRECT_OPTIONS = ("-ksp_type preonly -pc_type lu -pc_factor_mat_solver_type mumps "
                  "-ksp_monitor -ksp_converged_reason")

# PCB standard for PETSc's GMRES (gs, ssor, amg_gamg, ... /gmres): modified
# Gram-Schmidt, as the hand-rolled gmres_precon.idp. PETSc's default (classical
# Gram-Schmidt without refinement) loses orthogonality over the restart length
# 300 and stops with DIVERGED_BREAKDOWN at restarts (P05, P01-3; handoff task F).
# Not applied by regress (the fork check compares the solvers, not options).
# --petsc-extra comes after it (-ksp_gmres_classicalgramschmidt restores CGS).
PCB_GMRES_OPTIONS = "-ksp_gmres_modifiedgramschmidt"


# PCB-only presets: node-patch preconditioner (pcb_npatch_precon.idp, outerMethod
# npatch; Murayama et al. 2018, without the extended patch) -> npatchType.
# Hand-rolled GMRES / COCG; ras is not symmetric (GMRES only). Not in rfb.PRESET_MAP.
NPATCH_PRESETS = {"npatch_asm": 0, "npatch_ras": 1, "npatch_sms": 2}
# Standard combinations of the PCB runner (v1.0, docs/paper_plan.md): the
# existing benchmark's 10 and node patch with COCG.
PCB_DEFAULT_COMBOS = list(rb.DEFAULT_COMBOS) + ["npatch_asm/cocg"]

# Stopping rule of v1.0 (docs/paper_plan.md 4.1, task A3; decided 2026-10-05):
# converged, the iteration cap K_max of the combination (status "max_it"),
# breakdown, or the safety time limit (status "timeout"; should not happen).
# The trend indicators of the "max_it" results are computed by the summary
# (convergence_trend.py), never used to stop. Combinations not listed take the
# cap of their Krylov method (K_MAX_KRYLOV); mumps/direct has no cap.
K_MAX_STANDARD = {
    "gs/gmres": 10000, "ssor/gmres": 10000, "amg_gamg/gmres": 10000, "accel_ic/gmres": 10000,
    "hx/gmres": 10000,
    "ssor/cocg": 50000, "amg_gamg/cocg": 50000, "accel_ic/cocg": 50000, "npatch_asm/cocg": 50000,
    "cslp/gmres": 3000, "cslp_hx/gmres": 1000,
}
K_MAX_KRYLOV = {"gmres": 10000, "cocg": 50000}
SAFETY_TIME_LIMIT = 43200.0   # s per job (12 h) under the K_max rule
LEGACY_BUDGET = 600.0         # s per job incl. set-up: the rule before v1.0 (--k-max none)


def k_max_of(combo: str, spec: str) -> int | None:
    """Iteration cap of combo under --k-max spec ('standard', 'none' or an
    integer); None: no cap (the time budget stops the solve)."""
    if spec == "none" or combo == DIRECT_COMBO:
        return None
    if spec == "standard":
        return K_MAX_STANDARD.get(combo, K_MAX_KRYLOV[combo.split("/")[1]])
    return int(spec)


def k_max_problem(spec: str, tag: str, mrhs: str) -> str | None:
    """Why --k-max spec is not allowed, or None."""
    if mrhs and spec != "none":
        return "--mrhs keeps the time budget (multi-RHS is not in the v1.0 records): use --k-max none"
    if spec in ("standard", "none"):
        return None
    if not spec.isdigit() or int(spec) < 1:
        return f"--k-max {spec}: give standard, none or a positive integer"
    if not tag:
        return "--k-max with a number (not the standard caps) needs --tag"
    return None


LOG_RES_RE = re.compile(r"^\s*(\S+) (.*)$")


def full_history(log_path: Path) -> list | None:
    """Every residual of the outer solve, [[iteration, relative residual, time
    since start], ...], re-read from run_job's log (run_job keeps <= ~1500
    points in the result; v1.0 records the whole history, paper_plan 4.4). Same
    parsing as run_benchmark.run_job; None without residual lines."""
    if not log_path.exists():
        return None
    res = []
    with log_path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.endswith("\n"):   # partial last line of a killed process
                continue
            m = LOG_RES_RE.match(line.rstrip("\n"))
            if not m:
                continue
            body = m.group(2) + "\n"
            mr = rb.RES_RE.match(body)
            if mr and " : " not in body:
                try:
                    res.append((int(mr.group(1)), float(mr.group(2)), round(float(m.group(1)), 2)))
                except ValueError:
                    continue
    if not res or res[0][1] == 0.0:
        return None
    r0 = res[0][1]
    return [[i, v / r0, tm] for i, v, tm in res]


def apply_stop_rule(r: dict, k_max: int | None, log_path: Path) -> None:
    """v1.0 fields of a run_job result: the whole residual history, the stop
    reason (status "max_it" for DIVERGED_ITS at the cap) and the rule in force."""
    hist = full_history(log_path)
    if hist and r.get("history") and hist[-1][0] == r["history"][-1][0]:
        r["history"] = hist
        r["history_full"] = True
    else:
        r["history_full"] = False
    if k_max is not None and r.get("status") == "stopped" and r.get("reason") == "DIVERGED_ITS":
        r["status"] = "max_it"
    r["stop_rule"] = dict(k_max=k_max, time_limit=r.get("budget"),
                          rule="k_max" if k_max is not None else "budget")


def pcb_combo_problem(combo: str) -> str | None:
    """Why combo (preset/krylov) is not a valid combination, or None."""
    preset, _, krylov = combo.partition("/")
    if combo == DIRECT_COMBO:
        return None
    if preset in NPATCH_PRESETS:
        if krylov not in ("gmres", "cocg"):
            return f"{combo}: the node-patch presets take gmres or cocg"
        if preset == "npatch_ras" and krylov == "cocg":
            return f"{combo}: npatch_ras is not symmetric (gmres only)"
        return None
    if preset not in rfb.PRESET_MAP or krylov not in rfb.KRYLOV_MAP:
        return f"unknown combination {combo}"
    return None


def pcb_standard_extra(a) -> str:
    """PCB-standard PETSc options appended for this combination ('' if none)."""
    if a.outer_method == "petsc" and a.krylov == "gmres":
        return PCB_GMRES_OPTIONS
    return ""


def preset_namespace(preset: str, krylov: str, max_it: int,
                     gmres_restart: int = rfb.DEFAULT_GMRES_RESTART):
    """rfb.apply_preset on a minimal argparse-like namespace (gmres_restart:
    -ksp_gmres_restart of PETSc's GMRES; the hand-rolled drivers read it from
    runtime_case_config.idp)."""
    class A:
        pass
    a = A()
    a.preset, a.krylov, a.backend = preset, krylov, "petsc"
    a.petsc_options = rfb.DEFAULT_PETSC_OPTIONS
    a.max_it = max_it
    a.gmres_restart = gmres_restart
    if f"{preset}/{krylov}" == DIRECT_COMBO:
        a.outer_method, a.petsc_options = "petsc", DIRECT_OPTIONS
        return a
    if preset in NPATCH_PRESETS:
        a.outer_method, a.petsc_options, a.backend = "npatch", "", "none"
        return a
    rfb.apply_preset(a)
    return a


def build_job_dir(work: Path, solver: str, task: rfb.MeshTask, params: dict, preset: str,
                  krylov: str, max_it: int) -> None:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for f in FREEFEM_DIR.iterdir():
        if f.suffix in (".edp", ".idp") and f.name != "runtime_case_config.idp":
            shutil.copy(f, work / f.name)
    if solver == PCB_SOLVER:
        for f in PCB_DIR.iterdir():
            if f.suffix in (".edp", ".idp"):
                shutil.copy(f, work / f.name)

    a = preset_namespace(preset, krylov, max_it)
    cfg = rfb.build_runtime_config(
        task=task, params=params, phys=rfb.parse_physical_names(task.mesh_path),
        abc_mode="auto", backend=a.backend, petsc_options=a.petsc_options,
        save_vtk=False, result_dir=work, outer_method=a.outer_method,
        outer_rtol=1e-8, outer_max_it=max_it, krylov_method=krylov,
        gmres_restart=rfb.DEFAULT_GMRES_RESTART)
    (work / "runtime_case_config.idp").write_text(cfg, encoding="utf-8")
    (work / "pcb_case_config.idp").write_text(pcb_case_config(), encoding="utf-8")
    (work / "regress_wrap.edp").write_text(WRAPPER.format(solver=solver), encoding="utf-8")


def run_solver(work: Path, log_path: Path, freefem_bin: str, timeout: float) -> dict:
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1")
    t0 = time.time()
    try:
        p = subprocess.run(["stdbuf", "-oL", "-eL", freefem_bin, "-nw", "-v", "0", "regress_wrap.edp"],
                           cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           env=env, timeout=timeout)
        out, rc = p.stdout, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") if isinstance(e.stdout, str) else "", -9
    log_path.write_text(out, encoding="utf-8")

    hist, ndof, reason, petsc_error = [], None, None, False
    for line in out.splitlines():
        m = rb.RES_RE.match(line)
        if m and " : " not in line:
            hist.append(float(m.group(2)))
            continue
        m = rb.REASON_RE.search(line)
        if m:
            reason = m.group(2)
        if line.startswith("NDOF = "):
            ndof = int(line.split("=")[1])
        if "PETSC ERROR" in line:
            petsc_error = True
    sol = []
    sol_path = work / "solution.txt"
    if sol_path.exists():
        vals = [float(v) for v in sol_path.read_text().split()]
        sol = list(zip(vals[0::2], vals[1::2]))
    return dict(returncode=rc, petsc_error=petsc_error, ndof=ndof, reason=reason,
                history=hist, solution=sol, wall=round(time.time() - t0, 2))


def rel_diff_solution(ref: list, new: list) -> float:
    num = sum((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a, b in zip(ref, new))
    den = sum(a[0] ** 2 + a[1] ** 2 for a in ref)
    return math.sqrt(num / den) if den > 0 else (0.0 if num == 0 else math.inf)


def rel_diff_history(ref: list, new: list) -> float:
    return max((abs(a - b) / abs(a) if a != 0 else abs(b) for a, b in zip(ref, new)), default=0.0)


def regress_one(case: str, pset: str, combo: str, case_db: dict, mesh_dir: Path, out: Path,
                scratch: Path, max_it: int, freefem_bin: str, timeout: float) -> dict:
    preset, krylov = combo.split("/")
    task = rfb.MeshTask(case_name=case, param_set=pset, mesh_path=mesh_dir / f"{case}_{pset}.msh")
    params = case_db[case]["parameter_sets"][pset]
    tag = f"{case}_{pset}__{preset}_{krylov}"
    runs = {}
    for label, solver in (("ref", REF_SOLVER), ("pcb", PCB_SOLVER)):
        work = scratch / f"{tag}__{label}"
        build_job_dir(work, solver, task, params, preset, krylov, max_it)
        runs[label] = run_solver(work, out / "logs" / f"{tag}__{label}.log", freefem_bin, timeout)
        shutil.rmtree(work, ignore_errors=True)
    ref, new = runs["ref"], runs["pcb"]
    problems = []
    for label, r in runs.items():
        if r["returncode"] != 0 or r["petsc_error"]:
            problems.append(f"{label} failed (rc={r['returncode']}, petsc_error={r['petsc_error']})")
        if not r["history"] or not r["solution"]:
            problems.append(f"{label} produced no residual history or solution")
    if ref["ndof"] != new["ndof"]:
        problems.append(f"NDOF {ref['ndof']} != {new['ndof']}")
    if len(ref["history"]) != len(new["history"]):
        problems.append(f"iterations {len(ref['history'])} != {len(new['history'])}")
    if len(ref["solution"]) != len(new["solution"]):
        problems.append(f"solution length {len(ref['solution'])} != {len(new['solution'])}")
    d_hist = rel_diff_history(ref["history"], new["history"])
    d_sol = rel_diff_solution(ref["solution"], new["solution"]) if ref["solution"] and new["solution"] else math.inf
    if d_hist > REGRESSION_TOL:
        problems.append(f"residual history differs (max rel {d_hist:.2e})")
    if d_sol > REGRESSION_TOL:
        problems.append(f"solution differs (rel {d_sol:.2e})")
    return dict(case=case, param_set=pset, combo=combo, max_it=max_it, ndof=ref["ndof"],
                iterations=len(ref["history"]) - 1 if ref["history"] else 0,
                final_relres=(ref["history"][-1] / ref["history"][0]) if ref["history"] else None,
                history_max_rel_diff=d_hist, solution_rel_diff=d_sol,
                wall_ref=ref["wall"], wall_pcb=new["wall"],
                passed=not problems, problems=problems)


def regress_reference_one(case: str, pset: str, combo: str, case_db: dict, mesh_dir: Path, out: Path,
                          scratch: Path, max_it: int, freefem_bin: str, timeout: float,
                          update: bool) -> dict:
    """A PCB-only combination (no counterpart in the old solver, e.g. npatch):
    the PCB solver against the stored reference (REFERENCE_JSON: residual
    history and solution norm, REFERENCE_TOL). update: store this run instead."""
    preset, krylov = combo.split("/")
    task = rfb.MeshTask(case_name=case, param_set=pset, mesh_path=mesh_dir / f"{case}_{pset}.msh")
    params = case_db[case]["parameter_sets"][pset]
    tag = f"{case}_{pset}__{preset}_{krylov}"
    work = scratch / f"{tag}__pcb"
    build_job_dir(work, PCB_SOLVER, task, params, preset, krylov, max_it)
    r = run_solver(work, out / "logs" / f"{tag}__pcb.log", freefem_bin, timeout)
    shutil.rmtree(work, ignore_errors=True)
    problems = []
    if r["returncode"] != 0 or r["petsc_error"] or not r["history"] or not r["solution"]:
        problems.append(f"pcb failed (rc={r['returncode']}, petsc_error={r['petsc_error']})")
    key = f"{case}:{pset}:{combo}@{HOST.name}"
    mesh_md5 = hashlib.md5(task.mesh_path.read_bytes()).hexdigest() if task.mesh_path.exists() else None
    sol_l2 = math.sqrt(sum(a * a + b * b for a, b in r["solution"])) if r["solution"] else None
    with REFERENCE_LOCK:
        refs = json.loads(REFERENCE_JSON.read_text(encoding="utf-8")) if REFERENCE_JSON.exists() else {}
        if update and not problems:
            refs[key] = dict(ndof=r["ndof"], mesh_md5=mesh_md5, max_it=max_it, history=r["history"],
                             solution_l2=sol_l2, date=time.strftime("%Y-%m-%d"), host=HOST.name)
            REFERENCE_JSON.write_text(json.dumps(refs, indent=1) + "\n", encoding="utf-8")
    d_hist = d_sol = math.inf
    if update and not problems:
        d_hist = d_sol = 0.0
    elif key not in refs:
        problems.append(f"no stored reference for host {HOST.name} in {REFERENCE_JSON.name} "
                        f"(regress --update-reference)")
    elif not problems:
        ref = refs[key]
        if ref["max_it"] != max_it:
            problems.append(f"reference taken with --max-it {ref['max_it']}")
        if ref.get("mesh_md5") and ref["mesh_md5"] != mesh_md5:
            problems.append(f"mesh {task.mesh_path.name} changed since the reference (MD5)")
        if ref["ndof"] != r["ndof"]:
            problems.append(f"NDOF {ref['ndof']} != {r['ndof']}")
        if len(ref["history"]) != len(r["history"]):
            problems.append(f"iterations {len(ref['history'])} != {len(r['history'])}")
        d_hist = rel_diff_history(ref["history"], r["history"])
        d_sol = abs(sol_l2 - ref["solution_l2"]) / ref["solution_l2"]
        if d_hist > REFERENCE_TOL:
            problems.append(f"residual history differs (max rel {d_hist:.2e})")
        if d_sol > REFERENCE_TOL:
            problems.append(f"solution norm differs (rel {d_sol:.2e})")
    return dict(case=case, param_set=pset, combo=combo, max_it=max_it, ndof=r["ndof"],
                iterations=len(r["history"]) - 1 if r["history"] else 0,
                history_max_rel_diff=d_hist, solution_rel_diff=d_sol, wall_pcb=r["wall"],
                kind="reference", passed=not problems, problems=problems)


def regress_npatch_toy(out: Path, freefem_bin: str, timeout: float) -> dict:
    """test_npatch_toy.edp (n = 6): the assembled node-patch matrix against the
    patch-by-patch application, complex symmetry of asm / sms, and convergence
    of asm and sms with COCG."""
    problems, vals = [], {}
    for np_type in (0, 2):
        try:
            p = subprocess.run([freefem_bin, "-nw", "-v", "0", "test_npatch_toy.edp", "-n", "6", "-np", str(np_type)],
                               cwd=PCB_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               timeout=timeout)
            text = p.stdout
        except subprocess.TimeoutExpired:
            text = ""
        (out / "logs" / f"npatch_toy_np{np_type}.log").write_text(text, encoding="utf-8")
        for name, pat in (("check_patch", r"CHECK_PATCH .* = (\S+)"), ("check_sym", r"CHECK_SYM \S+ (\S+)")):
            m = re.search(pat, text)
            if m:
                vals[f"{name}_np{np_type}"] = float(m.group(1))
        conv = re.findall(r"RESULT B npatch_\w+ cocg it=(\d+) .* conv=(\d)", text)
        if not conv or conv[0][1] != "1":
            problems.append(f"np {np_type}: COCG did not converge")
        else:
            vals[f"cocg_it_np{np_type}"] = int(conv[0][0])
    for k in ("check_patch_np0", "check_sym_np0", "check_sym_np2"):
        if k not in vals:
            problems.append(f"{k} missing")
        elif vals[k] > 1.0e-12:
            problems.append(f"{k} = {vals[k]:.2e} > 1e-12")
    return dict(case="toy", param_set="n6", combo="npatch", kind="toy", checks=vals,
                passed=not problems, problems=problems)


def cmd_regress(args: argparse.Namespace) -> int:
    case_db = rfb.load_case_params()
    cases = list(REGRESSION_CASES) + list(REFERENCE_CASES)
    if args.all_cases:
        # every parameter set of case1A-3F once (materials, lossy regions, TEAM-19,
        # UPML of each case through the assembly), before the old solver is retired
        # (docs/paper_plan.md A2)
        cases += [(c, p, ALL_CASES_COMBO) for c in sorted(case_db)
                  for p in case_db[c]["parameter_sets"]
                  if (c, p, ALL_CASES_COMBO) not in cases]
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        cases = [c for c in cases if f"{c[0]}:{c[1]}:{c[2]}" in want]
    out = args.out / "regression"
    (out / "logs").mkdir(parents=True, exist_ok=True)
    toy = not args.only or "toy" in {s.strip() for s in args.only.split(",")}
    n_ref = sum(c in REFERENCE_CASES for c in cases)
    print(f"{len(cases) - n_ref} regression cases x 2 solvers, {n_ref} against the stored reference"
          + (", node-patch toy check" if toy else "")
          + f", max_it={args.max_it}, {args.workers} workers", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {}
        for c, p, k in cases:
            if (c, p, k) in REFERENCE_CASES:
                fut = ex.submit(regress_reference_one, c, p, k, case_db, args.mesh_dir, out, args.scratch,
                                args.max_it, args.freefem_bin, args.timeout, args.update_reference)
            else:
                fut = ex.submit(regress_one, c, p, k, case_db, args.mesh_dir, out, args.scratch,
                                args.max_it, args.freefem_bin, args.timeout)
            futs[fut] = (c, p, k)
        if toy:
            futs[ex.submit(regress_npatch_toy, out, args.freefem_bin, args.timeout)] = ("toy", "n6", "npatch")
        for f in as_completed(futs):
            c, p, k = futs[f]
            try:
                r = f.result()
            except Exception as e:  # keep going; report as failure
                r = dict(case=c, param_set=p, combo=k, passed=False, problems=[repr(e)])
            results.append(r)
            verdict = "PASS" if r["passed"] else "FAIL"
            if r.get("kind") == "toy":
                detail = " ".join(f"{n}={v:.1e}" if isinstance(v, float) else f"{n}={v}"
                                  for n, v in (r.get("checks") or {}).items())
            else:
                detail = (f"it={r.get('iterations')} hist={r.get('history_max_rel_diff', math.inf):.1e} "
                          f"sol={r.get('solution_rel_diff', math.inf):.1e}"
                          + (" (reference)" if r.get("kind") == "reference" else ""))
            print(f"[{verdict}] {c}:{p} {k}: {detail} {'; '.join(r['problems'])}", flush=True)
    results.sort(key=lambda r: (r["case"], r["combo"]))
    meta = dict(date=time.strftime("%Y-%m-%d %H:%M:%S"), tol=REGRESSION_TOL, max_it=args.max_it,
                ref_solver=REF_SOLVER, pcb_solver=PCB_SOLVER, results=results)
    (out / "regression.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    n_fail = sum(not r["passed"] for r in results)
    print(f"{len(results) - n_fail}/{len(results)} passed -> {out / 'regression.json'}")
    return 0 if n_fail == 0 else 1


# ---------------------------------------------------------------------------
# run: PCB benchmark
# ---------------------------------------------------------------------------
def load_pcb_cases() -> dict:
    with PCB_PARAMS_JSON.open(encoding="utf-8") as f:
        return json.load(f)


def eval_param(expr, params: dict) -> float:
    """A number, or an arithmetic expression of parameter names ("L/2")."""
    if isinstance(expr, (int, float)):
        return float(expr)
    names = {k: v for k, v in params.items() if isinstance(v, (int, float))}
    return float(eval(str(expr), {"__builtins__": {}}, names))


def expected_physical(pdef: dict) -> dict:
    """{(dim, name): tag} of the groups the template defines (pcb_case_parameters.json),
    used when the mesh is not available. Optional volumes (a dielectric region
    that only some parameter sets have, e.g. the solder resist Substrate2 of
    P02) are left out: their slot would need the set's epsSub2; optional
    surfaces (an empty label) are kept."""
    pg = pdef.get("physical_groups", {})
    out = {}
    for kind, dim in (("volumes", 3), ("surfaces", 2), ("surfaces_optional", 2)):
        for name, tag in pg.get(kind, {}).items():
            out[(dim, name)] = int(tag)
    return out


def check_mesh_physical(pdef: dict, mesh: Path) -> dict:
    """Physical groups of the mesh; the required ones must match the JSON tags."""
    phys = rfb.parse_physical_names(mesh)
    pg = pdef.get("physical_groups", {})
    for kind, dim in (("volumes", 3), ("surfaces", 2)):
        for name, tag in pg.get(kind, {}).items():
            if phys.get((dim, name)) != int(tag):
                raise RuntimeError(f"{mesh.name}: physical group {name} is {phys.get((dim, name))}, "
                                   f"expected {tag} (regenerate the mesh)")
    return phys


def port_source(pdef: dict, params: dict, port_label: str) -> dict:
    """E1 substitute for a lumped port (settings 15.4): a Gaussian volume source
    at the port centre, polarized along the port direction (ground -> trace),
    width = half the port height."""
    ports = {p["label"]: p for p in pdef.get("ports", [])}
    if port_label not in ports:
        raise KeyError(f"port {port_label} not defined (have {', '.join(ports)})")
    p = ports[port_label]
    return dict(port=port_label,
                center=[eval_param(c, params) for c in p["center"]],
                direction=[float(v) for v in p["direction"]],
                width=0.5 * eval_param(p["height"], params),
                port_width=eval_param(p["width"], params),
                port_height=eval_param(p["height"], params),
                R=float(p.get("R", 50.0)))


def surface_impedance(f_ghz: float, sigma: float) -> complex:
    """Leontovich surface impedance Z_s = (1+j) sqrt(omega mu0 / (2 sigma)) [Ohm]
    of a good conductor (settings 3.4; exp(+j omega t))."""
    return (1 + 1j) * math.sqrt(2 * math.pi * f_ghz * 1e9 * MU0 / (2 * sigma))


def conductor_model(pdef: dict, params: dict) -> tuple:
    """(model, sigma [S/m], {surface name: n_f}) of a parameter set: model
    'pec' (default) or 'sibc' on the problem's conductor_surfaces, or on the
    parameter set's own conductorSurfaces (e.g. a finite-thickness trace,
    whose surface is an outer face: n_f = 1); or 'volume', the mesh volume
    Conductor with conductivity sigma (settings 5.5 stage 4, no SIBC faces)."""
    model = params.get("conductorModel", "pec")
    if model == "pec":
        return "pec", None, {}
    if model == "volume":
        sigma = float(params.get("sigmaCond", DEFAULT_SIGMA))
        if not sigma > 0:
            raise ValueError(f"sigmaCond {sigma}: must be > 0")
        return "volume", sigma, {}
    if model != "sibc":
        raise ValueError(f"conductorModel {model!r}: use 'pec', 'sibc' or 'volume'")
    faces = params.get("conductorSurfaces") or pdef.get("conductor_surfaces") or {}
    if not faces:
        raise ValueError("conductorModel 'sibc' needs conductor_surfaces in the problem definition")
    if len(faces) > MAX_SIBC:
        raise ValueError(f"{len(faces)} SIBC surfaces, at most {MAX_SIBC} supported")
    sigma = float(params.get("sigmaCond", DEFAULT_SIGMA))
    if not sigma > 0:
        raise ValueError(f"sigmaCond {sigma}: must be > 0")
    return "sibc", sigma, {n: float(v) for n, v in faces.items()}


def conductor_volume(model: str, sigma: float | None, f_ghz: float, phys: dict) -> dict:
    """Volume conductor slot {label_tag, sigma, rel} (rel = sigma/(omega eps0)
    at f_ghz) for conductorModel 'volume'; label -1 otherwise. The mesh volume
    Conductor must exist exactly for that model."""
    tag = phys.get((3, CONDUCTOR_VOLUME))
    if model != "volume":
        if tag is not None:
            raise RuntimeError(f"mesh has the volume {CONDUCTOR_VOLUME} but conductorModel is {model!r} "
                               "(use 'volume')")
        return dict(label_tag=-1, sigma=0.0, rel=0.0)
    if tag is None:
        raise RuntimeError(f"conductorModel 'volume' needs the mesh volume {CONDUCTOR_VOLUME}")
    return dict(label_tag=int(tag), sigma=sigma, rel=sigma / (2 * math.pi * f_ghz * 1e9 * EPS0))


def sibc_list(faces: dict, phys: dict) -> list:
    """SIBC slots [{label, label_tag, factor}] in the order of conductor_surfaces."""
    out = []
    for name, factor in faces.items():
        tag = phys.get((2, name))
        if tag is None:
            raise RuntimeError(f"SIBC surface {name} missing from the mesh physical groups")
        out.append(dict(label=name, label_tag=int(tag), factor=factor))
    return out


def substrate_list(params: dict, phys: dict) -> list:
    """Dielectric slots [{name, label_tag, eps, tan_delta}] of the mesh volumes
    Substrate, Substrate2..4 present in phys (SUBSTRATE_SLOTS); an absent
    volume gives an unused slot (label -1). Substrate defaults to eps 1 and
    loss 0 as before; the further regions need their parameters."""
    out = []
    for name, eps_key, td_key in SUBSTRATE_SLOTS:
        tag = phys.get((3, name))
        if tag is None:
            out.append(dict(name=name, label_tag=-1, eps=1.0, tan_delta=0.0))
            continue
        if name != "Substrate" and eps_key not in params:
            raise ValueError(f"volume {name} in the mesh but no {eps_key} in the parameter set")
        out.append(dict(name=name, label_tag=int(tag), eps=float(params.get(eps_key, 1.0)),
                        tan_delta=float(params.get(td_key, 0.0))))
    return out


def port_list(pdef: dict, params: dict, phys: dict) -> list:
    """Lumped ports of a problem (settings 3.3) in JSON order, with the mesh
    face tag of each port label."""
    out = []
    for p in pdef.get("ports", []):
        tag = phys.get((2, p["label"]))
        if tag is None:
            raise RuntimeError(f"port face {p['label']} missing from the mesh physical groups")
        out.append(dict(label=p["label"], label_tag=int(tag),
                        width=eval_param(p["width"], params), height=eval_param(p["height"], params),
                        R=float(p.get("R", 50.0)), direction=[float(v) for v in p["direction"]]))
    return out


def build_pcb_runtime_config(problem: str, pset: str, params: dict, phys: dict, mesh: Path,
                             src: dict, a, rtol: float, max_it: int,
                             accel_ic_alpha: float = rfb.DEFAULT_ACCEL_IC_ALPHA,
                             not_pec: tuple = (), sol_save_file: str = "",
                             sol_ref_file: str = "") -> str:
    """runtime_case_config.idp for a PCB case. Same variables as
    rfb.build_runtime_config (checked by runtime_config_names_match), with the
    PCB label names, mm units (k0 in 1/mm) and the port-substitute source.
    The GMRES restart length is a.gmres_restart (preset_namespace). Surfaces
    named in not_pec (SIBC conductors) are left out of the PEC labels."""
    vol = {name: tag for (dim, name), tag in phys.items() if dim == 3}
    sur = {name: tag for (dim, name), tag in phys.items() if dim == 2}
    pec = [sur[n] for n in PCB_PEC_NAMES if n in sur and n not in not_pec][:8]
    sm = [sur[n] for n in PCB_SM_NAMES if n in sur][:4]
    use_sm = 1 if sm else 0
    pec += [-1] * (8 - len(pec))
    sm += [-1] * (4 - len(sm))
    f_ghz = float(params["freqGHz"])
    lambda0 = C0_MM_GHZ / f_ghz
    k0 = 2.0 * math.pi / lambda0
    unused = ["CoreAir", "SphereDielectric", "Layer2_CeramicOrHighK", "PTFE", "Alumina", "Eps1",
              "Eps100", "RodsHighEps", "LossyMaterial", "Lossy", "HighK"]
    unused_vars = ["labCoreAir", "labSphereDielectric", "labLayer2", "labPTFE", "labAlumina",
                   "labEps1", "labEps100", "labRodsHighEps", "labLossyMaterial", "labLossy",
                   "labHighK"]
    clash = [n for n in unused if n in vol]
    if clash:
        raise RuntimeError(f"PCB mesh uses region names of the existing benchmark: {clash}")
    cx, cy, cz = src["center"]
    lines = [
        "// Auto-generated by run_pcb_benchmark.py (PCB case; lengths in mm)",
        f"string caseName = \"{problem}\";",
        f"string paramSetName = \"{pset}\";",
        f"string meshFile = \"{mesh.as_posix()}\";",
        "",
        f"string backend = \"{a.backend}\";",
        f"string petscOptions = \"{a.petsc_options}\";",
        "",
        f"string outerMethod = \"{a.outer_method}\";",
        f"string krylovMethod = \"{a.krylov}\";",
        f"real cslpBeta1 = {rfb.DEFAULT_CSLP_BETA1};",
        f"real cslpBeta2 = {rfb.DEFAULT_CSLP_BETA2};",
        f"real outerRtol = {rtol};",
        f"int outerMaxIt = {max_it};",
        f"real accelIcAlpha = {accel_ic_alpha};",
        f"real hxSmootherOmega = {rfb.DEFAULT_HX_SMOOTHER_OMEGA};",
        f"int gmresRestartCfg = {a.gmres_restart};",
        "",
        f"real lambda0 = {lambda0!r};   // mm, f = {f_ghz} GHz",
        f"real k0 = {k0!r};   // 1/mm",
        "",
        "int usePML = 0;",
        f"int useSM = {use_sm};",
        "real pmlThick = 1.0;",
        "real pmlSigmaMax = 0.0;",
        "real pmlXmin = 0.0; real pmlXmax = 0.0;",
        "real pmlYmin = 0.0; real pmlYmax = 0.0;",
        "real pmlZmin = 0.0; real pmlZmax = 0.0;",
        "",
        "real srcAmp = 1.0;",
        f"real srcX0 = {cx!r};",
        f"real srcY0 = {cy!r};",
        f"real srcZ0 = {cz!r};",
        f"real srcWidth = {src['width']!r};",
        "",
        "int saveVtk = 0;",
        "string vtkOutReal = \"E_real.vtu\";",
        "string vtkOutImag = \"E_imag.vtu\";",
        "",
        "real epsSphere = 1.0;",
        "real kappa = 1.0;",
        "real epsPTFE = 2.1;",
        "real epsAlumina = 9.8;",
        "real epsRods = 1.0;",
        "real epsLossy = 1.0;",
        "real tanDelta = 0.0;",
        "real vloss = 0.0;",
        "",
    ]
    lines += [f"int {v} = -1;" for v in unused_vars]
    lines += [""]
    lines += [f"int labPML{s} = -1;" for s in ("XP", "XM", "YP", "YM", "ZP", "ZM")]
    lines += [""]
    lines += [f"int pecLabel{i + 1} = {t};" for i, t in enumerate(pec)]
    lines += [""]
    lines += [f"int smLabel{i + 1} = {t};" for i, t in enumerate(sm)]
    lines += ["", "// Solution save / error against a reference (solution_check.idp; '' = off)",
              f"string solSaveFile = \"{sol_save_file}\";",
              f"string solRefFile = \"{sol_ref_file}\";", ""]
    return "\n".join(lines)


DECL_RE = re.compile(r"^\s*(?:int|real|string)\s+(\w+)\s*=", re.MULTILINE)


def declared_names(cfg: str) -> set:
    """Variables declared in a runtime_case_config.idp text (several per line allowed)."""
    names = set()
    for line in cfg.splitlines():
        for part in line.split(";"):
            m = DECL_RE.match(part)
            if m:
                names.add(m.group(1))
    return names


def runtime_config_names_match() -> tuple:
    """(missing, extra) variables of the PCB runtime config against the one
    rfb.build_runtime_config writes for the existing benchmark."""
    a = preset_namespace("ssor", "gmres", 10)
    task = rfb.MeshTask(case_name="case2A", param_set="standard", mesh_path=Path("x.msh"))
    ref = rfb.build_runtime_config(task=task, params={}, phys={}, abc_mode="auto", backend=a.backend,
                                   petsc_options=a.petsc_options, save_vtk=False, result_dir=Path("."),
                                   outer_method=a.outer_method, krylov_method="gmres")
    src = dict(center=[0.0, 0.0, 0.0], width=1.0)
    new = build_pcb_runtime_config("P", "p", {"freqGHz": 1.0}, {}, Path("x.msh"), src, a, 1e-8, 10)
    r, n = declared_names(ref), declared_names(new)
    return sorted(r - n), sorted(n - r)


TAG_RE = re.compile(r"^[A-Za-z0-9_.+-]+$")


def uses_gmres(combo: str) -> bool:
    """GMRES outer iteration (PETSc KSP or hand-rolled gmres_precon.idp)."""
    return combo != DIRECT_COMBO and combo.split("/")[1] == "gmres"


def uses_accel_ic(combo: str) -> bool:
    return combo.split("/")[0] == "accel_ic"


def sensitivity_problem(combos: list, gmres_restart: int, accel_ic_alpha: float, tag: str) -> str | None:
    """Why --gmres-restart/--accel-ic-alpha cannot be used with these
    combinations, or None. Non-default values need --tag (results named
    <set>@<tag>) and must affect every selected combination, so that no
    result under the tag merely repeats a standard run."""
    if gmres_restart != rfb.DEFAULT_GMRES_RESTART:
        if gmres_restart < 1:
            return f"--gmres-restart {gmres_restart}: must be >= 1"
        if not tag:
            return "--gmres-restart other than the default needs --tag (results would overwrite the standard runs)"
        bad = [c for c in combos if not uses_gmres(c)]
        if bad:
            return f"--gmres-restart applies to GMRES combinations only; not to {', '.join(bad)}"
    if accel_ic_alpha != rfb.DEFAULT_ACCEL_IC_ALPHA:
        if not accel_ic_alpha > 0:
            return f"--accel-ic-alpha {accel_ic_alpha}: must be > 0"
        if not tag:
            return "--accel-ic-alpha other than the default needs --tag (results would overwrite the standard runs)"
        bad = [c for c in combos if not uses_accel_ic(c)]
        if bad:
            return f"--accel-ic-alpha applies to accel_ic combinations only; not to {', '.join(bad)}"
    return None


HX_MASK_COMBOS = ("hx/gmres", "cslp_hx/gmres")


# PCB standard for HX / CSLP+HX (handoff task I-9, settings 8.2): the gradient
# correction is masked on the on() penalty rows of PEC (hxDirichletMask = 1 in
# pcb_case_config.idp), i.e. the HX correction of the space constrained on PEC.
# Unmasked, the penalty rows leave an O(|r|) term in A*M^-1 that the smoother
# cannot correct (task I-8: the masked HX / CSLP+HX need about as few
# iterations as with SIBC, where the conductor edges are ordinary unknowns).
# Not applied by regress (the fork check compares with ../hx_precon.idp and
# ../cslp_hx_precon.idp, which have no mask); --no-hx-mask switches it off.
PCB_HX_DIRICHLET_MASK = True


# PCB standard HX form (docs/paper_plan.md A1, decided 2026-10-05): (vector term,
# smoother 0 Jacobi / 1 symmetric Gauss-Seidel) per combination. hx/gmres adds the
# vector term Pi^T (A + 2k0^2 Meps) Pi (pcb_hx_vec.idp) and one SGS sweep (Core 9/9
# converged, the 2-term form stalls on P03); cslp_hx/gmres keeps the 2-term form
# (the vector term gave no gain). --mrhs keeps the 2-term form (the vector term is
# not checked there). Not applied by regress (the fork check compares with the
# 2-term ../hx_precon.idp); --hx-vec / --hx-smoother override it (with --tag).
HX_STANDARD = {"hx/gmres": (2, 1), "cslp_hx/gmres": (0, 0)}


def hx_variant_problem(combos: list, args) -> str | None:
    """Why --hx-vec / --hx-smoother cannot be used here, or None (docs/paper_plan.md A1)."""
    vec, sm = args.hx_vec, args.hx_smoother
    if vec is None and sm is None and not args.hx_vec_options:
        return None
    if not args.tag:
        return "--hx-vec / --hx-smoother / --hx-vec-options need --tag (results would overwrite the standard runs)"
    bad = [c for c in combos if c not in HX_MASK_COMBOS]
    if bad:
        return f"--hx-vec / --hx-smoother apply to {', '.join(HX_MASK_COMBOS)} only; not to {', '.join(bad)}"
    if sm is not None and combos != ["hx/gmres"]:
        return "--hx-smoother applies to hx/gmres only"
    if vec == 3 and combos != ["cslp_hx/gmres"]:
        return "--hx-vec 3 (CSLP-shifted operator) applies to cslp_hx/gmres only"
    if args.mrhs:
        return "--hx-vec / --hx-smoother with --mrhs are not supported"
    return None


def hx_mask_problem(combos: list, no_hx_mask: bool, tag: str) -> str | None:
    """Why --no-hx-mask cannot be used with these combinations, or None."""
    if not no_hx_mask:
        return None
    if not tag:
        return "--no-hx-mask needs --tag (results would overwrite the standard runs)"
    bad = [c for c in combos if c not in HX_MASK_COMBOS]
    if bad:
        return f"--no-hx-mask applies to {', '.join(HX_MASK_COMBOS)} only; not to {', '.join(bad)}"
    return None


MRHS_METHODS = ("shared", "block", "gcro")
MRHS_RECYCLE, MRHS_RECYCLE_MAX = 20, 60   # gcro defaults (pcb_mrhs_seq.idp)


def mrhs_label(method: str, recycle: int = MRHS_RECYCLE, recycle_max: int = MRHS_RECYCLE_MAX) -> str:
    """Result-name part of a multiple-right-hand-side run: 'mrhs-shared',
    'mrhs-block', 'mrhs-gcro' (+ '-k<recycle>-<max>' for non-default sizes)."""
    lab = f"mrhs-{method}"
    if method == "gcro" and (recycle, recycle_max) != (MRHS_RECYCLE, MRHS_RECYCLE_MAX):
        lab += f"-k{recycle}-{recycle_max}"
    return lab


def mrhs_problem(combos: list, mrhs: str, port: str, excitation: str, recycle: int, recycle_max: int) -> str | None:
    """Why --mrhs cannot be used with these settings, or None. shared: any
    combination (the PETSc KSP ones solve the right-hand sides one after the
    other with the same KSP, e.g. one MUMPS factorization); block and gcro:
    the hand-rolled GMRES combinations (cslp, hx, cslp_hx, accel_ic)."""
    if not mrhs:
        return None
    if mrhs not in MRHS_METHODS:
        return f"--mrhs {mrhs}: use one of {', '.join(MRHS_METHODS)}"
    if port:
        return "--mrhs solves every port in one process; do not give --port"
    if excitation != "E2":
        return "--mrhs needs the E2 excitation"
    if mrhs == "gcro" and not (0 < recycle <= recycle_max):
        return f"--mrhs-recycle {recycle} / --mrhs-recycle-max {recycle_max}: need 0 < recycle <= max"
    if mrhs in ("block", "gcro"):
        bad = [c for c in combos if c == DIRECT_COMBO or c.split("/")[1] != "gmres"
               or preset_namespace(*c.split("/"), rb.NO_CAP).outer_method == "petsc"]
        if bad:
            return f"--mrhs {mrhs} needs a hand-rolled GMRES combination; not {', '.join(bad)}"
    return None


MRHS_DONE_RE = re.compile(r"MRHS_DONE (\d+) (-?\d+) (\S+) (\S+) (\d)")
MRHS_MV_RE = re.compile(r"MRHS_MATVECS (\d+)")
MRHS_RECYCLE_RE = re.compile(r"MRHS_RECYCLE (\d+) dim (\d+)")


def parse_mrhs(text: str) -> dict | None:
    """Per-right-hand-side results of a --mrhs run (None if not one)."""
    rows = [dict(port=int(m.group(1)), iterations=int(m.group(2)), time=float(m.group(3)),
                 true_relres=float(m.group(4)), converged=bool(int(m.group(5))))
            for m in MRHS_DONE_RE.finditer(text)]
    if not rows:
        return None
    mv = MRHS_MV_RE.search(text)
    rec = {int(m.group(1)): int(m.group(2)) for m in MRHS_RECYCLE_RE.finditer(text)}
    return dict(rhs=rows, matvecs=int(mv.group(1)) if mv else None, recycle_dim=rec or None)


def parse_freqs(text: str) -> list:
    """--freq 'GHz[,GHz...]' -> [float, ...] (distinct, > 0, in input order)."""
    out = []
    for t in (v.strip() for v in text.split(",")):
        if not t:
            continue
        try:
            f = float(t)
        except ValueError:
            raise ValueError(f"--freq {t}: not a number") from None
        if not (f > 0 and math.isfinite(f)):
            raise ValueError(f"--freq {t}: must be a positive number")
        if f in out:
            raise ValueError(f"--freq {t}: given twice")
        out.append(f)
    return out


def freq_label(f_ghz: float) -> str:
    """Result-name part of a swept frequency: 0.705 -> 'f0.705', 10.0 -> 'f10'."""
    return f"f{f_ghz:.6g}"


def petsc_extra_problem(combos: list, petsc_extra: str, tag: str) -> str | None:
    """Why --petsc-extra/--tag cannot be used with these combinations, or None."""
    if tag and not TAG_RE.match(tag):
        return f"--tag {tag!r}: use letters, digits and _ . + - only"
    if not petsc_extra:
        return None
    if '"' in petsc_extra or "\\" in petsc_extra:
        return "--petsc-extra must not contain quotes or backslashes (FreeFEM string literal)"
    if not tag:
        return "--petsc-extra needs --tag (results would overwrite the standard runs)"
    bad = [c for c in combos if preset_namespace(*c.split("/"), rb.NO_CAP).outer_method != "petsc"]
    if bad:
        return (f"--petsc-extra applies to PETSc-KSP combinations only (outerMethod petsc); "
                f"not to {', '.join(bad)}")
    return None


class PcbJob:
    """One PCB solve: problem, parameter set, excited port; optionally extra
    PETSc options (diagnostic variants, appended to the options of the PETSc
    KSP, so they override the preset's) under a result tag."""

    def __init__(self, problem: str, pset: str, pdef: dict, params: dict, mesh_dir: Path, port: str,
                 excitation: str = "E2", petsc_extra: str = "", tag: str = "",
                 gmres_restart: int = rfb.DEFAULT_GMRES_RESTART,
                 accel_ic_alpha: float = rfb.DEFAULT_ACCEL_IC_ALPHA, freq_ghz: float | None = None,
                 hx_mask: bool = PCB_HX_DIRICHLET_MASK, mrhs: str = "", mrhs_recycle: int = 20,
                 mrhs_recycle_max: int = 60):
        self.problem, self.pset, self.pdef = problem, pset, pdef
        # multiple right-hand sides (pcb_mrhs.idp): every port in one process
        self.mrhs, self.mrhs_recycle, self.mrhs_recycle_max = mrhs, mrhs_recycle, mrhs_recycle_max
        # freq_ghz (--freq): the parameter set solved at another frequency on
        # its own mesh (the mesh file is named after the set, not the frequency).
        self.freq_param_set = float(params["freqGHz"])
        self.freq_override = freq_ghz is not None
        self.params = dict(params, freqGHz=freq_ghz) if self.freq_override else params
        self.excitation = excitation
        self.petsc_extra, self.tag = petsc_extra.strip(), tag
        self.gmres_restart, self.accel_ic_alpha = gmres_restart, accel_ic_alpha
        self.hx_mask = bool(hx_mask)
        # HX vector term / smoother (--hx-vec, --hx-smoother; set by select_jobs;
        # None: HX_STANDARD of the combination, see hx_form)
        self.hx_vec, self.hx_smoother, self.hx_vec_options = None, None, ""
        # iteration cap rule (--k-max; set by select_pcb_jobs): standard, none or a number
        self.k_max_spec = "none"
        # Conductor model (settings 3.4): SIBC faces and Z_s at the solve frequency.
        self.conductor, self.sigma, self.sibc_faces = conductor_model(pdef, self.params)
        self.zs = surface_impedance(float(self.params["freqGHz"]), self.sigma) \
            if self.conductor == "sibc" else None
        self.mesh = mesh_dir / f"{pset}.msh"
        self.src = port_source(pdef, params, port or pdef["ports"][0]["label"])
        self.excited_index = 1 + [p["label"] for p in pdef["ports"]].index(self.src["port"])
        # Result/log name: the parameter set, plus "@<port>" when a port other
        # than the first is excited, "@E1" for the port-substitute source,
        # "@f<GHz>" for a swept frequency and "@<tag>" for a tagged
        # (diagnostic or sensitivity) variant.
        self.key = pset + ("" if self.excited_index == 1 else f"@{self.src['port']}") \
            + ("" if excitation == "E2" else f"@{excitation}") \
            + (f"@{freq_label(freq_ghz)}" if self.freq_override else "") \
            + (f"@{mrhs_label(mrhs, mrhs_recycle, mrhs_recycle_max)}" if mrhs else "") + (f"@{tag}" if tag else "")
        self.task = rfb.MeshTask(case_name=problem, param_set=self.key, mesh_path=self.mesh)

    def hx_form(self, combo: str) -> tuple:
        """(vector term, smoother 0 Jacobi / 1 SGS) of combo: --hx-vec / --hx-smoother
        when given, else HX_STANDARD (the 2-term form with --mrhs); (0, 0) for non-HX."""
        vec, sm = (0, 0) if self.mrhs else HX_STANDARD.get(combo, (0, 0))
        vec = vec if self.hx_vec is None else self.hx_vec
        sm = sm if self.hx_smoother is None else self.hx_smoother
        return (vec if combo in HX_MASK_COMBOS else 0, sm if combo == "hx/gmres" else 0)

    def configs(self, preset: str, krylov: str, rtol: float, phys: dict | None = None,
                sol_save_file: str = "", sol_ref_file: str = "", ritz: dict | None = None) -> tuple:
        """(runtime_case_config.idp, pcb_case_config.idp) texts.
        E2: all ports carry their resistor, the excited one also the 1 A
        Norton current. E1: port-substitute volume source, no port terms.
        ritz: Ritz probe instead of the solve (cmd_ritz): steps, start, seed and
        petsc_options (the probe's fixed preconditioner options)."""
        combo = f"{preset}/{krylov}"
        cap = rb.NO_CAP if ritz else (k_max_of(combo, self.k_max_spec) or rb.NO_CAP)
        a = preset_namespace(preset, krylov, cap, self.gmres_restart)
        if ritz:
            a.petsc_options = ritz["petsc_options"]
        if rtol != 1e-8 and a.outer_method == "petsc":   # as run_benchmark.build_job_dir
            a.petsc_options = re.sub(r"-ksp_rtol \S+", f"-ksp_rtol {rtol}", a.petsc_options, count=1)
        if pcb_standard_extra(a):
            a.petsc_options = f"{a.petsc_options} {pcb_standard_extra(a)}"
        if self.petsc_extra:
            if a.outer_method != "petsc":
                raise ValueError(f"--petsc-extra with {preset}/{krylov} (outerMethod {a.outer_method})")
            a.petsc_options = f"{a.petsc_options} {self.petsc_extra}"
        if phys is None:
            phys = expected_physical(self.pdef)
            opt = self.pdef.get("physical_groups", {}).get("volumes_optional", {})
            if self.conductor == "volume" and CONDUCTOR_VOLUME in opt:
                phys[(3, CONDUCTOR_VOLUME)] = int(opt[CONDUCTOR_VOLUME])
        runtime = build_pcb_runtime_config(self.problem, self.pset, self.params, phys, self.mesh,
                                           self.src, a, rtol, cap, self.accel_ic_alpha,
                                           not_pec=tuple(self.sibc_faces), sol_save_file=sol_save_file,
                                           sol_ref_file=sol_ref_file)
        e2 = self.excitation == "E2"
        hx_vec, hx_sm = self.hx_form(combo)
        cond = conductor_volume(self.conductor, self.sigma, float(self.params["freqGHz"]), phys)
        pcb = pcb_case_config(excitation=self.excitation, src_dir=tuple(self.src["direction"]),
                              substrates=substrate_list(self.params, phys),
                              ports=port_list(self.pdef, self.params, phys) if e2 else [],
                              excited_port=self.excited_index if e2 else 0, pcb_diag=1,
                              sibc=sibc_list(self.sibc_faces, phys),
                              sibc_zs=self.zs if self.zs is not None else 1.0,
                              hx_dirichlet_mask=int(self.hx_mask and combo in HX_MASK_COMBOS),
                              hx_vec_term=hx_vec, hx_smoother=hx_sm,
                              hx_vec_options=self.hx_vec_options,
                              npatch_type=NPATCH_PRESETS.get(preset, 0),
                              mrhs_method=self.mrhs, mrhs_recycle=self.mrhs_recycle,
                              mrhs_recycle_max=self.mrhs_recycle_max, cond_label=cond["label_tag"],
                              cond_sigma=cond["sigma"], cond_rel=cond["rel"],
                              **(dict(ritz_steps=ritz["steps"], ritz_start=ritz["start"],
                                      ritz_seed=ritz["seed"]) if ritz else {}))
        return runtime, pcb


class ExistingJob:
    """One solve of a parameter set of the existing benchmark (case1A-3F,
    gmsh_templates/case_parameters.json) with the PCB solver and the PCB
    standard (docs/paper_plan.md A2): the job directory is built as regress
    does (rfb.build_runtime_config, lengths normalised by lambda0, Gaussian
    volume source), plus the PCB-standard settings of run (MGS for PETSc's
    GMRES, HX mask and HX_STANDARD, node patch, K_max). Selected as
    <case>:<set> (e.g. case2A:standard); results are named as run_benchmark.py
    names them (<case>_<set>__<preset>_<krylov>)."""
    existing = True
    excitation = "gaussian_volume_source"
    mrhs = ""

    def __init__(self, case: str, pset: str, params: dict, mesh_dir: Path, petsc_extra: str = "",
                 tag: str = "", gmres_restart: int = rfb.DEFAULT_GMRES_RESTART,
                 accel_ic_alpha: float = rfb.DEFAULT_ACCEL_IC_ALPHA, hx_mask: bool = PCB_HX_DIRICHLET_MASK):
        self.problem, self.params = case, params
        self.pset = f"{case}:{pset}"       # as --sets names it
        self.set_name = pset
        self.petsc_extra, self.tag = petsc_extra.strip(), tag
        self.gmres_restart, self.accel_ic_alpha = gmres_restart, accel_ic_alpha
        self.hx_mask = bool(hx_mask)
        self.hx_vec, self.hx_smoother, self.hx_vec_options = None, None, ""
        self.k_max_spec = "none"
        self.mesh = mesh_dir / f"{case}_{pset}.msh"
        self.key = pset + (f"@{tag}" if tag else "")
        self.src = dict(port="-")
        self.task = rfb.MeshTask(case_name=case, param_set=self.key, mesh_path=self.mesh)

    hx_form = PcbJob.hx_form

    def configs(self, preset: str, krylov: str, rtol: float, phys: dict | None = None,
                sol_save_file: str = "", sol_ref_file: str = "", work: Path | None = None,
                ritz: dict | None = None) -> tuple:
        """(runtime_case_config.idp, pcb_case_config.idp) texts; phys from the mesh
        (needed: the existing cases have no physical-group list in the JSON).
        ritz: Ritz probe instead of the solve, as PcbJob.configs."""
        combo = f"{preset}/{krylov}"
        cap = rb.NO_CAP if ritz else (k_max_of(combo, self.k_max_spec) or rb.NO_CAP)
        a = preset_namespace(preset, krylov, cap, self.gmres_restart)
        if ritz:
            a.petsc_options = ritz["petsc_options"]
        if rtol != 1e-8 and a.outer_method == "petsc":
            a.petsc_options = re.sub(r"-ksp_rtol \S+", f"-ksp_rtol {rtol}", a.petsc_options, count=1)
        if pcb_standard_extra(a):
            a.petsc_options = f"{a.petsc_options} {pcb_standard_extra(a)}"
        if self.petsc_extra:
            if a.outer_method != "petsc":
                raise ValueError(f"--petsc-extra with {combo} (outerMethod {a.outer_method})")
            a.petsc_options = f"{a.petsc_options} {self.petsc_extra}"
        if phys is None:
            phys = rfb.parse_physical_names(self.mesh)
        runtime = rfb.build_runtime_config(
            task=self.task, params=self.params, phys=phys, abc_mode="auto", backend=a.backend,
            petsc_options=a.petsc_options, save_vtk=False, result_dir=work or Path("."),
            outer_method=a.outer_method, outer_rtol=rtol, outer_max_it=cap, krylov_method=krylov,
            accel_ic_alpha=self.accel_ic_alpha, gmres_restart=a.gmres_restart,
            sol_save_file=sol_save_file, sol_ref_file=sol_ref_file)
        hx_vec, hx_sm = self.hx_form(combo)
        pcb = pcb_case_config(hx_dirichlet_mask=int(self.hx_mask and combo in HX_MASK_COMBOS),
                              hx_vec_term=hx_vec, hx_smoother=hx_sm, hx_vec_options=self.hx_vec_options,
                              npatch_type=NPATCH_PRESETS.get(preset, 0),
                              **(dict(ritz_steps=ritz["steps"], ritz_start=ritz["start"],
                                      ritz_seed=ritz["seed"]) if ritz else {}))
        return runtime, pcb


def existing_record_fields(job: ExistingJob, combo: str, log_path: Path) -> dict:
    """The "pcb" field of an existing-benchmark result (as pcb_record_fields)."""
    version = None
    if log_path.exists():
        m = re.search(r"PCB_SOLVER_VERSION = (\S+)", log_path.read_text(encoding="utf-8", errors="ignore"))
        version = m.group(1) if m else None
    hx_vec, hx_sm = job.hx_form(combo)
    return dict(
        solver_version=version, benchmark="existing", suite=job.params.get("suite"),
        mesh=job.mesh.relative_to(ROOT).as_posix() if job.mesh.is_relative_to(ROOT) else str(job.mesh),
        # lengths normalised by the free-space wavelength (lambda0 = 1), Gaussian volume source
        length_unit="lambda0", excitation=job.excitation, k0=rfb.pick_k0(job.problem, job.params),
        petsc_pcb_standard=pcb_standard_extra(preset_namespace(*combo.split("/"), rb.NO_CAP)) or None,
        tag=job.tag or None, petsc_extra=job.petsc_extra or None,
        gmres_restart=job.gmres_restart if uses_gmres(combo) else None,
        accel_ic_alpha=job.accel_ic_alpha if uses_accel_ic(combo) else None,
        hx_dirichlet_mask=job.hx_mask if combo in HX_MASK_COMBOS else None,
        hx_vec_term=hx_vec if combo in HX_MASK_COMBOS else None,
        hx_smoother=(("jacobi", "sgs")[hx_sm]) if combo == "hx/gmres" else None,
        hx_vec_options=job.hx_vec_options or None if hx_vec else None,
    )


def load_existing_cases() -> dict:
    return rfb.load_case_params()


# Entry point started by run_benchmark.run_job in the job directory.
LAUNCHER = """// Launcher written by run_pcb_benchmark.py: run_benchmark.run_job starts
// maxwell_edge03d_solver.edp; in a PCB job directory that name runs the PCB solver.
include "maxwell_pcb_solver.edp"
"""


def make_pcb_build_job_dir(jobs: dict):
    """A replacement for run_benchmark.build_job_dir (same signature) that
    writes a PCB job directory; jobs maps (problem, param set) -> PcbJob."""
    def build(work: Path, task: rfb.MeshTask, case_db: dict, preset: str, krylov: str,
              rtol: float, sol_save_file: str = "", sol_ref_file: str = "") -> None:
        job = jobs[(task.case_name, task.param_set)]
        existing = getattr(job, "existing", False)
        phys = rfb.parse_physical_names(task.mesh_path) if existing else check_mesh_physical(job.pdef, task.mesh_path)
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        for d in (FREEFEM_DIR, PCB_DIR):   # pcb/ overrides same names
            for f in d.iterdir():
                if f.suffix in (".edp", ".idp") and f.name != "runtime_case_config.idp":
                    shutil.copy(f, work / f.name)
        if existing:
            runtime, pcb = job.configs(preset, krylov, rtol, phys, sol_save_file, sol_ref_file, work=work)
        else:
            runtime, pcb = job.configs(preset, krylov, rtol, phys, sol_save_file, sol_ref_file)
        (work / "runtime_case_config.idp").write_text(runtime, encoding="utf-8")
        (work / "pcb_case_config.idp").write_text(pcb, encoding="utf-8")
        (work / REF_SOLVER).write_text(LAUNCHER, encoding="utf-8")
    return build


PORT_V_RE = re.compile(r"PORT_V (\d+) (-?\d+) (\S+) (\S+) area (\S+)")
PORT_S_RE = re.compile(r"PORT_S (\d+) (\d+) (\S+) (\S+)")
PEC_RE = re.compile(r"PEC_CHECK (\d+) area (\S+) rmsEt (\S+) rmsE (\S+)")
SIBC_RE = re.compile(r"SIBC_CHECK (\d+) factor (\S+) area (\S+) rmsEt (\S+) power (\S+)")
COND_RE = re.compile(r"COND_CHECK (\d+) sigma (\S+) volume (\S+) power (\S+)")
# -ksp_monitor_true_residual (log lines carry run_job's time stamp first)
TRUE_RES_RE = re.compile(r"^\s*\S+\s+(\d+) KSP \w+ resid norm (\S+) true resid norm (\S+)", re.MULTILINE)


def parse_true_residual(text: str) -> list | None:
    """[[iteration, monitored residual, true residual], ...] relative to the
    first true residual (PETSc -ksp_monitor_true_residual), <= 3000 rows with
    the last one; None without such lines. For right-preconditioned GMRES the
    monitored residual is the GMRES estimate |g_{j+1}| and the true one is
    ||b - A x_j|| of the solution built at that iteration."""
    rows = [(int(m.group(1)), float(m.group(2)), float(m.group(3))) for m in TRUE_RES_RE.finditer(text)]
    if not rows or rows[0][2] == 0.0:
        return None
    r0 = rows[0][2]
    rel = [[i, est / r0, tr / r0] for i, est, tr in rows]
    step = max(1, len(rel) // 3000)
    return rel[::step] + ([rel[-1]] if (len(rel) - 1) % step else [])


def s_name(i: int, j: int) -> str:
    """Name of S_ij (1-based): 'S21' while both indices are single digits,
    'S12_3' style ('S<i>_<j>') otherwise, so that names stay unambiguous with
    up to 16 ports."""
    return f"S{i}{j}" if i < 10 and j < 10 else f"S{i}_{j}"


def parse_port_output(text: str, job: PcbJob) -> dict | None:
    """Port voltages [V], S-parameters (column of the excited port) and the
    PEC check from the solver log; None if the solver printed no port lines."""
    names = [p["label"] for p in job.pdef.get("ports", [])]
    volt, s_par, pec, sibc = {}, {}, {}, {}
    for m in PORT_V_RE.finditer(text):
        i = int(m.group(1))
        volt[names[i - 1]] = dict(re=float(m.group(3)), im=float(m.group(4)), area=float(m.group(5)))
    for m in PORT_S_RE.finditer(text):
        i, j = int(m.group(1)), int(m.group(2))
        s_par[s_name(i, j)] = [float(m.group(3)), float(m.group(4))]
    for m in PEC_RE.finditer(text):
        pec[m.group(1)] = dict(area=float(m.group(2)), rms_Et=float(m.group(3)), rms_E=float(m.group(4)))
    for m in SIBC_RE.finditer(text):
        sibc[m.group(1)] = dict(factor=float(m.group(2)), area=float(m.group(3)),
                                rms_Et=float(m.group(4)), power_W=float(m.group(5)))
    extra = dict(sibc_check=sibc) if sibc else {}
    for m in COND_RE.finditer(text):
        extra["conductor_check"] = dict(label=int(m.group(1)), sigma=float(m.group(2)),
                                        volume=float(m.group(3)), power_W=float(m.group(4)))
    if not volt:
        return dict(pec_check=pec, **extra) if (pec or extra) else None
    return dict(voltage=volt, S=s_par, current_A=1.0, pec_check=pec, **extra)


def pcb_record_fields(job: PcbJob, combo: str, log_path: Path) -> dict:
    version, text = None, ""
    if log_path.exists():
        text = log_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"PCB_SOLVER_VERSION = (\S+)", text)
        version = m.group(1) if m else None
    f_ghz = float(job.params["freqGHz"])
    e2 = job.excitation == "E2"
    return dict(
        solver_version=version,
        role=job.params.get("role"),
        mesh=job.mesh.relative_to(ROOT).as_posix() if job.mesh.is_relative_to(ROOT) else str(job.mesh),
        freq_GHz=f_ghz, k0_per_mm=2.0 * math.pi * f_ghz / C0_MM_GHZ,
        # --freq: the parameter set's own frequency (its mesh was made for it)
        freq_GHz_param_set=job.freq_param_set if job.freq_override else None,
        eps_substrate=job.params.get("epsSub"), tan_delta=job.params.get("tanDelta"),
        # further dielectric regions (Substrate2..4) of the mesh: {name: [eps_r, tan_delta]}
        dielectric_regions={d["name"]: [d["eps"], d["tan_delta"]]
                            for d in substrate_list(job.params, rfb.parse_physical_names(job.mesh)
                                                    if job.mesh.exists() else expected_physical(job.pdef))[1:]
                            if d["label_tag"] >= 0} or None,
        # E2: lumped ports (settings 3.3); E1: port-substitute volume source (15.4)
        excitation="E2_lumped_port" if e2 else "E1_port_substitute",
        excited_port="all" if job.mrhs else job.src["port"],
        # conductor model (settings 3.4): 'pec', or 'sibc' with sigma [S/m], Z_s [Ohm], faces {name: n_f};
        # 'volume' (5.5 stage 4): the mesh volume Conductor with sigma, sigma/(omega eps0)
        conductor_model=job.conductor, sigma=job.sigma,
        Zs_ohm=[job.zs.real, job.zs.imag] if job.zs is not None else None,
        sigma_over_omega_eps0=job.sigma / (2 * math.pi * f_ghz * 1e9 * EPS0)
        if job.conductor == "volume" else None,
        sibc_surfaces=job.sibc_faces or None,
        source=None if e2 else job.src,
        ports=parse_port_output(text, job),
        petsc_pcb_standard=pcb_standard_extra(preset_namespace(*combo.split("/"), rb.NO_CAP)) or None,
        tag=job.tag or None, petsc_extra=job.petsc_extra or None,
        # restart length / acceleration factor in effect (None: not used by the combination)
        gmres_restart=job.gmres_restart if uses_gmres(combo) else None,
        accel_ic_alpha=job.accel_ic_alpha if uses_accel_ic(combo) else None,
        hx_dirichlet_mask=job.hx_mask if combo in HX_MASK_COMBOS else None,
        hx_vec_term=job.hx_form(combo)[0] if combo in HX_MASK_COMBOS else None,
        hx_smoother=(("jacobi", "sgs")[job.hx_form(combo)[1]]) if combo == "hx/gmres" else None,
        hx_vec_options=job.hx_vec_options or None if job.hx_form(combo)[0] else None,
        true_residual=parse_true_residual(text),
        # multiple right-hand sides (--mrhs): method, gcro sizes, per-port results
        mrhs=dict(method=job.mrhs, recycle=job.mrhs_recycle if job.mrhs == "gcro" else None,
                  recycle_max=job.mrhs_recycle_max if job.mrhs == "gcro" else None,
                  **(parse_mrhs(text) or {})) if job.mrhs else None,
    )


def parse_ports(text: str, pdef: dict) -> list:
    """--port 'Port1,Port3' / 'all' -> port labels of the problem ([None]: the
    first port, the default). Unknown labels are an error."""
    names = [p["label"] for p in pdef.get("ports", [])]
    want = [t.strip() for t in text.split(",") if t.strip()]
    if not want:
        return [None]
    if want == ["all"]:
        return names
    bad = [t for t in want if t not in names]
    if bad:
        raise ValueError(f"--port {','.join(bad)}: not a port of the problem (have {', '.join(names)})")
    return list(dict.fromkeys(want))


def select_existing_jobs(args: argparse.Namespace, problems: set, sets: set, suites: set) -> list:
    """ExistingJob of the existing benchmark's parameter sets selected by --sets
    (<case>:<set>), --suite ("suite" of the set) or --problems (case names);
    never by --roles alone (docs/paper_plan.md A2)."""
    db = load_existing_cases()
    want = {s for s in sets if ":" in s}
    unknown = [s for s in want if s.split(":", 1)[0] not in db
               or s.split(":", 1)[1] not in db[s.split(":", 1)[0]]["parameter_sets"]]
    if unknown:
        raise ValueError(f"--sets {','.join(sorted(unknown))}: not a parameter set of "
                         f"{rfb.CASE_PARAM_JSON.relative_to(ROOT).as_posix()}")
    jobs = []
    for case, cdef in db.items():
        for pset, params in cdef["parameter_sets"].items():
            if sets:
                if f"{case}:{pset}" not in want:
                    continue
            elif problems:
                if case not in problems or (suites and params.get("suite") not in suites):
                    continue
            elif not (suites and params.get("suite") in suites):
                continue
            jobs.append(ExistingJob(case, pset, params, args.existing_mesh_dir, args.petsc_extra, args.tag,
                                    args.gmres_restart, args.accel_ic_alpha, not args.no_hx_mask))
    if jobs:
        bad = [o for o, on in (("--port", args.port), ("--freq", args.freq), ("--mrhs", args.mrhs),
                               ("--excitation E1", args.excitation == "E1")) if on]
        if bad:
            raise ValueError(f"{', '.join(bad)}: not for the existing benchmark's sets "
                             f"({jobs[0].pset}, ...)")
    return jobs


def select_pcb_jobs(args: argparse.Namespace, cases: dict, include_existing: bool = False) -> list:
    problems = {s.strip() for s in args.problems.split(",") if s.strip()}
    sets = {s.strip() for s in args.sets.split(",") if s.strip()}
    suites = {s.strip() for s in args.suite.split(",") if s.strip()}
    bad = suites - set(SUITES)
    if bad:
        raise ValueError(f"--suite {','.join(sorted(bad))}: not a suite tier (have {', '.join(SUITES)})")
    roles = {s.strip() for s in args.roles.split(",") if s.strip()}
    jobs = []
    for prob, pdef in cases.items():
        if problems and prob not in problems:
            continue
        if sets and not {s for s in sets if ":" not in s}:
            continue
        for pset, params in pdef["parameter_sets"].items():
            if sets:
                if pset not in sets:
                    continue
            elif suites:
                tiers = {params.get("suite")} | ({"multi_rhs"} if "multiRhsBudgetPerPort" in params else set())
                if not tiers & suites:
                    continue
            elif roles and params.get("role") not in roles:
                continue
            for port in parse_ports(args.port, pdef):
                for f in args.freqs or [None]:
                    jobs.append(PcbJob(prob, pset, pdef, params, args.mesh_dir, port, args.excitation,
                                       args.petsc_extra, args.tag, args.gmres_restart, args.accel_ic_alpha,
                                       f, not args.no_hx_mask, args.mrhs, args.mrhs_recycle,
                                       args.mrhs_recycle_max))
    for j in jobs:
        j.hx_vec = getattr(args, "hx_vec", None)
        sm = getattr(args, "hx_smoother", None)
        j.hx_smoother = None if sm is None else int(sm == "sgs")
        j.hx_vec_options = getattr(args, "hx_vec_options", "")
        j.k_max_spec = getattr(args, "k_max", None) or "none"
    if include_existing:
        ex = select_existing_jobs(args, problems, sets, suites)
        for j in ex:
            j.hx_vec = getattr(args, "hx_vec", None)
            sm = getattr(args, "hx_smoother", None)
            j.hx_smoother = None if sm is None else int(sm == "sgs")
            j.hx_vec_options = getattr(args, "hx_vec_options", "")
            j.k_max_spec = getattr(args, "k_max", None) or "none"
        jobs += ex
    if getattr(args, "release_dir", None):
        use_release_meshes(jobs, args.release_dir)
    return jobs


def use_release_meshes(jobs: list, release_dir: Path) -> None:
    """--release-dir: every job reads the mesh of the released data,
    <release_dir>/<set>/mesh.msh (':' of the canonical sets as '_', as
    release_data.py names the folders). The file is the benchmark mesh itself
    (md5 of mesh_md5.txt), so the solve is the same; only its path changes."""
    for j in jobs:
        j.mesh = release_dir / j.pset.replace(":", "_") / "mesh.msh"
        j.task = rfb.MeshTask(case_name=j.task.case_name, param_set=j.task.param_set, mesh_path=j.mesh)


def reference_tags(job: PcbJob) -> list:
    """Job names of the mumps/direct solve whose saved solution is the
    reference of job (solution error check), in order of preference: the same
    result name, then without the tag (as summarize_pcb_benchmark.reference_key)."""
    p, k = DIRECT_COMBO.split("/")
    keys = [job.key]
    if job.tag and job.key.endswith(f"@{job.tag}"):
        keys.append(job.key[:-len(job.tag) - 1])
    return [f"{job.problem}_{key}__{p}_{k}" for key in keys]


def s_max_abs_diff(r: dict, ref_sol: Path) -> float | None:
    """max |S - S_ref| over the S-parameters of result r and of the direct solve
    whose saved solution is ref_sol (its result JSON in <dir>/runs)."""
    ref_json = ref_sol.parent.parent / "runs" / ref_sol.name.replace(".sol.gz", ".json")
    if not ref_json.exists():
        return None
    s = ((r.get("pcb") or {}).get("ports") or {}).get("S") or {}
    s_ref = ((json.loads(ref_json.read_text(encoding="utf-8")).get("pcb") or {}).get("ports") or {}).get("S") or {}
    common = [n for n in s if n in s_ref]
    if not common:
        return None
    return max(abs(complex(*s[n]) - complex(*s_ref[n])) for n in common)


def cmd_run(args: argparse.Namespace) -> int:
    missing, extra = runtime_config_names_match()
    if missing or extra:
        print(f"ERROR: PCB runtime config out of sync with run_freefem_batch.build_runtime_config: "
              f"missing {missing}, extra {extra}")
        return 2
    cases = load_pcb_cases()
    # stopping rule (paper_plan 4.1): K_max per combination and a safety time
    # limit; --mrhs keeps the time budget (multi-RHS is not in the v1.0 records)
    if args.k_max is None:
        args.k_max = "none" if args.mrhs else "standard"
    if args.budget is None:
        args.budget = LEGACY_BUDGET if args.k_max == "none" else SAFETY_TIME_LIMIT
    try:
        args.freqs = parse_freqs(args.freq)
    except ValueError as e:
        print(f"ERROR: {e}")
        return 2
    if args.show_config and not args.sets and args.show_config.count(":") == 2:
        args.sets = args.show_config.rsplit(":", 1)[0]   # an existing set, e.g. case2A:standard:ssor/gmres
    try:
        jobs = select_pcb_jobs(args, cases, include_existing=True)
    except (ValueError, KeyError) as e:
        print(f"ERROR: {e}")
        return 2
    combos = [c.strip() for c in args.combos.split(",") if c.strip()]
    for c in combos:
        why = pcb_combo_problem(c)
        if why:
            print(f"ERROR: {why}")
            return 2
    err = (k_max_problem(args.k_max, args.tag, args.mrhs)
           or petsc_extra_problem(combos, args.petsc_extra, args.tag)
           or sensitivity_problem(combos, args.gmres_restart, args.accel_ic_alpha, args.tag)
           or hx_mask_problem(combos, args.no_hx_mask, args.tag)
           or hx_variant_problem(combos, args)
           or mrhs_problem(combos, args.mrhs, args.port, args.excitation, args.mrhs_recycle,
                           args.mrhs_recycle_max))
    if not err and args.mrhs and (args.save_solutions or args.ref_solutions):
        err = "--save-solutions / --ref-solutions need a single right-hand side (not --mrhs)"
    if err:
        print(f"ERROR: {err}")
        return 2

    if args.show_config:
        key, combo = args.show_config.rsplit(":", 1)
        job = next((j for j in jobs if key in (j.pset, j.key)), None)
        if job is None:
            print(f"ERROR: parameter set {key} not selected")
            return 2
        preset, krylov = combo.split("/")
        if getattr(job, "existing", False):
            if not job.mesh.exists():
                print(f"ERROR: {job.pset}: no mesh {job.mesh} (the existing cases need their mesh: "
                      "python3 gmsh_templates/generate_all_meshes.py -o generated_meshes)")
                return 2
            phys = rfb.parse_physical_names(job.mesh)
        else:
            phys = check_mesh_physical(job.pdef, job.mesh) if job.mesh.exists() else None
        runtime, pcb = job.configs(preset, krylov, args.rtol, phys)
        print(f"// ===== runtime_case_config.idp ({'mesh' if phys else 'JSON'} physical tags)")
        print(runtime)
        print("// ===== pcb_case_config.idp")
        print(pcb)
        return 0

    runs_dir = args.out / "runs"

    def tag(j, c):
        p, k = c.split("/")
        return f"{j.problem}_{j.key}__{p}_{k}"
    pairs = [(j, c) for c in combos for j in jobs]   # combo-major, as run_benchmark.py
    todo = [(j, c) for j, c in pairs if args.force or not (runs_dir / f"{tag(j, c)}.json").exists()]
    # a result under another stopping rule is not "done": refuse to mix rules in one directory
    if not args.force:
        other = []
        for j, c in pairs:
            fp = runs_dir / f"{tag(j, c)}.json"
            if not fp.exists():
                continue
            try:
                prev = json.loads(fp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            rule = prev.get("stop_rule") or {}   # none before v1.0: no cap, the budget
            if rule.get("k_max") != k_max_of(c, args.k_max) or prev.get("budget") != args.budget:
                other.append(f"{j.key} {c}")
        if other:
            print(f"ERROR: {len(other)} results in {runs_dir} were taken under another stopping rule "
                  f"(e.g. {other[0]}; this run: --k-max {args.k_max}, --budget {args.budget:g}). "
                  "Use another --out (v1.0: e.g. results/pcb_v1), or --force to re-run them")
            return 2
    n_ex = len({(j.problem, j.pset, j.src["port"]) for j in jobs})
    n_sets = f"{n_ex} parameter sets/ports x {len(args.freqs)} frequencies" \
        if args.freqs else f"{len(jobs)} parameter sets/ports"
    print(f"{n_sets} x {len(combos)} combos = {len(pairs)} jobs; {len(todo)} to run, "
          f"budget {args.budget:.0f} s, K_max {args.k_max}, {args.workers} workers"
          + (f", tag {args.tag}" if args.tag else "")
          + (f", extra PETSc options '{args.petsc_extra}'" if args.petsc_extra else "")
          + (f", GMRES restart {args.gmres_restart}"
             if args.gmres_restart != rfb.DEFAULT_GMRES_RESTART else "")
          + (f", accel_ic alpha {args.accel_ic_alpha:g}"
             if args.accel_ic_alpha != rfb.DEFAULT_ACCEL_IC_ALPHA else "")
          + (", HX without Dirichlet mask" if args.no_hx_mask else "")
          + (", saving solutions" if args.save_solutions else "")
          + (f", errors against {args.ref_solutions}" if args.ref_solutions else ""), flush=True)
    # reference solution per job (solution error check; not for the direct solve itself).
    # Keyed by the case too: the existing sets share set names (standard, off_resonance).
    refs = {}
    if args.ref_solutions:
        for j, c in todo:
            if c == DIRECT_COMBO:
                continue
            ref, why = rb.find_reference(args.ref_solutions, reference_tags(j), j.mesh)
            refs[(j.problem, j.key, c)] = ref
            if why:
                print(f"  WARNING {j.key} {c}: {why}; no error check")
    # Memory (Mac): estimate from the WSL records; jobs over the budget are excluded.
    budget_gb = args.mem_budget if args.mem_budget > 0 else None
    est = {}
    if budget_gb:
        peak = pcb_host.wsl_peak_rss()
        est = {(j.problem, j.key, c): pcb_host.estimate_gb(peak, j.pset, c) for j, c in todo}
        over = [(j, c) for j, c in todo if (est[(j.problem, j.key, c)][0] or 0) > budget_gb]
        unknown = [(j, c) for j, c in todo if est[(j.problem, j.key, c)][0] is None]
        print(f"host {HOST.name} ({HOST.label}, {HOST.perf_cores} performance cores, "
              f"{HOST.ram_gb:.0f} GB): memory budget {budget_gb:g} GB; "
              f"{len(over)} jobs excluded (estimate over the budget), "
              f"{len(unknown)} without a WSL record (run alone)", flush=True)
        for j, c in over:
            print(f"  excluded: {j.key} {c} (estimate {est[(j.problem, j.key, c)][0]:.1f} GB, "
                  f"{est[(j.problem, j.key, c)][1]})")
        todo = [(j, c) for j, c in todo if (j, c) not in over]
        jobs = [j for j in jobs if any(jj is j for jj, _ in todo)]
    no_mesh = sorted({j.mesh.name for j in jobs if not j.mesh.exists() and not getattr(j, "existing", False)})
    no_mesh_ex = sorted({j.mesh.name for j in jobs if not j.mesh.exists() and getattr(j, "existing", False)})
    if args.release_dir:
        missing = sorted({j.pset for j in jobs if not j.mesh.exists()})
        no_mesh = no_mesh_ex = []
        if missing:
            msg = (f"meshes missing in {args.release_dir}: {', '.join(missing)} "
                   "(<release-dir>/<set>/mesh.msh; download and unpack the sets from the released data)")
            if not args.list:
                print(f"ERROR: {msg}")
                return 2
            print(msg)
    if args.list:
        for j, c in todo:
            s = j.src
            km = k_max_of(c, args.k_max)
            if getattr(j, "existing", False):
                print(f"  {j.problem}:{j.key:13s} {c:15s} K_max={km or '-':<6} existing benchmark "
                      f"(suite {j.params.get('suite')}, lengths / lambda0, Gaussian source)"
                      f"{'' if j.mesh.exists() else '  [no mesh]'}")
                continue
            if j.excitation == "E2":
                exc = f"E2 {s['port']} of {len(j.pdef['ports'])} ports, R={s['R']:g}"
            else:
                exc = (f"E1 src {s['port']} at ({', '.join(f'{v:g}' for v in s['center'])}) "
                       f"dir {tuple(s['direction'])} w={s['width']:g}")
            if j.conductor == "sibc":
                exc += f" SIBC sigma={j.sigma:g} Zs={j.zs.real:.3e}(1+j) on {','.join(j.sibc_faces)}"
            elif j.conductor == "volume":
                exc += f" volume conductor sigma={j.sigma:g}"
            mem = ""
            if budget_gb:
                e, src = est[(j.problem, j.key, c)]
                mem = f"  mem {e:.1f} GB ({src})" if e is not None else "  mem unknown (alone)"
            print(f"  {j.problem}:{j.key:13s} {c:15s} K_max={km or '-':<6} f={j.params['freqGHz']} GHz {exc}"
                  f"{'' if j.mesh.exists() else '  [no mesh]'}{mem}")
        if no_mesh:
            print(f"meshes missing in {args.mesh_dir}: {', '.join(no_mesh)} "
                  "(python3 gmsh_templates/pcb/generate_pcb_meshes.py)")
        if no_mesh_ex:
            print(f"meshes missing in {args.existing_mesh_dir}: {', '.join(no_mesh_ex)} "
                  "(python3 gmsh_templates/generate_all_meshes.py -o generated_meshes)")
        return 0
    if no_mesh or no_mesh_ex:
        print("ERROR: meshes missing: "
              + "; ".join(f"{d}: {', '.join(m)} ({how})" for d, m, how in (
                  (args.mesh_dir, no_mesh, "python3 gmsh_templates/pcb/generate_pcb_meshes.py"),
                  (args.existing_mesh_dir, no_mesh_ex,
                   "python3 gmsh_templates/generate_all_meshes.py -o generated_meshes")) if m))
        return 2

    runs_dir.mkdir(parents=True, exist_ok=True)
    (args.out / "logs").mkdir(parents=True, exist_ok=True)
    meta = dict(host=HOST.name, host_label=HOST.label, mem_budget_gb=budget_gb,
                budget=args.budget, rtol=args.rtol, workers=args.workers, combos=combos,
                k_max=args.k_max, k_max_per_combo={c: k_max_of(c, args.k_max) for c in combos},
                sets=list(dict.fromkeys(j.pset for j in jobs)), params_json=PCB_PARAMS_JSON.relative_to(ROOT).as_posix(),
                existing_params_json=rfb.CASE_PARAM_JSON.relative_to(ROOT).as_posix(),
                tag=args.tag or None, petsc_extra=args.petsc_extra or None,
                gmres_restart=args.gmres_restart, accel_ic_alpha=args.accel_ic_alpha,
                freqs_GHz=args.freqs or None, hx_dirichlet_mask=not args.no_hx_mask,
                mrhs=dict(method=args.mrhs, recycle=args.mrhs_recycle,
                          recycle_max=args.mrhs_recycle_max) if args.mrhs else None,
                save_solutions=args.save_solutions or None,
                ref_solutions=str(args.ref_solutions) if args.ref_solutions else None,
                suite=args.suite or None,
                started=time.strftime("%Y-%m-%d %H:%M:%S"),
                environment=pcb_host.environment(args.freefem_bin))
    # one meta file per tag, so that a diagnostic campaign keeps the main one;
    # every run call is also appended to meta_history.jsonl (settings 13.4)
    meta_name = f"meta@{args.tag}.json" if args.tag else "meta.json"
    (args.out / meta_name).write_text(json.dumps(meta, indent=1), encoding="utf-8")
    with (args.out / "meta_history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    by_key = {(j.problem, j.key): j for j in jobs}
    # run_benchmark.run_job (budget, RSS, log parsing, result JSON) with the PCB job directory.
    rb.build_job_dir = make_pcb_build_job_dir(by_key)
    gate = pcb_host.MemoryGate(budget_gb) if budget_gb else None

    def run_one(ticket, j, c):
        sol = dict(save_solution=args.save_solutions, ref_solution=refs.get((j.problem, j.key, c)))
        if gate is None:
            return rb.run_job(j.task, cases, c, args.out, args.scratch, args.budget, args.rtol,
                              args.freefem_bin, **sol)
        held = gate.acquire(ticket, est[(j.problem, j.key, c)][0])
        try:
            return rb.run_job(j.task, cases, c, args.out, args.scratch, args.budget, args.rtol,
                              args.freefem_bin, **sol)
        finally:
            gate.release(held)
    n = n_fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, i, j, c): (j, c) for i, (j, c) in enumerate(todo)}
        for f in as_completed(futs):
            j, c = futs[f]
            n += 1
            try:
                r = f.result()
            except Exception as e:  # keep the campaign going
                n_fail += 1
                print(f"[{n}/{len(todo)}] {j.pset} {c}: EXCEPTION {e!r}", flush=True)
                continue
            log = args.out / "logs" / f"{tag(j, c)}.log"
            r["pcb"] = (existing_record_fields(j, c, log) if getattr(j, "existing", False)
                        else pcb_record_fields(j, c, log))
            r["host"] = HOST.name
            apply_stop_rule(r, k_max_of(c, args.k_max), log)
            if r["pcb"]["solver_version"] is None and r["status"] != "error":
                r["status"] = "error"   # the launcher did not reach the PCB solver
            ref = refs.get((j.problem, j.key, c))
            if ref and "rel_l2" in (r.get("solution_check") or {}):
                r["solution_check"]["s_max_abs_diff"] = s_max_abs_diff(r, ref)
            (runs_dir / f"{tag(j, c)}.json").write_text(json.dumps(r), encoding="utf-8")
            n_fail += r["status"] == "error"
            fr = f"{r['final_relres']:.2e}" if r["final_relres"] is not None else "-"
            sp = (r["pcb"].get("ports") or {}).get("S", {})
            s_txt = " ".join(f"{k}={abs(complex(*v)):.4f}<{math.degrees(math.atan2(v[1], v[0])):.1f}"
                             for k, v in sp.items())
            label = f"{j.problem}:{j.key}" if getattr(j, "existing", False) else j.key
            print(f"[{n}/{len(todo)}] {label} {c}: {r['status']} it={r['iterations']} rel={fr} "
                  f"wall={r['wall']:.0f}s setup={r['setup_time']} rss={r['peak_rss_gb']}GB {s_txt}"
                  f"{rb.solution_check_text(r.get('solution_check'))}"
                  + (f" |dS|={r['solution_check']['s_max_abs_diff']:.2e}"
                     if (r.get("solution_check") or {}).get("s_max_abs_diff") is not None else ""),
                  flush=True)
    print(f"done; {n_fail} errors -> {runs_dir}")
    return 0 if n_fail == 0 else 1


# Ritz probe (docs/matrix_features.md 8): Arnoldi on the preconditioned
# operator, per parameter set and preconditioner (the operator M^-1 A does not
# depend on the Krylov method, so one probe serves the GMRES and COCG rows).
RITZ_PRECS = ("gs", "ssor", "amg_gamg", "accel_ic", "cslp", "hx", "cslp_hx", "npatch_asm")
RITZ_OUT = ROOT / "results" / "pcb_ritz"
# inner solves of cslp / hx / cslp_hx in the probe. The standard inner GMRES
# (rtol 1e-2) makes the preconditioner change from step to step (no operator to
# take Ritz values of); "lu" (default) solves the inner systems exactly (MUMPS),
# the operator the standard combinations approximate; "vcycle" applies one GAMG
# V-cycle (as the cslp_mg / cslp_hx_mg presets).
RITZ_FIXED_INNER = {"lu": "-ksp_type preonly -pc_type lu -pc_factor_mat_solver_type mumps",
                    "vcycle": "-ksp_type preonly -pc_type gamg"}
RITZ_DONE_RE = re.compile(r"RITZ_DONE (\d+) n (\d+) start (\S+) time (\S+)")


def ritz_probe_setup(prec: str, inner: str = "lu") -> tuple:
    """(krylov, petsc_options, fixed_variant) of the probe of preconditioner
    prec. PETSc preconditioners run through the pc_cocg branch (precon() =
    one '-ksp_type preonly' application); hand-rolled ones through their own
    branch, with the inner solves made fixed (RITZ_FIXED_INNER[inner])."""
    if prec not in RITZ_PRECS:
        raise ValueError(f"preconditioner {prec}: not one of {', '.join(RITZ_PRECS)}")
    if preset_namespace(prec, "gmres", rb.NO_CAP).outer_method == "petsc":
        return "cocg", preset_namespace(prec, "cocg", rb.NO_CAP).petsc_options, False
    a = preset_namespace(prec, "gmres", rb.NO_CAP)
    if a.petsc_options and "preonly" not in a.petsc_options:
        return "gmres", RITZ_FIXED_INNER[inner], True
    return "gmres", a.petsc_options, False


def ritz_name(job: PcbJob, prec: str, args: argparse.Namespace) -> str:
    """<problem>_<key>__<prec>[@vcycle][@random]"""
    fixed = ritz_probe_setup(prec, args.inner)[2]
    return (f"{job.problem}_{job.key}__{prec}" + ("@vcycle" if fixed and args.inner == "vcycle" else "")
            + ("" if args.start == "rhs" else f"@{args.start}"))


def ritz_one(job: PcbJob, prec: str, args: argparse.Namespace) -> dict:
    import ritz_features as rf
    krylov, opts, fixed = ritz_probe_setup(prec, args.inner)
    name = ritz_name(job, prec, args)
    work = args.scratch / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for d in (FREEFEM_DIR, PCB_DIR):   # pcb/ overrides same names
        for f in d.iterdir():
            if f.suffix in (".edp", ".idp") and f.name != "runtime_case_config.idp":
                shutil.copy(f, work / f.name)
    probe = dict(steps=args.steps, start=args.start, seed=args.seed, petsc_options=opts)
    if getattr(job, "existing", False):
        runtime, pcb = job.configs(prec, krylov, 1e-8, rfb.parse_physical_names(job.mesh), work=work, ritz=probe)
    else:
        runtime, pcb = job.configs(prec, krylov, 1e-8, check_mesh_physical(job.pdef, job.mesh), ritz=probe)
    (work / "runtime_case_config.idp").write_text(runtime, encoding="utf-8")
    (work / "pcb_case_config.idp").write_text(pcb, encoding="utf-8")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1")
    env.setdefault("HWLOC_COMPONENTS", "-gl")
    t0 = time.time()
    try:
        p = subprocess.run([args.freefem_bin, "-nw", "-v", "0", PCB_SOLVER], cwd=work,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                           timeout=args.timeout)
        out, rc = p.stdout, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") if isinstance(e.stdout, str) else "", -9
    wall = time.time() - t0
    (args.out / "logs").mkdir(parents=True, exist_ok=True)
    (args.out / "logs" / f"{name}.log").write_text(out, encoding="utf-8")
    m = RITZ_DONE_RE.search(out)
    setup = re.search(r"PHASE setup_done (\S+)", out)
    ver = re.search(r"PCB_SOLVER_VERSION = (\S+)", out)
    # set: the parameter set as --sets names it (existing benchmark: <case>:<set>)
    r = dict(problem=job.problem, set=job.pset if getattr(job, "existing", False) else job.key, prec=prec, host=HOST.name, krylov_branch=krylov,
             petsc_options=opts, fixed_variant=fixed, inner=args.inner if fixed else None, steps_requested=args.steps, start=args.start,
             seed=args.seed if args.start == "random" else None,
             accel_ic_alpha=job.accel_ic_alpha if prec == "accel_ic" else None,
             hx_dirichlet_mask=job.hx_mask if f"{prec}/gmres" in HX_MASK_COMBOS else None,
             solver_version=ver.group(1) if ver else None, returncode=rc, wall=wall,
             setup_time=float(setup.group(1)) if setup else None,
             arnoldi_time=float(m.group(4)) if m else None,
             status="ok" if m and rc == 0 else ("timeout" if rc == -9 else "error"))
    if r["status"] == "ok":
        hess = work / RITZ_FILE
        (args.out / "hessenberg").mkdir(parents=True, exist_ok=True)
        shutil.copy(hess, args.out / "hessenberg" / f"{name}.txt")
        Hbar, beta, n = rf.load_hessenberg(hess)
        r["features"] = rf.features(Hbar)
        r["n"] = n
    (args.out / "runs").mkdir(parents=True, exist_ok=True)
    (args.out / "runs" / f"{name}.json").write_text(json.dumps(r), encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    return r


def cmd_ritz(args: argparse.Namespace) -> int:
    """Ritz probe of the preconditioned operators (docs/matrix_features.md 8)."""
    sys.path.insert(0, str(PCB_DIR))
    for k, v in dict(port="", freq="", freqs=[], excitation="E2", petsc_extra="", tag="",
                     gmres_restart=rfb.DEFAULT_GMRES_RESTART, accel_ic_alpha=rfb.DEFAULT_ACCEL_IC_ALPHA,
                     no_hx_mask=False, mrhs="", mrhs_recycle=MRHS_RECYCLE,
                     mrhs_recycle_max=MRHS_RECYCLE_MAX).items():
        setattr(args, k, v)
    try:
        jobs = select_pcb_jobs(args, load_pcb_cases(), include_existing=True)
        precs = [c.strip() for c in args.precs.split(",") if c.strip()]
        for c in precs:
            ritz_probe_setup(c, args.inner)
    except (ValueError, KeyError) as e:
        print(f"ERROR: {e}")
        return 2
    if args.steps < 2:
        print("ERROR: --steps must be >= 2")
        return 2
    args.out = args.out / HOST.name
    pairs = [(j, c) for j in jobs for c in precs]
    todo = [(j, c) for j, c in pairs
            if args.force or not (args.out / "runs" / f"{ritz_name(j, c, args)}.json").exists()]
    print(f"{len(jobs)} parameter sets x {len(precs)} preconditioners = {len(pairs)} probes; "
          f"{len(todo)} to run, {args.steps} Arnoldi steps, start {args.start}, inner {args.inner}, "
          f"{args.workers} workers, "
          f"host {HOST.name} -> {args.out}", flush=True)
    if args.list:
        for j, c in todo:
            k, opts, fixed = ritz_probe_setup(c, args.inner)
            print(f"  {j.problem}:{j.key:16s} {c:9s} branch {k:5s} '{opts}'"
                  f"{' (fixed variant)' if fixed else ''}{'' if j.mesh.exists() else '  [no mesh]'}")
        return 0
    no_mesh = sorted({str(j.mesh) for j, _ in todo if not j.mesh.exists()})
    if no_mesh:
        print(f"ERROR: meshes missing: {', '.join(no_mesh)}")
        return 2
    n = n_fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(ritz_one, j, c, args): (j, c) for j, c in todo}
        for f in as_completed(futs):
            j, c = futs[f]
            n += 1
            try:
                r = f.result()
            except Exception as e:  # keep the campaign going
                n_fail += 1
                print(f"[{n}/{len(todo)}] {j.key} {c}: EXCEPTION {e!r}", flush=True)
                continue
            n_fail += r["status"] != "ok"
            ft = r.get("features") or {}
            print(f"[{n}/{len(todo)}] {j.key} {c}: {r['status']} m={ft.get('m')} wall={r['wall']:.0f}s "
                  f"kappa_ritz={ft.get('kappa_ritz', float('nan')):.3g} sep={ft.get('origin_sep', float('nan')):.3g} "
                  f"pred_it={ft.get('pred_iterations')} gmres_res_m={ft.get('gmres_relres_m', float('nan')):.2e}",
                  flush=True)
    print(f"done; {n_fail} failed -> {args.out / 'runs'}")
    return 0 if n_fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    rg = sub.add_parser("regress", help="regression check of the PCB solver fork (settings 7.5)")
    rg.add_argument("--mesh-dir", type=Path, default=rfb.DEFAULT_MESH_DIR)
    rg.add_argument("--out", type=Path, default=DEFAULT_OUT)
    rg.add_argument("--scratch", type=Path, default=Path("/tmp/emag_pcb"))
    rg.add_argument("--only", default="", help="case:param_set:preset/krylov list, comma separated")
    rg.add_argument("--all-cases", action="store_true",
                    help=f"also every parameter set of case1A-3F with {ALL_CASES_COMBO} (46 more cases)")
    rg.add_argument("--max-it", type=int, default=50, help="iteration cap of every run (default 50)")
    rg.add_argument("--workers", type=int, default=HOST.workers(2),
                    help=f"parallel runs (default {HOST.workers(2)}; Mac: performance cores)")
    rg.add_argument("--timeout", type=float, default=1800.0, help="per-run timeout in seconds")
    rg.add_argument("--freefem-bin", default="FreeFem++-mpi")
    rg.add_argument("--update-reference", action="store_true",
                    help=f"store the runs of {', '.join(c for _, _, c in REFERENCE_CASES)} as the reference "
                         f"of this host ({REFERENCE_JSON.name}, key @{HOST.name}) instead of comparing")
    rn = sub.add_parser("run", help="PCB benchmark solves (settings 15.2)")
    rn.add_argument("--mesh-dir", type=Path, default=PCB_MESH_DIR)
    rn.add_argument("--existing-mesh-dir", type=Path, default=rfb.DEFAULT_MESH_DIR,
                    help="meshes of the existing benchmark's sets (<case>_<set>.msh)")
    rn.add_argument("--release-dir", type=Path, default=None, metavar="DIR",
                    help="read the meshes of the released data (Zenodo, J-Stage Data) unpacked in DIR: "
                         "DIR/<set>/mesh.msh, the canonical sets as <case>_<set>; overrides --mesh-dir "
                         "and --existing-mesh-dir")
    rn.add_argument("--out", type=Path, default=DEFAULT_OUT)
    rn.add_argument("--scratch", type=Path, default=Path("/tmp/emag_pcb_run"))
    rn.add_argument("--problems", default="", help="P01,P03,P05")
    rn.add_argument("--sets", default="", help="parameter sets, comma separated (overrides --suite, --roles); "
                    "the existing benchmark's as <case>:<set>, e.g. case2A:standard")
    rn.add_argument("--suite", default="",
                    help="suite tiers of the parameter sets (settings 15: core, extended, challenge; "
                         "'multi_rhs' = the sets with multiRhsBudgetPerPort), comma separated "
                         "(overrides --roles)")
    rn.add_argument("--roles", default="minimal_set",
                    help="parameter-set roles (minimal_set, mesh_convergence, supplementary, "
                         "diagnostic, sibc, extended_set); '' = all")
    rn.add_argument("--combos", default=",".join(PCB_DEFAULT_COMBOS))
    rn.add_argument("--port", default="",
                    help="excited port label(s), comma separated, or 'all' (one job per port; results "
                         "<set>@<port> except for the first port); default: the first port")
    rn.add_argument("--excitation", default="E2", choices=["E2", "E1"],
                    help="E2 lumped ports (default), E1 port-substitute volume source")
    rn.add_argument("--budget", type=float, default=None,
                    help=f"wall-clock seconds per solve, incl. setup (default: {SAFETY_TIME_LIMIT:g}, the safety "
                         f"limit of the K_max rule; {LEGACY_BUDGET:g} with --k-max none)")
    rn.add_argument("--k-max", default=None, metavar="standard|none|N",
                    help="iteration cap (docs/paper_plan.md 4.1): standard (default; per combination, "
                         "K_MAX_STANDARD: GMRES of gs/ssor/amg_gamg/accel_ic and hx 10000, COCG 50000, "
                         "cslp 3000, cslp_hx 1000), none (the pre-v1.0 rule: the time budget stops the "
                         "solve; the default with --mrhs) or a number for every combination (needs --tag). "
                         "Results at the cap have status max_it")
    rn.add_argument("--rtol", type=float, default=1e-8)
    rn.add_argument("--workers", type=int, default=HOST.workers(1),
                    help=f"parallel jobs (default {HOST.workers(1)}; Mac: performance cores)")
    rn.add_argument("--mem-budget", type=float, default=HOST.mem_budget_gb or 0.0, metavar="GB",
                    help=f"memory budget of the running jobs (default {HOST.mem_budget_gb or 0:g}; "
                         "Mac: 75 %% of the memory, 0 = off): jobs whose estimate from the WSL "
                         "records exceeds it are excluded")
    rn.add_argument("--freefem-bin", default="FreeFem++-mpi")
    rn.add_argument("--petsc-extra", default="", metavar="OPTS",
                    help="extra PETSc options appended to the KSP options of PETSc-KSP combinations "
                         "(outerMethod petsc: gs, ssor, amg_gamg, ... /gmres, mumps/direct); needs --tag. "
                         "Write --petsc-extra='-opt ...' (with '=')")
    rn.add_argument("--tag", default="",
                    help="variant name: results and logs are named <set>@<tag> and record it")
    rn.add_argument("--gmres-restart", type=int, default=rfb.DEFAULT_GMRES_RESTART, metavar="M",
                    help=f"GMRES restart length (default {rfb.DEFAULT_GMRES_RESTART}; PETSc and hand-rolled "
                         "GMRES); another value needs --tag and GMRES combinations only")
    rn.add_argument("--accel-ic-alpha", type=float, default=rfb.DEFAULT_ACCEL_IC_ALPHA, metavar="A",
                    help=f"accelerated IC(0) factor (default {rfb.DEFAULT_ACCEL_IC_ALPHA}); another value "
                         "needs --tag and accel_ic combinations only")
    rn.add_argument("--no-hx-mask", action="store_true",
                    help="HX / CSLP+HX without the PCB-standard mask of the gradient correction on the "
                         "PEC (on() penalty) rows, as the existing benchmark's HX; needs --tag")
    rn.add_argument("--hx-vec", type=int, default=None, choices=[0, 1, 2, 3],
                    help="HX vector (Pi) term for hx/cslp_hx (pcb_hx_vec.idp, docs/paper_plan.md A1): "
                         "0 off, 1 Pi^T A Pi, 2 Pi^T (A + 2k0^2 Meps) Pi, 3 Pi^T P Pi "
                         "(CSLP-shifted, cslp_hx only); default: the standard (hx 2, cslp_hx 0); "
                         "needs --tag")
    rn.add_argument("--hx-vec-options", default="", metavar="OPTS",
                    help="PETSc options of the vector-term inner solve (default: those of the gradient term)")
    rn.add_argument("--hx-smoother", default=None, choices=["jacobi", "sgs"],
                    help="HX smoother of hx/gmres: jacobi or sgs (symmetric Gauss-Seidel, the standard); "
                         "needs --tag")
    rn.add_argument("--freq", default="", metavar="GHz[,GHz...]",
                    help="solve at these frequencies instead of the parameter set's freqGHz, on the "
                         "set's mesh; results are named <set>@f<GHz>")
    rn.add_argument("--mrhs", default="", choices=["", *MRHS_METHODS],
                    help="multiple right-hand sides: every port of the set solved in ONE process "
                         "(results <set>@mrhs-<method>, full S matrix): shared (set-up shared, solves one "
                         "after the other), block (block FGMRES), gcro (recycled FGMRES); block/gcro "
                         "need a hand-rolled GMRES combination. Give --budget for all right-hand sides")
    rn.add_argument("--mrhs-recycle", type=int, default=MRHS_RECYCLE, metavar="K",
                    help=f"gcro: harmonic Ritz vectors added per right-hand side (default {MRHS_RECYCLE})")
    rn.add_argument("--mrhs-recycle-max", type=int, default=MRHS_RECYCLE_MAX, metavar="K",
                    help=f"gcro: largest recycle space (default {MRHS_RECYCLE_MAX})")
    rn.add_argument("--save-solutions", action="store_true",
                    help="write each solution to <out>/solutions/<job>.sol.gz (off by default; "
                         "for mumps/direct references)")
    rn.add_argument("--ref-solutions", type=Path, default=None, metavar="DIR",
                    help="result directory with saved mumps/direct solutions (DIR/solutions): record "
                         "the L2/curl/H(curl) errors and |dS| against them (off by default)")
    rn.add_argument("--force", action="store_true", help="re-run jobs that already have results")
    rn.add_argument("--list", action="store_true", help="list the jobs and exit (no FreeFEM)")
    rn.add_argument("--show-config", default="", metavar="SET:PRESET/KRYLOV",
                    help="print the generated .idp configuration of one job and exit")
    rz = sub.add_parser("ritz", help="Ritz probe of the preconditioned operators (docs/matrix_features.md 8)")
    rz.add_argument("--mesh-dir", type=Path, default=PCB_MESH_DIR)
    rz.add_argument("--existing-mesh-dir", type=Path, default=rfb.DEFAULT_MESH_DIR,
                    help="meshes of the existing benchmark's sets (<case>:<set>, selected by --sets "
                         "or --suite as run does)")
    rz.add_argument("--release-dir", type=Path, default=None, metavar="DIR",
                    help="read the meshes of the released data unpacked in DIR (as run)")
    rz.add_argument("--out", type=Path, default=RITZ_OUT, help="results go to <out>/<host>/")
    rz.add_argument("--scratch", type=Path, default=Path("/tmp/emag_pcb_ritz"))
    rz.add_argument("--problems", default="")
    rz.add_argument("--sets", default="")
    rz.add_argument("--suite", default="core")
    rz.add_argument("--roles", default="")
    rz.add_argument("--precs", default=",".join(RITZ_PRECS),
                    help=f"preconditioners (default {','.join(RITZ_PRECS)}); cslp, hx, cslp_hx with "
                         "fixed inner solves (--inner)")
    rz.add_argument("--steps", type=int, default=300, help="Arnoldi steps (default 300)")
    rz.add_argument("--start", default="rhs", choices=["rhs", "random"],
                    help="start vector: the right-hand side (default) or random (results <...>@random)")
    rz.add_argument("--seed", type=int, default=1)
    rz.add_argument("--inner", default="lu", choices=list(RITZ_FIXED_INNER),
                    help="inner solves of cslp, hx, cslp_hx: lu (exact, MUMPS; default; the operator "
                         "the standard inner GMRES approximates) or vcycle (one GAMG V-cycle, results "
                         "<...>@vcycle)")
    rz.add_argument("--workers", type=int, default=HOST.workers(1))
    rz.add_argument("--timeout", type=float, default=3600.0)
    rz.add_argument("--freefem-bin", default="FreeFem++-mpi")
    rz.add_argument("--force", action="store_true")
    rz.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.cmd == "ritz":
        return cmd_ritz(args)
    if args.cmd == "regress":
        return cmd_regress(args)
    if args.cmd == "run":
        return cmd_run(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
