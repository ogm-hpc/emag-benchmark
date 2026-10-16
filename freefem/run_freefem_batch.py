#!/usr/bin/env python3
"""Batch launcher for Edge03d Maxwell solves in FreeFEM++.

This script:
1) scans generated .msh files,
2) infers case/parameter-set,
3) writes freefem/runtime_case_config.idp,
4) optionally launches FreeFEM++ for each mesh.

Usage examples:
  python3 freefem/run_freefem_batch.py --list
  python3 freefem/run_freefem_batch.py --cases case1A,case1B --backend hypre --run
  python3 freefem/run_freefem_batch.py --abc sm --run
  python3 freefem/run_freefem_batch.py --preset dryrun --run
    # smoke test: mesh load + matrix assembly + 5 GMRES/Jacobi iterations only,
    # for every discovered case/parameter-set
  python3 freefem/run_freefem_batch.py --preset ilu --krylov gmres --run
  python3 freefem/run_freefem_batch.py --preset ilu --krylov cocg --run
    # this project's iterative-method scope is GMRES and COCG only (see
    # KRYLOV_MAP); run both for every preset you care about -- COCG doing
    # worse than (or breaking down relative to) GMRES is itself a result to
    # report, not a reason to drop it from the comparison.
  python3 freefem/run_freefem_batch.py --preset cslp --run
    # Complex Shifted Laplacian Preconditioner: bypasses PETSc's own KSP for
    # the outer loop (uses a hand-rolled GMRES instead, see gmres_precon.idp)
    # and ignores --krylov -- see maxwell_edge03d_solver.edp's
    # outerMethod=="cslp" branch.
  python3 freefem/run_freefem_batch.py --preset accel_ic --krylov gmres --run
  python3 freefem/run_freefem_batch.py --preset accel_ic --krylov cocg --accel-ic-alpha 1.0 --run
    # From-scratch accelerated IC(0) (Fujiwara/Nakata/Fusayasu-style, see
    # accel_ic_precon.idp) -- not PETSc-backed at all; --krylov selects
    # between hand-rolled GMRES/COCG drivers (both validated on
    # freefem/test_accel_ic_toy.edp).
  python3 freefem/run_freefem_batch.py --preset hx --run
    # Hiptmair-Xu-style 2-term auxiliary-space preconditioner (see
    # hx_precon.idp) -- addresses the curl-kernel/gradient near-null-space
    # problem, a DIFFERENT difficulty than CSLP's indefiniteness fix.
    # GMRES-only (ignores --krylov), not PETSc-backed for the outer loop.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
FREEFEM_DIR = ROOT / "freefem"
CONFIG_FILE = FREEFEM_DIR / "runtime_case_config.idp"
SOLVER_EDP = FREEFEM_DIR / "maxwell_edge03d_solver.edp"
CASE_PARAM_JSON = ROOT / "gmsh_templates" / "case_parameters.json"
DEFAULT_MESH_DIR = ROOT / "generated_meshes" / "mesh"
DEFAULT_RESULT_DIR = ROOT / "results" / "freefem"
DEFAULT_PETSC_OPTIONS = "-ksp_type gmres -ksp_rtol 1.0e-8 -ksp_max_it 4000 -pc_type ilu"

# The Gaussian excitation source position, per case. A blind (0,0,0) default is
# geometrically wrong for several cases: it falls inside the excluded PEC sphere
# in case1A (mesh doesn't exist there -> near-zero RHS), inside the dielectric
# sphere in case1B, and exactly on the dividing septum/iris/port plane in
# case1C/case2B/case2C/case2E. Each override below places the source safely
# inside an actual air region, clear of any material/PML boundary, for the
# fixed (non-swept) geometry constants shared across that case's parameter sets.
SOURCE_OVERRIDES = {
    "case1C": (-0.75, 0.0, 0.0), # center of the left chamber (Lc=1.5, x in [-1.5,-0.05])
    "case2B": (-1.05, 0.0, 0.0), # center of the left chamber (Lch=2, x in [-2.05,-0.05])
    "case2C": (-1.0, 0.0, 0.0),  # inside the left chamber, clear of the central slit plate
    "case2E": (0.25, 0.0, 0.0),  # inside the waveguide, clear of the x=0 port and first iris
    "case2F": (-75.0, 0.0, 0.0), # middle of the 150mm waveguide stub (x in [-150,0]), clear of the PortOut face (x=-150) and the iris/cavity junction (x=0)
}
# Gaussian width (in units of lambda0) where 0.25*lambda0 would be too wide for
# the domain: the 0.4*lambda0 cavities of case3A/3C/3F and the 0.2-high 3D box.
SOURCE_WIDTH_OVERRIDES = {"case3A": 0.05, "case3C": 0.05, "case3D": 0.05, "case3F": 0.05}


def source_for(case_name: str, params: Dict) -> Tuple[float, float, float, float]:
    """(x, y, z, width) of the Gaussian source. case1A/1B: on the z axis midway
    between the sphere surface and the PML, width = a quarter of that gap."""
    lambda0 = float(params.get("lambda0", 1.0))
    if case_name in ("case1A", "case1B"):
        R, half = float(params["R"]), float(params["L"]) / 2
        return 0.0, 0.0, (R + half) / 2, (half - R) / 4
    x, y, z = SOURCE_OVERRIDES.get(case_name, (0.0, 0.0, 0.0))
    return x, y, z, SOURCE_WIDTH_OVERRIDES.get(case_name, 0.25) * lambda0

# Iterative-method scope for this benchmark: GMRES and COCG only (see --krylov).
# COCG ("-ksp_type cg -ksp_cg_type symmetric") is PETSc's CG variant for complex
# *symmetric* (non-Hermitian) matrices -- exactly our matrix class, since the
# Nedelec curl-curl - k^2*eps bilinear form is never conjugated.
#
# 2026-09-28: "--krylov cocg" with a PETSc preconditioner NO LONGER uses PETSc's
# KSPCG. KSPSolve_CG (PETSc 3.22) stops with DIVERGED_INDEFINITE_MAT whenever
# Re(p^T A p) changes sign between iterations -- an SPD heuristic that is
# meaningless for complex-symmetric COCG (p^T A p is complex); it stopped every
# COCG run after 1-2 iterations (the "COCG breaks down immediately" finding of
# 2026-07 was this check, not COCG). Instead the solver's outerMethod
# "pc_cocg" applies the PETSc PC through "-ksp_type preonly" and runs the
# hand-rolled cocg_precon.idp. The KRYLOV_MAP["cocg"] entry below is only used
# by the legacy krylov choice "cocg_petsc" (kept for reference).
# COCG also requires a complex-symmetric preconditioner (M^T = M): SSOR, GAMG
# and IC(0) are (measured |x^T M^-1 y - y^T M^-1 x|/(|x||M^-1 y|) ~ 1e-16);
# forward GS is not (~4e-3), so gs/cocg is out of the benchmark scope.
#
# IMPORTANT: this project's purpose is determining *whether/how* a preconditioner
# can solve these systems, not finding the fastest solver. COCG performing worse
# than (or breaking down relative to) GMRES is itself a result to report, not a
# reason to drop COCG from the comparison -- keep both in scope regardless of
# which one "wins" on any given case.
#
# Residual definition (2026-09-28): every driver now monitors the TRUE
# (unpreconditioned) residual ||b - A x||, so residual histories are comparable
# across presets and with the hand-rolled drivers (which are right-
# preconditioned). PETSc's defaults monitored the PRECONDITIONED residual
# (left-preconditioned GMRES; CG's preconditioned norm), which is not
# comparable between preconditioners. GMRES also uses the same restart length
# as the hand-rolled drivers (DEFAULT_GMRES_RESTART) instead of PETSc's 30.
KRYLOV_MAP = {
    "gmres": "-ksp_type gmres -ksp_pc_side right -ksp_gmres_restart {restart}",
    "cocg": "-ksp_type cg -ksp_cg_type symmetric -ksp_norm_type unpreconditioned",
    "cocg_petsc": "-ksp_type cg -ksp_cg_type symmetric -ksp_norm_type unpreconditioned",
}

# Preconditioner (PC) presets. Each entry omits -ksp_type; apply_preset()
# prepends the --krylov choice so every PC can be paired with either GMRES or
# COCG.
PRESET_MAP = {
    "jacobi": {
        "backend": "petsc",
        "petsc_options": "-pc_type jacobi -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    # PCSOR sweep options are FLAGS: the former "-pc_sor_symmetric false/true"
    # did not select anything, so both "gs" and "ssor" ran PETSc's default
    # (local symmetric) sweep, i.e. both were SSOR (fixed 2026-09-28: gs and
    # ssor gave bit-identical iteration histories).
    "gs": {
        "backend": "petsc",
        "petsc_options": "-pc_type sor -pc_sor_forward -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "ssor": {
        "backend": "petsc",
        "petsc_options": "-pc_type sor -pc_sor_symmetric -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "ic0": {
        "backend": "petsc",
        "petsc_options": "-pc_type icc -pc_factor_levels 0 -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "ic0_shift": {
        # "Accelerated"/shifted IC(0): PETSc perturbs the diagonal during the
        # incomplete Cholesky factorization (-pc_factor_shift_type) to avoid
        # the breakdown plain IC(0) risks on our complex-symmetric indefinite
        # system. CONFIRMED on case2A: stable, monotonically decreasing
        # residual over 5 iterations, unlike plain IC(0)'s much slower setup.
        # -pc_factor_shift_amount can be omitted (PETSc auto-selects); set
        # explicitly here for reproducibility across cases/runs.
        "backend": "petsc",
        "petsc_options": (
            "-pc_type icc -pc_factor_levels 0 -pc_factor_shift_type positive_definite "
            "-pc_factor_shift_amount 0.1 -ksp_rtol 1e-8 -ksp_max_it 4000"
        ),
    },
    "ilu": {
        "backend": "petsc",
        "petsc_options": "-pc_type ilu -pc_factor_levels 1 -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "accel_ic": {
        # Fujiwara/Nakata/Fusayasu (IEEE Trans. Magn., vol.29, no.2, 1993)
        # -style accelerated IC(0): a from-scratch complex-symmetric
        # incomplete Cholesky (freefem/accel_ic_precon.idp) matching a
        # reference implementation the user supplied: standard fill-DROPPING
        # IC(0) (no redistribution to other diagonals -- an earlier version
        # of this file wrongly implemented Ajiz-Jennings/Gustafsson MILU
        # instead, which behaves oppositely under the acceleration factor),
        # where each row's ORIGINAL diagonal a_ii is multiplied by
        # --accel-ic-alpha BEFORE subtracting that row's accumulated
        # elimination terms. alpha=1.0 is plain IC(0) (no scaling). This is
        # NOT the same mechanism as ic0_shift (PETSc's
        # MAT_SHIFT_POSITIVE_DEFINITE perturbs the diagonal ADDITIVELY before
        # factoring; this scales it MULTIPLICATIVELY -- see
        # problem_settings.md). PETSc has no MILU/diagonal-scaled-IC option
        # at all, hence the from-scratch implementation.
        #
        # CONFIRMED on case2A_standard (direct ||A*z-b|| vs ||b||=0.035
        # quality check, z=precon(b)): alpha=1.0 is actively HARMFUL
        # (0.084, worse than no preconditioner), alpha=1.1->0.040,
        # alpha=1.2->0.0351 (~breakeven), alpha=1.5->0.0331 (first clearly
        # useful value, but only a modest ~5.5% improvement per application)
        # -- single-level IC(0)-family preconditioners are inherently weak
        # for this indefinite curl-curl system regardless of tuning; CSLP
        # (see the cslp preset) is the strong preconditioner for this project.
        #
        # Not PETSc-backed at all: unlike every other preset, petsc_options
        # is unused (the outer solver is also hand-rolled -- gmres_precon.idp
        # or cocg_precon.idp, selected by --krylov, both validated on
        # freefem/test_accel_ic_toy.edp and test_accel_ic_random.edp).
        "backend": "none",
        "petsc_options": "",
    },
    "hx": {
        # Hiptmair-Xu-style FULL 3-term additive auxiliary-space
        # preconditioner (freefem/hx_precon.idp): hxPrecon(r) =
        # omega*D_A^-1*r + G*(Mgrad^-1*(G^T*r)) + Pi*(Mvec^-1*(Pi^T*r)).
        # Addresses a DIFFERENT difficulty than CSLP: CSLP stabilizes the
        # sign-indefiniteness from -k0^2; HX corrects for A's curl-curl
        # term vanishing exactly on gradient fields (curl(grad phi)=0),
        # which plain algebraic smoothers/AMG cannot see at all -- a
        # structural problem independent of k0's sign.
        # HYPRE AMS (the standard PETSc route to this) is unavailable (no
        # HYPRE in this complex build); FreeFEM's own gradient-wrapper
        # Mat<complex> constructor also has no complex overload (confirmed
        # via test_hx_gradient.edp) -- hence this from-scratch
        # implementation, using mat_edgeP1's MatrixEdgeP1 for the discrete
        # gradient (real matrix, used directly against complex vectors, no
        # Mat wrapper needed -- same strategy as CSLP's Aloc), plus a
        # hand-derived tangential nodal interpolation Pi (P1^3 -> Edge03d,
        # exact via the trapezoid rule on the topology GLoc already
        # encodes) and its auxiliary vector-Laplacian Mvec (unshifted here
        # -- Mvec keeps A's curl-curl term and inherits its full
        # indefiniteness, unlike Mgrad; a shifted variant is the "cslp_hx"
        # preset below).
        #
        # VALIDATED on test_hx_toy.edp: adding the 3rd term took a
        # realistic Gaussian-source test case from 2.69e-3 (2-term) to
        # 7.75e-8 after 200 identical GMRES iterations. CONFIRMED on
        # case2A_standard: much faster per-iteration convergence rate than
        # 2-term (~3.8%/iter vs ~0.03-0.15%/iter) but each iteration costs
        # ~16x more (Mvec's indefinite GAMG solve dominates, ~0.6-0.7s vs
        # Mgrad's ~0.01s) -- 900s reached relative ~2.08e-3 with visible
        # late-stage deceleration, still short of CSLP's ~3e-5 in the same
        # budget.
        #
        # petsc_options here is used for Mgrad's AND Mvec's inner GAMG
        # solves (same string, matching every other preset's one-shared-
        # inner-options convention), not the outer loop, which is
        # hand-rolled (gmres_precon.idp) and GMRES-only for now (like CSLP,
        # --krylov is ignored -- COCG with this composite PC is unvalidated).
        "backend": "none",
        "petsc_options": "-ksp_type gmres -pc_type gamg -ksp_rtol 1e-2 -ksp_max_it 20",
    },
    "cslp_hx": {
        # Combined CSLP + 3-term HX (freefem/cslp_hx_precon.idp):
        # cslpHxPrecon(r) = P^-1*r + G*(Mgrad^-1*(G^T*r)) +
        # Pi*(MvecShift^-1*(Pi^T*r)). P (CSLP's shifted operator) replaces
        # HX's plain-Jacobi smoother term outright -- P^-1 is already a far
        # richer, indefiniteness-aware correction than a diagonal sweep.
        # Mgrad stays unshifted (not sign-indefinite); Mvec IS shifted
        # (same cslpBeta1/cslpBeta2 as P) since it inherits A's full
        # curl-curl indefiniteness, unlike Mgrad -- motivated directly by
        # pure 3-term HX's observed late-stage deceleration with an
        # unshifted Mvec (see the "hx" preset's notes / problem_settings.md).
        #
        # Addresses CSLP's and HX's difficulties SIMULTANEOUSLY: CSLP's
        # sign-indefiniteness fix and HX's curl-kernel/gradient
        # near-null-space fix are independent axes (per the user's
        # explicit correction to an earlier analysis) -- a problem could
        # need both. VALIDATED on test_cslp_hx_toy.edp (cube(5,5,5),
        # generic Gaussian-source RHS): CSLP alone converged in 33 iters,
        # HX alone (Jacobi smoother + shifted grad/vec corrections) reached
        # only 2.22e-5 in 100 iters, combined converged in 82 iters -- on
        # this SMALL, EASY toy problem the combination was slower than CSLP
        # alone (plausibly because CSLP's shift already achieves
        # near-optimal eigenvalue clustering there, and the extra
        # correction terms perturb rather than help) -- the real test is
        # on cases where CSLP alone struggles (e.g. case2A at real scale).
        #
        # GMRES-only (like both parents); petsc_options used for P's,
        # Mgrad's, AND Mvec's inner GAMG solves (same shared string).
        "backend": "none",
        "petsc_options": "-ksp_type gmres -pc_type gamg -ksp_rtol 1e-2 -ksp_max_it 20",
    },
    "cslp_mg": {
        # CSLP with a FIXED linear approximation of the shifted-operator inverse:
        # exactly one GAMG V-cycle ("-ksp_type preonly"), instead of the inner
        # GMRES+GAMG of "cslp" (whose result changes from one application to
        # the next). The preconditioner is then a fixed complex-symmetric
        # operator (M_beta^T = M_beta, GAMG with P^T restriction and polynomial
        # smoothers), so COCG applies as well as GMRES (2026-09-28).
        "backend": "none",
        "petsc_options": "-ksp_type preonly -pc_type gamg",
    },
    "cslp_hx_mg": {
        # CSLP+HX with both inner solves (shifted operator P and gradient
        # auxiliary problem G^T A G) replaced by one GAMG V-cycle each: fixed,
        # complex-symmetric -> usable with COCG.
        "backend": "none",
        "petsc_options": "-ksp_type preonly -pc_type gamg",
    },
    "amg_gamg": {
        "backend": "petsc",
        "petsc_options": "-pc_type gamg -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "amg_boomer": {
        # CONFIRMED BROKEN: this FreeFEM's complex-scalar PETSc build has no
        # HYPRE compiled in ("Unable to find requested PC type hypre"). Kept
        # here for reference / in case a HYPRE-enabled PETSc is swapped in.
        "backend": "hypre",
        "petsc_options": "-ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "ams": {
        # CONFIRMED BROKEN: same HYPRE-absence issue as amg_boomer, plus AMS
        # additionally needs a discrete-gradient matrix and nodal coordinates
        # passed to set(..., coordinates=..., gradient=...), which this solver
        # does not currently build.
        "backend": "petsc",
        "petsc_options": "-pc_type hypre -pc_hypre_type ams -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "ads": {
        # CONFIRMED BROKEN: same HYPRE-absence issue; ADS is also the H(div)
        # auxiliary-space method, a mismatch for our H(curl) Nedelec space
        # (AMS is the H(curl)-appropriate choice).
        "backend": "petsc",
        "petsc_options": "-pc_type hypre -pc_hypre_type ads -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "bddc": {
        # CONFIRMED BROKEN: "PCBDDC preconditioner requires matrix of type
        # MATIS"; MatCreate() here does not build a MATIS matrix. Would also
        # need true multi-subdomain (-np > 1) runs to be meaningful.
        "backend": "petsc",
        "petsc_options": "-pc_type bddc -ksp_rtol 1e-8 -ksp_max_it 4000",
    },
    "cslp": {
        # Complex Shifted Laplacian Preconditioner. Unlike every other preset,
        # these options precondition a SEPARATE shifted matrix P (assembled in
        # the .edp itself, not here), solved only approximately/inexactly
        # (loose rtol, low max_it -- it's an inner solve inside each outer
        # iteration, not the final answer). The outer loop is FreeFEM's own
        # AffineFGMRES, driven by outerRtol/outerMaxIt in runtime_case_config
        # (see build_runtime_config's DEFAULT_OUTER_RTOL/DEFAULT_OUTER_MAXIT).
        # CONFIRMED (freefem/test_cslp.edp, case2A_standard): relative
        # residual 6.2e-3 after 30 outer iterations, vs. plain GMRES+GAMG
        # stalling at DIVERGED_ITS after 4000 iterations without CSLP.
        "backend": "petsc",
        "petsc_options": "-ksp_type gmres -pc_type gamg -ksp_rtol 1e-2 -ksp_max_it 20",
    },
    "dryrun": {
        # Smoke test only: load the mesh, assemble the matrix/RHS, then run
        # exactly 5 GMRES+Jacobi iterations (rtol is set unreachably small so
        # convergence never triggers early) to confirm the whole pipeline runs
        # end to end without waiting for a full solve. Not a performance preset;
        # always uses GMRES regardless of --krylov, since it is only checking
        # that assembly/solve wiring works, not comparing Krylov methods.
        "backend": "petsc",
        "petsc_options": (
            "-ksp_type gmres -pc_type jacobi -ksp_max_it 5 -ksp_rtol 1e-50 "
            "-ksp_monitor -ksp_converged_reason"
        ),
    },
}


@dataclass
class MeshTask:
    case_name: str
    param_set: str
    mesh_path: Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Edge03d FreeFEM solves for benchmark meshes")
    p.add_argument("--mesh-dir", type=Path, default=DEFAULT_MESH_DIR, help="Directory containing *.msh")
    p.add_argument("--cases", type=str, default="", help="Comma-separated case filter, e.g. case1A,case2E")
    p.add_argument("--abc", type=str, default="auto", choices=["auto", "pml", "sm", "none"],
                   help="Absorbing boundary mode selection")
    p.add_argument("--backend", type=str, default="petsc", choices=["petsc", "hypre"],
                   help="Linear solver backend")
    p.add_argument(
        "--preset",
        type=str,
        default="",
        choices=[""] + sorted(PRESET_MAP.keys()),
        help="Preconditioner preset name. When set, backend/petsc-options are auto-filled.",
    )
    p.add_argument(
        "--krylov",
        type=str,
        default="gmres",
        choices=sorted(KRYLOV_MAP.keys()),
        help="Krylov method to pair with --preset's preconditioner: gmres or cocg "
             "(complex-symmetric CG, -ksp_type cg -ksp_cg_type symmetric). "
             "Ignored by the 'dryrun' preset, which always uses gmres.",
    )
    p.add_argument("--freefem-bin", type=str, default="FreeFem++-mpi", help="FreeFEM executable")
    p.add_argument("--run", action="store_true", help="Actually run FreeFEM; otherwise dry-run")
    p.add_argument("--list", action="store_true", help="List tasks and exit")
    p.add_argument("--save-vtk", action="store_true", help="Save .vtu files")
    p.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR, help="Directory for logs and VTK")
    p.add_argument("--petsc-options", type=str,
                   default=DEFAULT_PETSC_OPTIONS,
                   help="PETSc KSP/PC option string")
    p.add_argument("--list-presets", action="store_true", help="List available preconditioner presets and exit")
    p.add_argument("--timeout", type=int, default=3600,
                   help="Per-case FreeFEM wall-clock timeout in seconds (0 = no timeout, default 3600)")
    p.add_argument("--accel-ic-alpha", type=float, default=1.5,
                   help="Acceleration factor for --preset accel_ic (multiplies each "
                        "row's ORIGINAL diagonal before elimination; 1.0=plain IC(0), "
                        "no scaling; empirically on case2A, 1.0-1.2 are WORSE than no "
                        "preconditioner at all, 1.5 is the first value that helps at "
                        "all (modestly) -- default 1.5, tune per case)")
    p.add_argument("--hx-smoother-omega", type=float, default=1.0,
                   help="Jacobi-smoother damping factor for --preset hx's first "
                        "(smoother) term; default 1.0")
    p.add_argument("--gmres-restart", type=int, default=None,
                   help="Restart cycle length for every hand-rolled GMRES driver "
                        "(cslp/accel_ic/hx/cslp_hx); default 300 (raised from a "
                        "hardcoded 30 after confirming empirically that restart=30 "
                        "caused stagnation, not a genuine method/preconditioner "
                        "limitation -- see problem_settings.md)")
    p.add_argument("--outer-max-it", type=int, default=None,
                   help="Override the hand-rolled outer solver's max iterations "
                        "(cslp/accel_ic/hx presets; default 4000, matching every "
                        "PETSc-backed preset's -ksp_max_it convention)")
    p.add_argument("--max-it", type=int, default=None,
                   help="Override -ksp_max_it of the PETSc-backed presets (default: the "
                        "preset's own value, 4000)")
    return p.parse_args()


def apply_preset(args: argparse.Namespace) -> None:
    if args.preset in ("cslp", "cslp_mg"):
        args.outer_method = "cslp"
    elif args.preset == "accel_ic":
        args.outer_method = "accel_ic"
    elif args.preset == "hx":
        args.outer_method = "hx"
    elif args.preset in ("cslp_hx", "cslp_hx_mg"):
        args.outer_method = "cslp_hx"
    else:
        args.outer_method = "petsc"

    if not args.preset:
        return

    cfg = PRESET_MAP[args.preset]

    # Preset has priority: consistent reproducibility for benchmarking.
    args.backend = cfg["backend"]
    if args.preset in ("accel_ic", "hx", "cslp_hx", "cslp_mg", "cslp_hx_mg"):
        # Fully/partly hand-rolled outer loop; petsc_options for "hx"/
        # "cslp_hx" is the auxiliary-solve string (see PRESET_MAP), used
        # verbatim, not prefixed by --krylov (both are GMRES-only, like
        # cslp). "accel_ic" unused entirely -- --krylov DOES apply there
        # (selects gmres_precon.idp vs cocg_precon.idp inside the .edp),
        # unlike cslp/hx/cslp_hx/dryrun.
        args.petsc_options = cfg["petsc_options"]
    elif args.krylov == "cocg" and args.preset != "dryrun":
        # PETSc PC applied once per iteration (preonly) + hand-rolled COCG
        # (outerMethod "pc_cocg"; see the note above KRYLOV_MAP).
        args.outer_method = "pc_cocg"
        pc_opts = re.sub(r"-ksp_(rtol|max_it) \S+", "", cfg["petsc_options"]).strip()
        args.petsc_options = f"-ksp_type preonly {pc_opts}"
    elif args.preset in ("dryrun", "cslp"):
        # dryrun bakes in its own -ksp_type gmres; it is a pipeline smoke test,
        # not part of the GMRES-vs-COCG comparison. cslp's petsc_options is the
        # INNER shifted-matrix solve, not the outer KSP -- --krylov and the
        # -ksp_monitor/-ksp_converged_reason suffix below don't apply to it
        # (the .edp prints its own matching-format monitor/reason lines).
        args.petsc_options = cfg["petsc_options"]
    else:
        # -ksp_monitor/-ksp_converged_reason are appended unconditionally (not
        # just for dryrun) so every performance-comparison run also emits a
        # per-iteration residual history and final iteration count/reason --
        # this is what generate_convergence_report.py parses out of the log.
        restart = getattr(args, "gmres_restart", None) or DEFAULT_GMRES_RESTART
        pc_opts = cfg["petsc_options"]
        max_it = getattr(args, "max_it", None)
        if max_it:
            pc_opts = re.sub(r"-ksp_max_it \d+", f"-ksp_max_it {max_it}", pc_opts)
        args.petsc_options = (
            f"{KRYLOV_MAP[args.krylov].format(restart=restart)} {pc_opts} "
            "-ksp_monitor -ksp_converged_reason"
        )


def load_case_params() -> Dict:
    with CASE_PARAM_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_mesh_tasks(mesh_dir: Path) -> List[MeshTask]:
    tasks: List[MeshTask] = []
    for msh in sorted(mesh_dir.glob("case*.msh")):
        stem = msh.stem
        m = re.match(r"^(case[0-9][A-Z])_(.+)$", stem)
        if not m:
            continue
        tasks.append(MeshTask(case_name=m.group(1), param_set=m.group(2), mesh_path=msh))
    return tasks


def filter_tasks(tasks: List[MeshTask], case_filter: str) -> List[MeshTask]:
    if not case_filter.strip():
        return tasks
    selected = {c.strip() for c in case_filter.split(",") if c.strip()}
    return [t for t in tasks if t.case_name in selected]


def parse_physical_names(msh_file: Path) -> Dict[Tuple[int, str], int]:
    names: Dict[Tuple[int, str], int] = {}
    with msh_file.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    try:
        i0 = lines.index("$PhysicalNames\n")
    except ValueError:
        return names

    n = int(lines[i0 + 1].strip())
    for i in range(i0 + 2, i0 + 2 + n):
        line = lines[i].strip()
        m = re.match(r"^(\d+)\s+(\d+)\s+\"(.+)\"$", line)
        if not m:
            continue
        dim = int(m.group(1))
        tag = int(m.group(2))
        name = m.group(3)
        names[(dim, name)] = tag
    return names


def pick_k0(case_name: str, params: Dict) -> float:
    # An explicit "k0" (operating wavenumber) takes precedence: used where the
    # operating point was moved off an accidental resonance (resonance_check.py)
    # without touching lambda0, which also scales the .geo templates.
    if "k0" in params:
        return float(params["k0"])
    lambda0 = float(params.get("lambda0", 1.0))
    if case_name in {"case1A", "case1B"} and "k0R" in params and "R" in params:
        return float(params["k0R"]) / float(params["R"])
    return 2.0 * 3.141592653589793 / lambda0


DEFAULT_OUTER_METHOD = "petsc"
DEFAULT_CSLP_BETA1 = 1.0    # standard CSLP shift (Erlangga/Vuik/Oosterlee-style)
DEFAULT_CSLP_BETA2 = 0.5
DEFAULT_OUTER_RTOL = 1.0e-8   # matches the rtol used by every other preset
DEFAULT_OUTER_MAXIT = 4000
DEFAULT_ACCEL_IC_ALPHA = 1.5
DEFAULT_HX_SMOOTHER_OMEGA = 1.0
# Restart cycle length for every hand-rolled GMRES driver (cslp/accel_ic/hx/
# cslp_hx). Was hardcoded to 30 in every .edp; raised to 300 after confirming
# empirically (case2F:plex7, accel_ic+GMRES) that restart=30 was causing
# genuine stagnation, not a real preconditioner/method limitation -- restart=
# 300 converged in 282 iterations where restart=30 still hadn't converged
# after 2000. A short restart discards the Krylov subspace's accumulated
# approximate-eigenspace information every cycle, which can stall badly on
# non-normal operators (this project's complex-symmetric but indefinite
# curl-curl - k^2*eps matrix); COCG's unrestarted 3-term recurrence never had
# this problem, which is why some "COCG beats GMRES" results in this project
# were actually "GMRES(30) stagnates" artifacts, not genuine method
# superiority. Larger restart costs more memory/orthogonalization per cycle,
# so this remains user-overridable, not a free win.
DEFAULT_GMRES_RESTART = 300
# Target normal-incidence reflection coefficient of the UPML profile
# (EMAG_PML_R0 overrides it, for PML studies). 1e-4 chosen 2026-09-28 on
# case1A (direct solves): the inner-box field energy of tPML = 0.5 and 0.75
# agree to 0.5% (1e-6: 1.5%, 1e-3: 1.4%), while CSLP converges ~7x further in
# 300 s than with 1e-6 (sigmaMax/k0 = 4.4 instead of 6.6 at tPML = 0.5: less
# extreme anisotropic PML coefficients for the inner AMG).
PML_R0 = float(os.environ.get("EMAG_PML_R0", "1.0e-4"))


def build_runtime_config(task: MeshTask, params: Dict, phys: Dict[Tuple[int, str], int],
                         abc_mode: str, backend: str, petsc_options: str,
                         save_vtk: bool, result_dir: Path,
                         outer_method: str = DEFAULT_OUTER_METHOD,
                         cslp_beta1: float = DEFAULT_CSLP_BETA1,
                         cslp_beta2: float = DEFAULT_CSLP_BETA2,
                         outer_rtol: float = DEFAULT_OUTER_RTOL,
                         outer_max_it: int = DEFAULT_OUTER_MAXIT,
                         krylov_method: str = "gmres",
                         accel_ic_alpha: float = DEFAULT_ACCEL_IC_ALPHA,
                         hx_smoother_omega: float = DEFAULT_HX_SMOOTHER_OMEGA,
                         gmres_restart: int = DEFAULT_GMRES_RESTART,
                         sol_save_file: str = "", sol_ref_file: str = "") -> str:
    """runtime_case_config.idp text. sol_save_file / sol_ref_file (solution_check.idp):
    write the solution vector to / compute the errors against a reference
    solution read from that path ('' = off, the default)."""
    vol = {name: tag for (dim, name), tag in phys.items() if dim == 3}
    sur = {name: tag for (dim, name), tag in phys.items() if dim == 2}

    has_pml = any(k.startswith("PML_") for k in vol)

    if abc_mode == "pml":
        use_pml, use_sm = 1, 0
    elif abc_mode == "sm":
        use_pml, use_sm = 0, 1
    elif abc_mode == "none":
        use_pml, use_sm = 0, 0
    else:
        # auto mode
        if has_pml:
            use_pml, use_sm = 1, 0
        elif "OuterBoundary" in sur or "PortOut" in sur:
            use_pml, use_sm = 0, 1
        else:
            use_pml, use_sm = 0, 0

    pec_candidates = [
        "PEC", "PECWall", "PEC_Sphere", "PEC_Cavity", "PortIn"
    ]
    # With a PML, the outer face of the PML shell is PEC-backed (standard
    # truncation of a PML); without one, OuterBoundary is a Silver-Mueller face.
    if use_pml:
        pec_candidates = pec_candidates + ["OuterBoundary"]
    sm_candidates = ["OuterBoundary", "PortOut"] if not use_pml else ["PortOut"]

    pec_labels = [sur[name] for name in pec_candidates if name in sur][:8]
    sm_labels = [sur[name] for name in sm_candidates if name in sur][:4]

    while len(pec_labels) < 8:
        pec_labels.append(-1)
    while len(sm_labels) < 4:
        sm_labels.append(-1)

    lambda0 = float(params.get("lambda0", 1.0))
    k0 = pick_k0(task.case_name, params)
    # Anisotropic UPML (see maxwell_edge03d_solver.edp): the PML is every point
    # outside the core box, identified by coordinates (so the corner/edge slabs
    # of the telescoping PML geometry get the product of the relevant stretches).
    # Quadratic profile sigma(d) = sigmaMax*(d/t)^2 with the classical choice
    # sigmaMax = (m+1)*ln(1/R0)/(2t), m=2, target normal-incidence reflection
    # R0 = PML_R0.
    pml_t = float(params.get("tPML", 1.0))
    if "Lc" in params:      # case1C: two Lc-long chambers along x, Lc x Lc section
        lc_ = float(params["Lc"])
        core = (-lc_, lc_, -lc_ / 2, lc_ / 2, -lc_ / 2, lc_ / 2)
    else:                   # case1A/1B: cube [-L/2, L/2]^3
        half = float(params.get("L", 4.0)) / 2
        core = (-half, half, -half, half, -half, half)
    pml_sigma_max = 3.0 * math.log(1.0 / PML_R0) / (2.0 * pml_t)

    src_x, src_y, src_z, src_w = source_for(task.case_name, params)

    eps_sphere = float(params.get("epsSphere", 10.0))
    kappa = float(params.get("kappa", 10.0))
    eps_lossy = float(params.get("epsLossy", 10.0))
    tan_delta = float(params.get("tanDelta", 0.1))
    vloss = float(params.get("vloss", 0.1))

    vtk_real = (result_dir / f"{task.case_name}_{task.param_set}_E_real.vtu").as_posix()
    vtk_imag = (result_dir / f"{task.case_name}_{task.param_set}_E_imag.vtu").as_posix()

    def vol_tag(name: str) -> int:
        return int(vol.get(name, -1))

    lines = [
        "// Auto-generated by run_freefem_batch.py",
        f"string caseName = \"{task.case_name}\";",
        f"string paramSetName = \"{task.param_set}\";",
        f"string meshFile = \"{task.mesh_path.as_posix()}\";",
        "",
        f"string backend = \"{backend}\";",
        f"string petscOptions = \"{petsc_options}\";",
        "",
        f"string outerMethod = \"{outer_method}\";",
        f"string krylovMethod = \"{krylov_method}\";",
        f"real cslpBeta1 = {cslp_beta1};",
        f"real cslpBeta2 = {cslp_beta2};",
        f"real outerRtol = {outer_rtol};",
        f"int outerMaxIt = {outer_max_it};",
        f"real accelIcAlpha = {accel_ic_alpha};",
        f"real hxSmootherOmega = {hx_smoother_omega};",
        f"int gmresRestartCfg = {gmres_restart};",
        "",
        f"real lambda0 = {lambda0};",
        f"real k0 = {k0};",
        "",
        f"int usePML = {use_pml};",
        f"int useSM = {use_sm};",
        f"real pmlThick = {pml_t};",
        f"real pmlSigmaMax = {pml_sigma_max};",
        f"real pmlXmin = {core[0]}; real pmlXmax = {core[1]};",
        f"real pmlYmin = {core[2]}; real pmlYmax = {core[3]};",
        f"real pmlZmin = {core[4]}; real pmlZmax = {core[5]};",
        "",
        "real srcAmp = 1.0;",
        f"real srcX0 = {src_x};",
        f"real srcY0 = {src_y};",
        f"real srcZ0 = {src_z};",
        # Default 0.25*lambda0 (scaled by lambda0 so case2F's real-mm geometry
        # gets a ~30mm Gaussian, not a sub-element 0.25mm one); see source_for()
        # for the per-case exceptions.
        f"real srcWidth = {src_w};",
        "",
        f"int saveVtk = {1 if save_vtk else 0};",
        f"string vtkOutReal = \"{vtk_real}\";",
        f"string vtkOutImag = \"{vtk_imag}\";",
        "",
        f"real epsSphere = {eps_sphere};",
        f"real kappa = {kappa};",
        "real epsPTFE = 2.1;",
        "real epsAlumina = 9.8;",
        f"real epsRods = {float(params.get('epsRods', 50.0))};",
        f"real epsLossy = {eps_lossy};",
        f"real tanDelta = {tan_delta};",
        f"real vloss = {vloss};",
        "",
        f"int labCoreAir = {vol_tag('CoreAir')};",
        f"int labSphereDielectric = {vol_tag('SphereDielectric')};",
        f"int labLayer2 = {vol_tag('Layer2_CeramicOrHighK')};",
        f"int labPTFE = {vol_tag('PTFE')};",
        f"int labAlumina = {vol_tag('Alumina')};",
        f"int labEps1 = {vol_tag('Eps1')};",
        f"int labEps100 = {vol_tag('Eps100')};",
        f"int labRodsHighEps = {vol_tag('RodsHighEps')};",
        f"int labLossyMaterial = {vol_tag('LossyMaterial')};",
        f"int labLossy = {vol_tag('Lossy')};",
        f"int labHighK = {vol_tag('HighK')};",
        "",
        f"int labPMLXP = {vol_tag('PML_X_Plus')};",
        f"int labPMLXM = {vol_tag('PML_X_Minus')};",
        f"int labPMLYP = {vol_tag('PML_Y_Plus')};",
        f"int labPMLYM = {vol_tag('PML_Y_Minus')};",
        f"int labPMLZP = {vol_tag('PML_Z_Plus')};",
        f"int labPMLZM = {vol_tag('PML_Z_Minus')};",
        "",
        f"int pecLabel1 = {pec_labels[0]};",
        f"int pecLabel2 = {pec_labels[1]};",
        f"int pecLabel3 = {pec_labels[2]};",
        f"int pecLabel4 = {pec_labels[3]};",
        f"int pecLabel5 = {pec_labels[4]};",
        f"int pecLabel6 = {pec_labels[5]};",
        f"int pecLabel7 = {pec_labels[6]};",
        f"int pecLabel8 = {pec_labels[7]};",
        "",
        f"int smLabel1 = {sm_labels[0]};",
        f"int smLabel2 = {sm_labels[1]};",
        f"int smLabel3 = {sm_labels[2]};",
        f"int smLabel4 = {sm_labels[3]};",
        "",
        "// Solution save / error against a reference (solution_check.idp; '' = off)",
        f"string solSaveFile = \"{sol_save_file}\";",
        f"string solRefFile = \"{sol_ref_file}\";",
        "",
    ]

    return "\n".join(lines)


def run_task(task: MeshTask, case_db: Dict, args: argparse.Namespace) -> int:
    if task.case_name not in case_db:
        print(f"[WARN] Missing case definition in JSON: {task.case_name}")
        return 1

    psets = case_db[task.case_name].get("parameter_sets", {})
    if task.param_set not in psets:
        print(f"[WARN] Missing parameter set in JSON: {task.case_name}:{task.param_set}")
        return 1

    params = psets[task.param_set]
    phys = parse_physical_names(task.mesh_path)

    config_text = build_runtime_config(
        task=task,
        params=params,
        phys=phys,
        abc_mode=args.abc,
        backend=args.backend,
        petsc_options=args.petsc_options,
        save_vtk=args.save_vtk,
        result_dir=args.result_dir,
        outer_method=getattr(args, "outer_method", DEFAULT_OUTER_METHOD),
        krylov_method=getattr(args, "krylov", "gmres"),
        accel_ic_alpha=getattr(args, "accel_ic_alpha", DEFAULT_ACCEL_IC_ALPHA),
        hx_smoother_omega=getattr(args, "hx_smoother_omega", DEFAULT_HX_SMOOTHER_OMEGA),
        outer_max_it=getattr(args, "outer_max_it", None) or DEFAULT_OUTER_MAXIT,
        gmres_restart=getattr(args, "gmres_restart", None) or DEFAULT_GMRES_RESTART,
    )
    CONFIG_FILE.write_text(config_text, encoding="utf-8")

    cmd = [args.freefem_bin, str(SOLVER_EDP)]
    print(f"[RUN] {task.case_name}:{task.param_set} -> {task.mesh_path.name}")
    print(f"      cmd: {' '.join(cmd)}")

    if not args.run:
        return 0

    args.result_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.result_dir / f"{task.case_name}_{task.param_set}.log"

    with log_path.open("w", encoding="utf-8") as logf:
        try:
            p = subprocess.run(
                cmd, cwd=FREEFEM_DIR, stdout=logf, stderr=subprocess.STDOUT,
                timeout=args.timeout if args.timeout > 0 else None,
            )
            returncode = p.returncode
        except subprocess.TimeoutExpired:
            logf.write(f"\n[TIMEOUT] exceeded {args.timeout}s\n")
            returncode = 124

    # PETSc KSP/PC setup failures (e.g. BDDC requiring a MATIS matrix) can print
    # a fatal "PETSC ERROR" while FreeFEM itself still exits 0 and reports a
    # bogus (typically all-zero) solution -- returncode alone silently passes
    # these through as successes, so scan the log for that marker too.
    petsc_error = False
    if returncode == 0:
        with log_path.open("r", encoding="utf-8", errors="ignore") as logf:
            petsc_error = "PETSC ERROR" in logf.read()

    if returncode != 0 or petsc_error:
        reason = f"return code {returncode}" if returncode != 0 else "PETSC ERROR found in log despite return code 0"
        print(f"[FAIL] {reason}, log={log_path}")
        return returncode if returncode != 0 else 1
    else:
        print(f"[ OK ] log={log_path}")
        return returncode


def main() -> int:
    args = parse_args()

    if args.list_presets:
        print("Available presets (preconditioner only; combine with --krylov gmres|cocg):")
        for name in sorted(PRESET_MAP.keys()):
            cfg = PRESET_MAP[name]
            print(f"  {name:12s} backend={cfg['backend']:5s} opts={cfg['petsc_options']}")
        print("\nAvailable --krylov choices:")
        for name in sorted(KRYLOV_MAP.keys()):
            print(f"  {name:12s} {KRYLOV_MAP[name]}")
        return 0

    apply_preset(args)

    if args.preset:
        print(f"[INFO] preset={args.preset} backend={args.backend}")
        print(f"[INFO] petsc-options={args.petsc_options}")

    case_db = load_case_params()

    tasks = discover_mesh_tasks(args.mesh_dir)
    tasks = filter_tasks(tasks, args.cases)

    if not tasks:
        print("No mesh tasks found.")
        return 1

    if args.list:
        for t in tasks:
            print(f"{t.case_name}:{t.param_set} -> {t.mesh_path}")
        print(f"Total: {len(tasks)} tasks")
        return 0

    n_ok = 0
    n_fail = 0
    for task in tasks:
        rc = run_task(task, case_db, args)
        if rc == 0:
            n_ok += 1
        else:
            n_fail += 1

    print("==========================================")
    print(f"Done. success={n_ok}, failed={n_fail}, total={len(tasks)}")
    print("==========================================")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
