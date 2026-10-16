#!/usr/bin/env python3
"""Matrix features of the benchmark systems (docs/matrix_features.md).

Exports the system matrix A of a parameter set with pcb_matrix_export.edp
(the solver's aMaxwell, no solve) and computes, on the free DOFs (the PEC
on() penalty rows |A_ii| > 1e20 removed):

  structure   n, nnz/row, |diag| range, fraction of diagonally dominant rows
  symmetry    ||A - A^T||_F/||A||_F (complex symmetry, COCG), A = R + iS with
              R = Re A, S = Im A real symmetric (Hermitian / skew-Hermitian
              parts): ||S||_F/||A||_F, non-normality
              ||A A^H - A^H A||_F/||A||_F^2 = 2 ||RS - SR||_F/||A||_F^2
  definiteness  inertia of R (LDL^T, Sylvester), lambda_min/max(S) (S >= 0:
              passive), optionally the field of values,
              max_theta lambda_min(cos(t) R + sin(t) S) (> 0: 0 not in W(A))
  kernel      N_grad = rank of G on the free edges / nodes; beta = dim ker K0
              - N_grad (discrete harmonic fields of the plain curl-curl K0,
              gradient-deflated shift-invert); PEC components (beta >=
              components - 1); modes below k0 = negative eigenvalues of R
              beyond dim ker K0 (closed, weakly lossy)
  resonance   modes of (A + k0^2 Meps, Meps) nearest k0 (gradient-deflated
              shift-invert), relative distance and Q
  spectrum    sigma_max, the smallest singular values (svds of A^-1 with one
              factorization), kappa_2, also of the Jacobi-scaled
              |D|^-1/2 A |D|^-1/2; eigenvalues of A nearest 0 (shift-invert)

Sets: PCB parameter sets (P05-1) or existing benchmark cases (case2A:standard).

Backends of the factorizations:
  superlu   scipy only (python3); fine up to ~6e4 DOFs
  mumps     MUMPS through petsc4py built on FreeFEM's complex PETSc; run with
            that interpreter (~/venvs/ff-petsc-c/bin/python). The inertia of R
            needs the real PETSc: a subprocess with --real-python
            (~/venvs/ff-petsc-r/bin/python). Building both: docs/matrix_features.md 4.1.

  python3 freefem/pcb/matrix_features.py --sets P05-1
  ~/venvs/ff-petsc-c/bin/python freefem/pcb/matrix_features.py --backend mumps --sets P03-1
  python3 freefem/pcb/matrix_features.py --sets case2A:standard
  python3 freefem/pcb/matrix_features.py --sets P05-1 --fov 8      # + field of values (slow)

Results: <out>/<host>/<set>.json (host from pcb_host).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.sparse.csgraph import connected_components

PCB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PCB_DIR))
import run_pcb_benchmark as rpb  # noqa: E402

PENALTY = 1.0e20
EXPORT_EDP = "pcb_matrix_export.edp"
REAL_PYTHON = Path.home() / "venvs" / "ff-petsc-r" / "bin" / "python"


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def load_bin(path: Path) -> sp.csr_matrix:
    """[n, m, nnz, I, J, Re, Im] written by pcb_matrix_export.edp (SaveVec)."""
    with open(path, "rb") as f:
        np.fromfile(f, dtype="<i8", count=1)
        v = np.fromfile(f, dtype="<f8")
    n, m, nz = (int(x) for x in v[:3])
    i, j = v[3:3 + nz].astype(np.int64), v[3 + nz:3 + 2 * nz].astype(np.int64)
    c = v[3 + 2 * nz:3 + 3 * nz] + 1j * v[3 + 3 * nz:3 + 4 * nz]
    keep = (i < n) & (j < m)   # MatrixEdgeP1 stores a zero at (n, m), one past the end
    return sp.csr_matrix((c[keep], (i[keep], j[keep])), shape=(n, m))


def export(pset: str, scratch: Path, freefem_bin: str) -> Path:
    work = scratch / pset.replace(":", "_")
    if ":" in pset:   # existing benchmark case, built as run_pcb_benchmark.py regress does
        case, ps = pset.split(":")
        db = rpb.rfb.load_case_params()
        task = rpb.rfb.MeshTask(case_name=case, param_set=ps,
                                mesh_path=rpb.rfb.DEFAULT_MESH_DIR / f"{case}_{ps}.msh")
        rpb.build_job_dir(work, rpb.PCB_SOLVER, task, db[case]["parameter_sets"][ps], "mumps", "direct", 1)
    else:
        cases = rpb.load_pcb_cases()
        prob = next(p for p, d in cases.items() if pset in d["parameter_sets"])
        pdef = cases[prob]
        job = rpb.PcbJob(prob, pset, pdef, pdef["parameter_sets"][pset], rpb.PCB_MESH_DIR, "")
        rpb.make_pcb_build_job_dir({(prob, job.key): job})(work, job.task, None, "mumps", "direct", 1e-8)
    shutil.copy(PCB_DIR / EXPORT_EDP, work / EXPORT_EDP)
    p = subprocess.run([freefem_bin, "-nw", "-v", "0", EXPORT_EDP], cwd=work, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (work / "export.log").write_text(p.stdout)
    if "EXPORT_DONE" not in p.stdout:
        raise RuntimeError(f"export failed, see {work / 'export.log'}")
    return work


# ---------------------------------------------------------------------------
# Factorizations: .solve(x) = M^-1 x, .solve_h(x) = M^-H x
# ---------------------------------------------------------------------------
class SuperLU:
    def __init__(self, M: sp.spmatrix, symmetric: bool = True):
        self.lu = sla.splu(M.tocsc())

    def solve(self, x):
        return self.lu.solve(x)

    def solve_h(self, x):
        return self.lu.solve(x, trans="H")


class Mumps:
    """MUMPS LDL^T (complex symmetric, the matrices here are all symmetric)
    or LU through petsc4py on FreeFEM's complex PETSc. M^-H x = conj(M^-1
    conj(x)) for a complex symmetric M, so one factorization serves both."""

    def __init__(self, M: sp.spmatrix, symmetric: bool = True):
        from petsc4py import PETSc
        self.PETSc = PETSc
        M = M.tocsr().astype(complex)
        self.real = False
        self.sym = symmetric
        self.A = PETSc.Mat().createAIJ(size=M.shape, csr=(M.indptr.astype(PETSc.IntType),
                                                           M.indices.astype(PETSc.IntType), M.data))
        if symmetric:
            self.A.setOption(PETSc.Mat.Option.SYMMETRIC, True)
        self.ksp = PETSc.KSP().create()
        self.ksp.setOperators(self.A)
        self.ksp.setType("preonly")
        pc = self.ksp.getPC()
        pc.setType("cholesky" if symmetric else "lu")
        pc.setFactorSolverType("mumps")
        self.ksp.setUp()
        self.x, self.b = self.A.createVecs()

    def solve(self, x):
        isreal = not np.iscomplexobj(x)
        self.b.setArray(np.asarray(x, dtype=complex))
        self.ksp.solve(self.b, self.x)
        y = self.x.getArray().copy()
        return y.real if isreal else y

    def solve_h(self, x):
        if not self.sym:
            raise NotImplementedError
        return np.conj(self.solve(np.conj(x)))


def inertia_superlu(R: sp.spmatrix) -> dict:
    """LU with diagonal pivots and a symmetric ordering (= LDL^T of P R P^T).
    Valid only if SuperLU kept the diagonal pivots (perm_r == perm_c)."""
    lu = sla.splu(R.tocsc(), permc_spec="MMD_AT_PLUS_A", diag_pivot_thresh=0.0,
                  options=dict(SymmetricMode=True))
    ok = bool(np.array_equal(lu.perm_r, lu.perm_c))
    d = lu.U.diagonal()
    tiny = np.abs(d) < 1e-14 * np.abs(d).max()
    return dict(neg=int(np.sum((d < 0) & ~tiny)), zero=int(np.sum(tiny)),
                pos=int(np.sum((d > 0) & ~tiny)), diagonal_pivots=ok)


def inertia_mumps_real(path: Path) -> dict:
    """Run in the real-PETSc interpreter (--inertia-of): MUMPS LDL^T inertia."""
    from petsc4py import PETSc
    R = sp.load_npz(path).tocsr()
    P = PETSc.Mat().createAIJ(size=R.shape, csr=(R.indptr.astype(PETSc.IntType),
                                                 R.indices.astype(PETSc.IntType), R.data))
    P.setOption(PETSc.Mat.Option.SYMMETRIC, True)
    PETSc.Options().setValue("mat_mumps_icntl_24", 1)   # null pivots, required by MatGetInertia
    ksp = PETSc.KSP().create()
    ksp.setOperators(P)
    ksp.setType("preonly")
    pc = ksp.getPC()
    pc.setType("cholesky")
    pc.setFactorSolverType("mumps")
    pc.setFromOptions()
    ksp.setUp()
    neg, zero, pos = pc.getFactorMatrix().getInertia()
    return dict(neg=int(neg), zero=int(zero), pos=int(pos), diagonal_pivots=True)


def inertia(R: sp.spmatrix, backend: str, work: Path, real_python: Path) -> dict:
    if backend == "superlu":
        return inertia_superlu(R)
    path = work / "R.npz"
    sp.save_npz(path, R.tocsr())
    p = subprocess.run([str(real_python), __file__, "--inertia-of", str(path)], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    path.unlink()
    line = [l for l in p.stdout.splitlines() if l.startswith("INERTIA ")]
    if not line:
        raise RuntimeError(f"inertia subprocess failed:\n{p.stdout[-2000:]}")
    return json.loads(line[-1][len("INERTIA "):])


# ---------------------------------------------------------------------------
# Eigenvalue helpers
# ---------------------------------------------------------------------------
def lam_ext(Hs: sp.spmatrix, which: str, tol: float = 1e-6) -> float:
    return float(sla.eigsh(Hs, k=1, which=which, tol=tol, maxiter=20000,
                           return_eigenvectors=False)[0])


def lam_min(Hs: sp.spmatrix, Fac, sigma: float | None = None, maxiter: int | None = None) -> float | None:
    """Smallest eigenvalue of a real symmetric matrix by shift-invert below
    the spectrum (Hs - sigma I positive definite, the eigenvalue nearest sigma
    is the smallest). Default sigma: just below the Gershgorin lower bound
    (safe, but slow when the bound is far from lambda_min, e.g. mass-like S);
    for a matrix known to be >= 0 (inertia), sigma slightly below 0 is fast.
    Plain Lanczos ('SA') stalls on the near-zero clusters of S (lossless air).
    None if ARPACK does not converge within maxiter."""
    Hs = Hs.tocsr()
    if sigma is None:
        dg = Hs.diagonal()
        lower = float(np.min(dg - (np.asarray(abs(Hs).sum(axis=1)).ravel() - np.abs(dg))))
        sigma = lower - 1e-3 * max(abs(lower), 1e-300)
    f = Fac((Hs - sigma * sp.identity(Hs.shape[0], format="csr")).tocsr())
    op = sla.LinearOperator(Hs.shape, dtype=float, matvec=lambda x: np.real(f.solve(x)))
    try:
        return float(sla.eigsh(Hs, k=1, sigma=sigma, which="LM", tol=1e-10, OPinv=op, maxiter=maxiter,
                               return_eigenvectors=False)[0])
    except sla.ArpackNoConvergence:
        return None


class Timer:
    def __init__(self):
        self.t = {}

    def __call__(self, name, fn, *a, **k):
        t0 = time.time()
        out = fn(*a, **k)
        self.t[name] = round(time.time() - t0, 2)
        return out


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
def features(work: Path, n_sv: int, n_theta: int, backend: str, real_python: Path,
             n_modes: int = 6, open_modes: bool = False) -> dict:
    Fac = Mumps if backend == "mumps" else SuperLU
    tm = Timer()
    A = tm("load", load_bin, work / "A.bin")
    K0, M0, G = (load_bin(work / f).real for f in ("K0.bin", "M0.bin", "G.bin"))
    pec_node = np.loadtxt(work / "pecnode.txt", skiprows=1).astype(bool)
    k0sq = next(float(l.split()[1]) for l in (work / "export.log").read_text().splitlines()
                if l.startswith("K0_SQ"))

    free = np.abs(A.diagonal()) < PENALTY
    Af = A[free][:, free].tocsr()
    n = Af.shape[0]
    out = dict(backend=backend, n_total=A.shape[0], n_penalty_rows=int((~free).sum()), n=n,
               nnz=int(Af.nnz), nnz_per_row=round(Af.nnz / n, 2), k0_sq=k0sq)

    # structure
    d = Af.diagonal()
    offsum = np.asarray(abs(Af).sum(axis=1)).ravel() - np.abs(d)
    out["diag_abs_min"], out["diag_abs_max"] = float(np.abs(d).min()), float(np.abs(d).max())
    out["diag_dominant_fraction"] = float(np.mean(np.abs(d) >= offsum))
    out["diag_real_negative_fraction"] = float(np.mean(d.real < 0))

    # symmetry, Hermitian / skew-Hermitian parts, non-normality
    nA = sla.norm(Af)
    R, S = Af.real.tocsr(), Af.imag.tocsr()
    out["sym_rel"] = float(sla.norm(Af - Af.T) / nA)
    out["herm_rel"] = float(sla.norm(Af - Af.conj().T) / nA)
    out["imag_rel"] = float(sla.norm(S) / nA)
    out["nonnormal_rel"] = float(tm("nonnormal", lambda: 2 * sla.norm(R @ S - S @ R)) / nA ** 2)

    # inertia of R, extremes of S, field of values
    out["inertia_R"] = tm("inertia_R", inertia, R, backend, work, real_python)
    # S >= 0 (passive) is decided exactly by its inertia; lambda_min(S) then by
    # shift-invert just below 0, otherwise (PML) below the Gershgorin bound
    out.update(tm("S", s_features, S, Fac, backend, work, real_python))
    if n_theta:   # slow (one shift-invert Lanczos per angle)
        thetas = np.linspace(0, 2 * math.pi, n_theta, endpoint=False)
        lmins = tm("fov", lambda: [lam_min(math.cos(t) * R + math.sin(t) * S, Fac) for t in thetas])
        i = int(np.argmax(lmins))
        out["fov_dist0"] = float(lmins[i])      # > 0: 0 not in W(A); a lower bound of dist(0, W(A))
        out["fov_dist0_theta_deg"] = float(np.degrees(thetas[i]))

    # gradient kernel and topology (plain K0, M0, G on free edges / free nodes)
    fn = ~pec_node
    K0f, M0f = K0[free][:, free].tocsr(), M0[free][:, free].tocsr()
    # PEC components: P1 nodes on PEC joined by edges with both ends on PEC
    Gp = G[:, pec_node].tocsc()
    pe = np.asarray((abs(Gp) > 0).sum(axis=1)).ravel() == 2
    adj = (abs(Gp[pe]).T @ abs(Gp[pe])).tocsr()
    ncomp = connected_components(adj, directed=False)[0] if pec_node.any() else 0
    # components of free nodes not touching PEC (e.g. all-SIBC models) carry a
    # constant in ker G: pin one node of each, so that G has full column rank
    # (and G^T M G is invertible)
    adjall = (abs(G).T @ abs(G)).tocsr()
    _, lab = connected_components(adjall[fn][:, fn], directed=False)
    touching = set(lab[np.asarray(adjall[fn][:, pec_node].sum(axis=1)).ravel() > 0])
    fidx = np.flatnonzero(fn)
    keep = np.ones(fidx.size, dtype=bool)
    for c in sorted(set(lab) - touching):
        keep[np.flatnonzero(lab == c)[0]] = False
    Gf = G[free][:, fidx[keep]].tocsr()
    out["n_free_nodes"] = int(fn.sum())
    out["floating_components"] = int((~keep).sum())
    out["N_grad"] = int(keep.sum())
    out["pec_components"] = int(ncomp)

    # singular values: largest by svds(A), smallest via svds(A^-1) with one factorization
    out["sigma_max"] = float(tm("sigma_max", lambda: sla.svds(Af, k=1, which="LM", tol=1e-6,
                                                              return_singular_vectors=False)[0]))
    lu = tm("factor_A", Fac, Af)
    Ainv = sla.LinearOperator(Af.shape, dtype=complex, matvec=lu.solve, rmatvec=lu.solve_h)
    s = tm("sigma_min", lambda: sla.svds(Ainv, k=n_sv, which="LM", tol=1e-8,
                                         return_singular_vectors=False))
    smin = np.sort(1.0 / s)
    out["sigma_small"] = [float(v) for v in smin]
    out["sigma_min"] = float(smin[0])
    out["kappa_2"] = out["sigma_max"] / out["sigma_min"]
    # Jacobi-scaled Aj = Dj A Dj, Dj = |diag A|^-1/2: Aj^-1 = Dj^-1 A^-1 Dj^-1 (same factorization)
    dj = 1.0 / np.sqrt(np.abs(d))
    Aj = (sp.diags(dj) @ Af @ sp.diags(dj)).tocsr()
    sjmax = float(sla.svds(Aj, k=1, which="LM", tol=1e-6, return_singular_vectors=False)[0])
    Ajinv = sla.LinearOperator(Aj.shape, dtype=complex, matvec=lambda x: lu.solve(x / dj) / dj,
                               rmatvec=lambda x: lu.solve_h(x / dj) / dj)
    sjmin = 1.0 / float(tm("sigma_min_jacobi", lambda: sla.svds(
        Ajinv, k=1, which="LM", tol=1e-8, return_singular_vectors=False)[0]))
    out["kappa_2_jacobi"] = sjmax / sjmin
    # capped at n_sv (then ">= n_sv")
    out["n_sigma_below_1e-3_sigma_max"] = int(np.sum(smin < 1e-3 * out["sigma_max"]))

    # eigenvalues of A nearest 0
    Ainv0 = sla.LinearOperator(Af.shape, dtype=complex, matvec=lu.solve)
    lam, V = tm("eig0", lambda: sla.eigs(Af, k=n_sv, sigma=0, which="LM", OPinv=Ainv0))
    o = np.argsort(np.abs(lam))
    lam, V = lam[o], V[:, o]
    out["eig_near0"] = [[float(v.real), float(v.imag)] for v in lam]
    # curl content of those eigenvectors: v^H K0 v / (k0^2 v^H M0 v); ~0 for a
    # gradient (low-frequency) near-null vector, ~eps_r (k_mode/k0)^2 for a
    # resonant mode
    out["eig_near0_curl_rayleigh"] = [
        float((np.vdot(v, K0f @ v) / (k0sq * np.vdot(v, M0f @ v))).real) for v in V.T]
    out["eig_near0_rel_sigma_max"] = float(abs(lam[0]) / out["sigma_max"])

    n_extra = max(4, int(ncomp))   # room for the harmonic fields (beta >= PEC components - 1)
    k0 = math.sqrt(k0sq)
    # beta = dim ker K0 - N_grad (topology: harmonic fields of the plain
    # curl-curl, >= PEC components - 1): the same deflated shift-invert on the
    # plain pencil (K0, M0) with T0 = P0 (K0 + s M0)^-1 M0 (positive definite),
    # where ker K0 / grad gives theta = 1/s exactly and every mode less.
    s0 = k0sq
    lu0 = tm("factor_plain", Fac, (K0f + s0 * M0f).tocsr())
    M0G = (M0f @ Gf).tocsr()
    L0lu = Fac((Gf.T @ M0G).tocsr())
    P0 = lambda y: y - Gf @ L0lu.solve(M0G.T @ y)
    T0 = sla.LinearOperator(K0f.shape, dtype=float, matvec=lambda x: np.real(P0(lu0.solve(M0f @ x))))
    # beta >= PEC components - 1: ask for more than that
    n_beta = max(n_extra, int(ncomp)) + 1
    th0 = tm("harmonic", lambda: sla.eigs(T0, k=n_beta, which="LM", return_eigenvectors=False))
    beta = int(np.sum(np.abs(th0 * s0 - 1.0) < 1e-6))
    out["beta_harmonic"] = beta if beta < n_beta else f">={beta}"
    out["dim_ker_K0"] = out["N_grad"] + beta
    # negative eigenvalues of Re A beyond ker K: modes below k0 (closed, weakly
    # lossy). Not with SIBC: its face term n_f i k0 eta0/Z_s, Z_s = (1+i) R_s,
    # has a large positive real part and lifts the gradients touching the
    # conductor faces out of the negative part of R.
    cfg = (work / "pcb_case_config.idp").read_text()
    m = re.search(r"sibcLabel1\s*=\s*(-?\d+)", cfg)
    out["has_sibc"] = bool(m and int(m.group(1)) >= 0)
    # open boundary (Silver-Mueller or UPML): the resonance search is not
    # robust there (docs/matrix_features.md 5.3); closed: PEC / PMC only
    rt = (work / "runtime_case_config.idp").read_text()
    out["open_boundary"] = any(re.search(rf"int {k}\s*=\s*1;", rt) for k in ("useSM", "usePML"))
    out["modes_below_k0_est"] = None if out["has_sibc"] else out["inertia_R"]["neg"] - out["dim_ker_K0"]
    # open cases: the search widens to 120 eigenvalues x 2 start vectors and took
    # hours at 3e5 DOFs (P01-1_t 6.7 h, 2026-10-12) for values that are not
    # robust and not tabulated (summarize_matrix_features.py); skipped unless
    # open_modes (--open-modes)
    if out["open_boundary"] and not open_modes:
        out["resonance_skipped"] = "open boundary"
    else:
        out.update(tm("modes", resonance, work, Af, free, lu, Fac, G, K0f, M0f, k0sq, n_modes, n_extra))
    out["times_s"] = tm.t
    return out


def resonance(work: Path, Af, free, lu, Fac, G, K0f, M0f, k0sq: float, n_modes: int,
              n_extra: int) -> dict:
    """Resonance proximity: modes of (A + k0^2 Meps) u = lambda Meps u nearest
    lambda = k0^2 (as resonance_check.edp; complex for lossy / open cases),
    k_j = sqrt(lambda_j).

    The gradient fields (lambda = 0, N_grad of them) can be nearer to k0^2 than
    the first mode, so shift-invert runs on T = P A^-1 Meps with the
    Meps-projector P = I - G L^-1 G^T Meps, L = G^T Meps G, which maps them to
    theta = 0; lambda = k0^2 + 1/theta. Only the gradients of nodes off PEC
    and off every face with a surface term (surfnode.txt: Silver-Mueller,
    ports, SIBC) are deflated: for those Kc G = 0 exactly, so every mode with
    lambda != 0 satisfies G^T Meps u = 0 and P leaves it unchanged. (Gradients
    of surface nodes are not in ker Kc; projecting them out destroys the
    modes, e.g. all of them with SIBC.) What remains of the curl-free fields
    -- the harmonic fields, shifted by port / SIBC terms, and near-gradients of
    functions almost constant on the surface-term faces (open cases) -- is told
    apart by the curl content of the eigenvector,
    r = |v^H K0 v| / (|lambda| v^H M0 v): about eps_r (>= 1) for a mode, small
    for a curl-free field; r < 0.5 is reported as quasi-static (heuristic).
    ARPACK with a fixed start vector and a wide Krylov space: with random
    starts, close non-normal clusters (open cases) gave different subsets from
    run to run."""
    pec_node = np.loadtxt(work / "pecnode.txt", skiprows=1).astype(bool)
    surf_node = np.loadtxt(work / "surfnode.txt", skiprows=1).astype(bool)
    Gi = G[free][:, ~pec_node & ~surf_node].tocsr()
    Me = load_bin(work / "Meps.bin")[free][:, free].tocsr()
    MeG = (Me @ Gi).tocsr()
    Llu = Fac((Gi.T @ MeG).tocsr())
    P = lambda y: y - Gi @ Llu.solve(MeG.T @ y)   # Me symmetric: G^T Me = (Me G)^T
    T = sla.LinearOperator(Af.shape, dtype=complex, matvec=lambda x: P(lu.solve(Me @ x)))
    k0 = math.sqrt(k0sq)

    def search(v0):
        # open cases: many quasi-static fields can lie nearer k0^2 than any
        # mode, so widen the search until a curl-rich mode is found
        for k in (n_modes + n_extra + 6, 60, 120):
            th, V = sla.eigs(T, k=k, ncv=max(2 * k + 1, 40), which="LM", v0=v0)
            lam = k0sq + 1.0 / th
            km = np.sqrt(lam.astype(complex))
            km = np.where(km.real < 0, -km, km)
            r = np.array([abs(np.vdot(v, K0f @ v)) / (abs(l) * np.vdot(v, M0f @ v).real)
                          for v, l in zip(V.T, lam)])
            if np.any(r >= 0.5):
                break
        return k, km, r

    k, km, r = search(np.ones(Af.shape[0], dtype=complex))
    # a second start vector: open cases have a near-continuum of quasi-static /
    # radiating fields around k0^2 and ARPACK may converge to different subsets;
    # the nearest mode is reported as stable only if both starts agree
    rng = np.random.default_rng(1)
    _, km2, r2 = search(rng.standard_normal(Af.shape[0]) + 1j * rng.standard_normal(Af.shape[0]))
    mode = lambda i: dict(f_rel=float(km[i].real / k0),
                          q=float(km[i].real / (2 * abs(km[i].imag))) if km[i].imag != 0 else None,
                          curl_ratio=float(r[i]))
    out = dict(n_deflated_gradients=int(Gi.shape[1]), n_eigs_searched=int(k))
    qs = np.flatnonzero(r < 0.5)
    out["quasi_static_modes"] = [mode(i) for i in qs[np.argsort(np.abs(km[qs]))]][:20]
    out["quasi_static_reldist"] = float(np.min(np.abs(km[qs] - k0)) / k0) if qs.size else None
    md = np.flatnonzero(r >= 0.5)
    md2 = np.flatnonzero(r2 >= 0.5)
    if md.size == 0:   # none among the k eigenvalues nearest k0^2
        out["modes_near_k0"], out["resonance_reldist"], out["resonance_stable"] = [], None, md2.size == 0
        return out
    o = md[np.argsort(np.abs(km[md] - k0))][:n_modes + 4]
    out["modes_near_k0"] = [mode(i) for i in o]
    near2 = km2[md2][np.argmin(np.abs(km2[md2] - k0))] if md2.size else None
    out["resonance_stable"] = bool(near2 is not None and abs(near2 - km[o[0]]) < 1e-3 * k0)
    out["resonance_reldist"] = float(abs(km[o[0]] - k0) / k0)
    return out


def patch_modes(path: Path, work: Path, backend: str, n_modes: int = 6) -> dict:
    """Recompute the resonance part (resonance()) of an existing result."""
    f = json.loads(path.read_text(encoding="utf-8"))
    Fac = Mumps if backend == "mumps" else SuperLU
    A = load_bin(work / "A.bin")
    free = np.abs(A.diagonal()) < PENALTY
    Af = A[free][:, free].tocsr()
    G = load_bin(work / "G.bin").real
    K0f, M0f = (load_bin(work / n).real[free][:, free].tocsr() for n in ("K0.bin", "M0.bin"))
    n_extra = max(4, int(f["pec_components"]))
    t0 = time.time()
    f.pop("harmonic_modes", None)
    f.update(resonance(work, Af, free, Fac(Af), Fac, G, K0f, M0f, f["k0_sq"], n_modes, n_extra))
    f.setdefault("times_s", {})["modes"] = round(time.time() - t0, 2)
    return f


def s_features(S: sp.spmatrix, Fac, backend: str, work: Path, real_python: Path) -> dict:
    """inertia_S, S_lambda_max, S_lambda_min. S >= 0 (passive) is decided
    exactly by the inertia; lambda_min(S) then by shift-invert just below 0,
    otherwise (PML) below the Gershgorin bound. S = 0 (lossless closed): trivial."""
    S = S.tocsr()
    S.eliminate_zeros()
    if S.nnz == 0:
        return dict(inertia_S=dict(neg=0, zero=S.shape[0], pos=0, diagonal_pivots=True),
                    S_lambda_max=0.0, S_lambda_min=0.0)
    ine = inertia(S, backend, work, real_python)
    smax = lam_ext(S, "LA")
    smin = lam_min(S, Fac, -1e-10 * smax) if ine["neg"] == 0 else lam_min(S, Fac, None, 2000)
    return dict(inertia_S=ine, S_lambda_max=smax, S_lambda_min=smin)


def patch_s(path: Path, work: Path, backend: str, real_python: Path) -> dict:
    """inertia_S and S_lambda_min (as features()) into an existing result."""
    f = json.loads(path.read_text(encoding="utf-8"))
    A = load_bin(work / "A.bin")
    free = np.abs(A.diagonal()) < PENALTY
    S = A[free][:, free].imag.tocsr()
    f.update(s_features(S, Mumps if backend == "mumps" else SuperLU, backend, work, real_python))
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sets", default="", help="parameter sets (P05-1) or cases (case2A:standard), comma separated")
    ap.add_argument("--out", type=Path, default=rpb.ROOT / "results" / "pcb_features")
    ap.add_argument("--scratch", type=Path, default=Path("/tmp/emag_pcb_features"))
    ap.add_argument("--freefem-bin", default="FreeFem++-mpi")
    ap.add_argument("--backend", choices=["superlu", "mumps"], default="superlu")
    ap.add_argument("--real-python", type=Path, default=REAL_PYTHON,
                    help="interpreter with petsc4py on FreeFEM's real PETSc (inertia, --backend mumps)")
    ap.add_argument("--n-sv", type=int, default=10, help="smallest singular values / eigenvalues near 0")
    ap.add_argument("--fov", type=int, default=0, metavar="N",
                    help="field of values: scan N angles (slow; 0 = off, lambda_min(S) is the theta = 90 deg value)")
    ap.add_argument("--patch-s", action="store_true",
                    help="only add inertia_S / S_lambda_min to existing results (made before they existed)")
    ap.add_argument("--patch-modes", action="store_true",
                    help="only recompute the resonance part of existing results")
    ap.add_argument("--open-modes", action="store_true",
                    help="also search the resonance modes of open cases (Silver-Mueller / UPML; slow, "
                         "not robust, not tabulated; skipped by default since 2026-10-13)")
    ap.add_argument("--keep", action="store_true", help="keep the exported matrices in the scratch directory")
    ap.add_argument("--inertia-of", type=Path, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.inertia_of:
        print("INERTIA " + json.dumps(inertia_mumps_real(a.inertia_of)))
        return 0
    outdir = a.out / rpb.HOST.name
    outdir.mkdir(parents=True, exist_ok=True)
    status = 0
    for pset in [s for s in a.sets.split(",") if s]:
        t0 = time.time()
        try:
            work = export(pset, a.scratch, a.freefem_bin)
            t_export = round(time.time() - t0, 1)
            if a.patch_modes:
                f = patch_modes(outdir / f"{pset.replace(':', '_')}.json", work, a.backend)
                (outdir / f"{pset.replace(':', '_')}.json").write_text(json.dumps(f, indent=1), encoding="utf-8")
                print(f"PATCHED-MODES {pset} reldist={f['resonance_reldist']}", flush=True)
                continue
            if a.patch_s:
                f = patch_s(outdir / f"{pset.replace(':', '_')}.json", work, a.backend, a.real_python)
                (outdir / f"{pset.replace(':', '_')}.json").write_text(json.dumps(f, indent=1), encoding="utf-8")
                print(f"PATCHED {pset}", flush=True)
                continue
            f = features(work, a.n_sv, a.fov, a.backend, a.real_python, open_modes=a.open_modes)
        except Exception as e:   # one failing set does not stop the others
            print(f"FAILED {pset}: {type(e).__name__}: {e}", flush=True)
            status = 1
            continue
        f = dict(set=pset, host=rpb.HOST.name, wall_s=round(time.time() - t0, 1), export_s=t_export, **f)
        (outdir / f"{pset.replace(':', '_')}.json").write_text(json.dumps(f, indent=1), encoding="utf-8")
        print(f"DONE {pset} n={f['n']} wall={f['wall_s']}s", flush=True)
        if not a.keep:
            for p in work.glob("*.bin"):
                p.unlink()
    return status


if __name__ == "__main__":
    sys.exit(main())
